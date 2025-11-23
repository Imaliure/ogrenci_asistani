from fastapi import FastAPI
from pydantic import BaseModel
from services.gemini_service import get_gemini_response
from services.chroma_service import (
    load_data_from_chroma,
    save_to_chroma,
    save_alternative_answer,
    get_alternative_answer,
    model,
    collection
)
from utils.preprocessing import preprocess_text
from utils.chroma_helper import get_best_match
from utils.question_classifier import is_technical_question
from utils.email_helper import send_email_to_teacher
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# CORS EKLENDİ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# Veri modelleri
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
    questions: list[str]
    num_questions: int = 3


@app.post("/ask")
def ask_question(request: QuestionRequest):
    user_input = request.question.strip()

    # Tüm DB verilerini çek
    questions, embeddings, answers = load_data_from_chroma()

    # Teknik değilse
    if not is_technical_question(user_input, model, collection, questions, embeddings):
        return {"answer": "Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun."}

    # Embedding için temiz hali
    preprocessed = preprocess_text(user_input)

    # En yakın DB kaydını bul
    best_index, best_score, top_question = get_best_match(
        preprocessed, model, collection, questions, embeddings
    )

    # --- 1) Kayıt Yeterli (0.75 ve üzeri) ---
    if best_score >= 0.75:
        answer = answers[best_index]
        return {
            "top_question": top_question,
            "similarity": float(best_score),
            "answer": answer,
            "source": "database"
        }

    # --- 2) Çok benzer fakat içerik aynıysa DB'ye kaydetme ---
    if top_question and top_question.strip().lower() == preprocessed.strip().lower():
        return {
            "top_question": top_question,
            "similarity": float(best_score),
            "message": "Bu soru zaten veritabanında var."
        }

    # --- 3) Yetersiz benzerlik → Gemini cevabı ---
    answer = get_gemini_response(user_input)

    # DB’ye kaydet (orijinal hali + processed embedding)
    save_to_chroma(user_input, answer)

    return {
        "top_question": top_question,
        "similarity": float(best_score),
        "answer": answer,
        "source": "gemini"
    }

@app.post("/feedback")
def feedback(request: FeedbackRequest):
    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz."}

    questions, embeddings, answers = load_data_from_chroma()
    preprocessed = preprocess_text(request.user_input)

    best_index, _, top_question = get_best_match(
        preprocessed, model, collection, questions, embeddings
    )

    alt_answer = get_alternative_answer(top_question)
    if alt_answer:
        return {
            "message": "Alternatif açıklama sunuldu.",
            "alternative_answer": alt_answer
        }

    alt_answer = get_gemini_response(
        "Bu soruyu daha anlaşılır şekilde açıkla: " + request.user_input
    )
    save_alternative_answer(top_question, alt_answer)

    return {
        "message": "Alternatif açıklama oluşturuldu.",
        "alternative_answer": alt_answer
    }


@app.post("/feedback2")
def feedback2(request: FeedbackRequest):
    if request.satisfied:
        return {"message": "Geri bildiriminiz için teşekkür ederiz."}

    message = (
        f"Soru: {request.user_input}\n\n"
        f"İlk Cevap: {request.answer}\n\n"
        f"Alternatif Açıklama: {request.alt_answer}\n\n"
    )

    if request.user_message:
        message += f"Kullanıcı Mesajı:\n{request.user_message}\n"

    send_email_to_teacher(
        subject="🛑 Öğrenci Anlamadı - Müdahale Gerekli",
        body=message
    )

    return {"message": "Eğitmene bilgilendirme gönderildi."}

@app.post("/quiz")
def generate_quiz(request: QuizRequest):
    questions_input = request.questions
    num = request.num_questions

    # Veritabanı yükle
    questions, embeddings, answers = load_data_from_chroma()

    quiz_list = []

    import random
    from utils.quiz_manager import is_too_similar

    # Rastgele sorular seç
    selected = random.sample(questions_input, min(num, len(questions_input)))

    for q in selected:
        processed = preprocess_text(q)
        q_emb = model.encode(processed).tolist()

        result = collection.query(
            query_embeddings=[q_emb],
            n_results=5,
            include=["documents", "metadatas"]
        )

        # En yakın kayıt (doğru cevap)
        correct_question = result["documents"][0][0]
        correct_answer = result["metadatas"][0][0]["answer"]

        # Diğer cevaplardan yanlış şıklar
        wrong_answers = []
        for item in result["metadatas"][0][1:]:
            cand = item["answer"]
            if is_too_similar(correct_answer, cand, model):
                continue
            wrong_answers.append(cand)
            if len(wrong_answers) == 3:
                break

        while len(wrong_answers) < 3:
            wrong_answers.append("Diğer")

        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        quiz_list.append({
            "question": correct_question,
            "options": options,
            "correct_index": options.index(correct_answer)
        })

    return {"quiz": quiz_list}
