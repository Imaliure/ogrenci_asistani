from fastapi import FastAPI
from pydantic import BaseModel
from services.openai_service import get_openai_response
from services.airtable_service import (
    load_data_from_airtable,
    save_to_airtable,
    update_alternative_answer_in_airtable
)
from utils.preprocessing import preprocess_text
from utils.faiss_helper import get_best_match
from utils.question_classifier import is_technical_question
from utils.email_helper import send_email_to_teacher

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    user_input: str
    answer: str
    satisfied: bool
    original_question: str
    alt_answer: str | None = None


@app.post("/ask")
def ask_question(request: QuestionRequest):
    user_input = request.question.strip()
    
    # Verileri sadece ihtiyaç anında yükle
    questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()

    if not is_technical_question(user_input, model, faiss_index, embedding_matrix, questions):
        return {"answer": "Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun."}

    preprocessed = preprocess_text(user_input)
    best_index, best_score, top_question = get_best_match(preprocessed, model, faiss_index, embedding_matrix, questions)

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
        save_to_airtable(preprocessed, answer, model)
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


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz!"}

    questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()

    preprocessed = preprocess_text(request.user_input)
    best_index, _, top_question = get_best_match(preprocessed, model, faiss_index, embedding_matrix, questions)

    alt_answer = alt_answers[best_index]
    if alt_answer:
        return {
            "message": "Alternatif açıklama sunuldu.",
            "alternative_answer": alt_answer
        }

    alt_answer = get_openai_response("Bu soruyu farklı bir şekilde açıkla: " + request.user_input)
    updated = update_alternative_answer_in_airtable(top_question, alt_answer)

    if updated:
        return {"message": "Alternatif açıklama oluşturuldu.", "alternative_answer": alt_answer}
    else:
        return {"message": "Alternatif açıklama oluşturulamadı."}


@app.post("/feedback2")
def feedback2(request: FeedbackRequest):
    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz!"}

    send_email_to_teacher(
        subject="Alternatif Açıklama da Yetersiz - Acil Müdahale Gerekli",
        body=f"Kullanıcı şu soruyu anlamadı: {request.user_input}\n\n"
             f"ilk Cevap: {request.answer}\n\nAlternatif Açıklama: {request.alt_answer}"
    )

    return {"message": "Alternatif açıklama da yeterli olmadı. Eğitmen bilgilendirildi."}
