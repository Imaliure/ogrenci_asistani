from utils.preprocessing import preprocess_text
from utils.chroma_helper import get_best_match
from services.openai_service import get_openai_response
from services.chroma_service import (
    load_data_from_chroma,
    save_to_chroma,
    save_alternative_answer,
    get_alternative_answer
)
from utils.email_helper import send_email_to_teacher
from utils.question_classifier import is_technical_question
from services.chroma_service import model, collection
from utils.quiz_manager import start_quiz


def main():
    print("AI Asistan başlatılıyor...")

    questions, embeddings, answers = load_data_from_chroma()
    session_questions = []  # Sohbet boyunca teknik sorular
    while True:
        user_input = input("Lütfen sorunuzu yazınız (Çıkmak için 'q'): ").strip()
        if user_input.lower() == 'q':
            break

        if user_input.lower() == "quiz":
            start_quiz(session_questions, model, collection)
            continue

        if not is_technical_question(user_input, model, collection, questions, embeddings):
            print("Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun.")
            continue
        
        session_questions.append(user_input)
    
        preprocessed = preprocess_text(user_input)
        best_index, best_score, top_question = get_best_match(preprocessed, model, collection, questions, embeddings)

        print(f"\nEn yakın soru: {top_question} (Benzerlik: {best_score:.4f})")

        if best_score >= 0.75:
            answer = answers[best_index]
            print(f"Cevap: {answer}")
        elif best_score >= 0.4:
            if top_question.strip().lower() != preprocessed.strip().lower():
                print("OpenAI'den cevap alınıyor...")
                answer = get_openai_response(user_input)
                print(f"OpenAI Cevabı: {answer}")
                save_to_chroma(preprocessed, answer)
                questions, embeddings, answers = load_data_from_chroma()
            else:
                print("Benzer soru zaten veritabanında var. Cevap verilemedi.")
                continue
        else:
            print("Soruya benzer bir kayıt bulunamadı. OpenAI'den cevap alınıyor...")
            answer = get_openai_response(user_input)
            print(f"OpenAI Cevabı: {answer}")
            save_to_chroma(preprocessed, answer)
            questions, embeddings, answers = load_data_from_chroma()


        feedback = input("\nBu cevaptan memnun kaldınız mı? (e/h): ").strip().lower()

        if feedback == "h":
            alt_answer = get_alternative_answer(top_question)
            if alt_answer:
                print("\nAlternatif Açıklama Mevcut:")
                print(f"Alternatif Açıklama: {alt_answer}")
            else:
                print("\nAlternatif açıklama hazırlanıyor...")
                alt_answer = get_openai_response("Bu soruyu farklı bir şekilde açıkla: " + user_input)
                print(f"Alternatif Açıklama: {alt_answer}")

                save_alternative_answer(top_question, alt_answer)
                questions, embeddings, answers = load_data_from_chroma()

            second_feedback = input("\nBu açıklama daha açıklayıcı oldu mu? (e/h): ").strip().lower()
            if second_feedback == "h":
                student_note = input("\nEğitmene iletmek istediğiniz özel bir not var mı? (Boş bırakabilirsiniz): ").strip()

                send_email_to_teacher(
                    subject="🛑 Öğrenci Anlamadı - Müdahale Gerekli",
                    body=(
                        f"Soru: {user_input}\n\n"
                        f"İlk Cevap: {answer}\n\n"
                        f"Alternatif Açıklama: {alt_answer}"
                    ),
                    student_message=student_note
                )
                print("Durum eğitmene iletildi. En kısa sürede geri dönüş yapılacaktır.")

        if len(session_questions) > 0 and len(session_questions) % 3 == 0:
            quiz_choice = input("\nBu zamana kadar öğrendiğiniz konulardan quiz yapmak ister misiniz? (e/h): ").strip().lower()
            if quiz_choice == "e":
                start_quiz(session_questions, model, collection)


if __name__ == "__main__":
    main()
