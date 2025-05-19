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

# Uygulama başlatıldığında verileri yükle
questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()


class QuestionRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    user_input: str
    answer: str
    satisfied: bool
    original_question: str


@app.post("/ask")
def ask_question(request: QuestionRequest):
    global questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model

    user_input = request.question.strip()
    if not is_technical_question(user_input, model, faiss_index, embedding_matrix, questions):
        return {"message": "Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun."}

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
        questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()
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
    global questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model

    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz!"}

    preprocessed = preprocess_text(request.user_input)
    best_index, _, top_question = get_best_match(preprocessed, model, faiss_index, embedding_matrix, questions)

    # Alternatif cevap veritabanında varsa onu döndür
    alt_answer = alt_answers[best_index]
    if alt_answer:
        return {
            "message": "Alternatif açıklama sunuldu.",
            "alternative_answer": alt_answer
        }

    # Yoksa OpenAI'den üret
    alt_answer = get_openai_response("Bu soruyu farklı bir şekilde açıkla: " + request.user_input)
    updated = update_alternative_answer_in_airtable(top_question, alt_answer)

    if updated:
        questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()
    else:
        return {"message": "Alternatif açıklama oluşturulamadı."}

    # Alternatif açıklama da yeterli değilse öğretmene mail gönder
    send_email_to_teacher(
        subject="Öğrenci Anlamadı - Müdahale Gerekli",
        body=f"Soru: {request.user_input}\n\n"
             f"İlk Cevap: {request.answer}\n\n"
             f"Alternatif Açıklama: {alt_answer}"
    )

    return {
        "message": "Alternatif açıklama üretildi ve eğitmene iletildi.",
        "alternative_answer": alt_answer
    }
