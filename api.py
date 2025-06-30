from fastapi import FastAPI
from pydantic import BaseModel
from services.openai_service import get_openai_response
from services.chroma_service import (
    load_data_from_chroma,
    save_to_chroma,
    update_alternative_answer_in_chroma
)
from utils.preprocessing import preprocess_text
from utils.chroma_helper import get_best_match
from utils.question_classifier import is_technical_question
from utils.email_helper import send_email_to_teacher

app = FastAPI()

# --- Veri modelleri ---
class QuestionRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    user_input: str
    answer: str
    satisfied: bool
    original_question: str
    alt_answer: str | None = None
    user_message: str | None = None


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 3


# --- /ask endpoint ---
@app.post("/ask")
def ask_question(request: QuestionRequest):
    user_input = request.question.strip()

    questions, embeddings, answers, alt_answers, collection, model = load_data_from_chroma()

    if not is_technical_question(user_input, model, collection, questions, embeddings):
        return {"answer": "Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun."}

    preprocessed = preprocess_text(user_input)
    best_index, best_score, top_question = get_best_match(preprocessed, model, collection, questions, embeddings)

    if best_score >= 0.75:
        answer = answers[best_index]
        return {
            "top_question": top_question,
            "similarity": float(best_score),
            "answer": answer,
            "source": "database"
        }

    elif best_score >= 0.4 and top_question.strip().lower() != preprocessed.strip().lower():
        answer = get_openai_response(user_input)
        save_to_chroma(preprocessed, answer, model)
        return {
            "top_question": top_question,
            "similarity": float(best_score),
            "answer": answer,
            "source": "openai"
        }

    elif best_score >= 0.4:
        return {
            "top_question": top_question,
            "similarity": float(best_score),
            "message": "Benzer soru zaten veritabanında var. Cevap verilemedi."
        }

    else:
        answer = get_openai_response(user_input)
        return {
            "top_question": None,
            "similarity": float(best_score),
            "answer": answer,
            "source": "openai"
        }


# --- /feedback endpoint ---
@app.post("/feedback")
def feedback(request: FeedbackRequest):
    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz!"}

    questions, embeddings, answers, alt_answers, collection, model = load_data_from_chroma()

    preprocessed = preprocess_text(request.user_input)
    best_index, _, top_question = get_best_match(preprocessed, model, collection, questions, embeddings)

    alt_answer = alt_answers[best_index]
    if alt_answer:
        return {
            "message": "Alternatif açıklama sunuldu.",
            "alternative_answer": alt_answer
        }

    alt_answer = get_openai_response("Bu soruyu farklı bir şekilde açıkla: " + request.user_input)
    updated = update_alternative_answer_in_chroma(top_question, alt_answer)

    if updated:
        return {"message": "Alternatif açıklama oluşturuldu.", "alternative_answer": alt_answer}
    else:
        return {"message": "Alternatif açıklama oluşturulamadı."}


# --- /feedback2 -> Eğitmene mesaj iletme ---
@app.post("/feedback2")
def feedback2(request: FeedbackRequest):
    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz!"}

    message = (
        f"Kullanıcı şu soruyu anlamadı:\n{request.user_input}\n\n"
        f"İlk Cevap:\n{request.answer}\n\n"
        f"Alternatif Açıklama:\n{request.alt_answer}\n\n"
    )

    if request.user_message:
        message += f"Kullanıcı Mesajı:\n{request.user_message}\n"

    send_email_to_teacher(
        subject="Alternatif Açıklama da Yetersiz - Acil Müdahale Gerekli",
        body=message
    )

    return {"message": "Eğitmene bilgilendirme gönderildi."}


# --- /quiz endpoint ---
@app.post("/quiz")
def quiz(request: QuizRequest):
    questions, embeddings, _, _, collection, model = load_data_from_chroma()

    preprocessed_topic = preprocess_text(request.topic)

    # İlgili konuyla en alakalı soruları seç
    scores_list = []
    for idx, question in enumerate(questions):
        _, score, _ = get_best_match(preprocessed_topic, model, collection, [question], [embeddings[idx]])
        scores_list.append((idx, score))

    # Skorları sırala
    scores_list = sorted(scores_list, key=lambda x: x[1], reverse=True)
    top_questions = scores_list[:request.num_questions]

    quiz_questions = []
    for idx, score in top_questions:
        quiz_questions.append({
            "question": questions[idx],
            "similarity": float(score)
        })

    if not quiz_questions:
        return {"message": "Bu konuyla ilgili yeterli soru bulunamadı."}

    return {
        "quiz_topic": request.topic,
        "quiz_questions": quiz_questions
    }
