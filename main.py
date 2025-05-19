from utils.preprocessing import preprocess_text
from utils.faiss_helper import get_best_match
from services.openai_service import get_openai_response
from services.airtable_service import load_data_from_airtable, save_to_airtable, update_alternative_answer_in_airtable
from utils.email_helper import send_email_to_teacher
from utils.question_classifier import is_technical_question


def main():
    print("AI Asistan başlatılıyor...")

    questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()

    while True:
        user_input = input("Lütfen sorunuzu yazınız (Çıkmak için 'q'): ").strip()
        if user_input.lower() == 'q':
            break

        if not is_technical_question(user_input, model, faiss_index, embedding_matrix, questions):
            print("Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun.")
            continue

        preprocessed = preprocess_text(user_input)
        best_index, best_score, top_question = get_best_match(preprocessed, model, faiss_index, embedding_matrix, questions)

        print(f"\nEn yakın soru: {top_question} (Benzerlik: {best_score:.4f})")

        if best_score >= 0.75:
            answer = answers[best_index]
            print(f"Cevap: {answer}")
        elif best_score >= 0.4:
            if top_question.strip().lower() != preprocessed.strip().lower():
                print("OpenAI'den cevap alınıyor...")
                answer = get_openai_response(user_input)
                print(f"OpenAI Cevabı: {answer}")
                save_to_airtable(preprocessed, answer, model)
                questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()
            else:
                print("Benzer soru zaten veritabanında var. Cevap verilemedi.")
                continue
        else:
            print("Soruya benzer bir kayıt bulunamadı. OpenAI'den cevap alınıyor...")
            answer = get_openai_response(user_input)
            print(f"OpenAI Cevabı: {answer}")

        feedback = input("\nBu cevaptan memnun kaldınız mı? (e/h): ").strip().lower()

        if feedback == "h":
            alt_answer = alt_answers[best_index]
            if alt_answer:
                print("\nAlternatif Açıklama Mevcut:")
                print(f"Alternatif Açıklama: {alt_answer}")
            else:
                print("\nAlternatif açıklama hazırlanıyor...")
                alt_answer = get_openai_response("Bu soruyu farklı bir şekilde açıkla: " + user_input)
                print(f"Alternatif Açıklama: {alt_answer}")

                updated = update_alternative_answer_in_airtable(top_question, alt_answer)
                if updated:
                    print("Alternatif açıklama Airtable'a başarıyla kaydedildi.")
                    questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model = load_data_from_airtable()
                else:
                    print("Alternatif açıklama kaydedilemedi.")

            second_feedback = input("\nBu açıklama daha açıklayıcı oldu mu? (e/h): ").strip().lower()
            if second_feedback == "h":
                send_email_to_teacher(
                    subject="Öğrenci Anlamadı - Müdahale Gerekli",
                    body=(
                        f"Soru: {user_input}\n\n"
                        f"İlk Cevap: {answer}\n\n"
                        f"Alternatif Açıklama: {alt_answer}"
                    )
                )
                print("Durum eğitmene iletildi. En kısa sürede geri dönüş yapılacaktır.")


if __name__ == "__main__":
    main()
