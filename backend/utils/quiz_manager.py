import random
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# -------------------------
#  NORMALIZE & CLEAN HELPERS
# -------------------------

def normalize_text(text: str):
    if not isinstance(text, str):
        return ""
    return " ".join(text.replace("\n", " ").split())   # newline → space, extra spaces remove


def clean_option(text: str, max_len=150):
    text = normalize_text(text)
    return text if len(text) <= max_len else text[:max_len] + "..."


# -------------------------
#  SIMILARITY CHECK
# -------------------------

def is_too_similar(correct_answer, wrong_answer, model, threshold=0.50):
    """
    Yanlış şık doğru cevaba çok benzerse eler.
    """
    try:
        emb_correct = np.array(model.encode(correct_answer)).reshape(1, -1)
        emb_wrong = np.array(model.encode(wrong_answer)).reshape(1, -1)
        sim = cosine_similarity(emb_correct, emb_wrong)[0][0]
        return sim >= threshold
    except:
        return False


# -------------------------
#  QUIZ SYSTEM
# -------------------------

def start_quiz(question_list, model, chroma_collection, num_questions=3):
    print("\n🎯 Sohbet bazlı quiz başlıyor!")

    if len(question_list) == 0:
        print("Sohbetten quiz oluşturmak için yeterli veri yok.")
        return

    # Quiz sorularını seç
    selected_questions = random.sample(question_list, min(num_questions, len(question_list)))

    total = 0
    correct = 0

    for q in selected_questions:

        # -----------------------------------------
        # 1) EN YAKIN SORU VE DOĞRU CEVABI BUL
        # -----------------------------------------
        q_emb = model.encode(q).tolist()

        result_correct = chroma_collection.query(
            query_embeddings=[q_emb],
            n_results=1,
            include=["documents", "metadatas"]
        )

        if not result_correct["documents"]:
            print(f"Soru için veri bulunamadı: {q}")
            continue

        correct_question = normalize_text(result_correct["documents"][0][0])
        correct_answer = normalize_text(result_correct["metadatas"][0][0]["answer"])
        correct_answer = clean_option(correct_answer)

        # -----------------------------------------
        # 2) YANLIŞ ŞIKLARI GETİR
        # -----------------------------------------
        result_wrong = chroma_collection.query(
            query_embeddings=[q_emb],
            n_results=6,   # 1 doğru + 5 aday
            include=["metadatas"]
        )

        wrong_answers = []

        for item in result_wrong["metadatas"][0][1:]:  # ilk eleman doğru cevap
            candidate = normalize_text(item["answer"])
            candidate = clean_option(candidate)

            if candidate == correct_answer:
                continue

            if is_too_similar(correct_answer, candidate, model):
                continue

            wrong_answers.append(candidate)
            if len(wrong_answers) == 3:
                break

        # Yanlış şıklar eksikse doldur
        while len(wrong_answers) < 3:
            wrong_answers.append("Diğer")

        # -----------------------------------------
        # 3) ŞIKLARI HAZIRLA
        # -----------------------------------------
        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        print(f"\n❓ {correct_question}")
        for i, opt in enumerate(options):
            print(f"{i + 1}. {opt}")

        # -----------------------------------------
        # 4) KULLANICI CEVABI
        # -----------------------------------------
        choice = input("Cevap numarası: ").strip()

        total += 1
        if choice.isdigit() and 1 <= int(choice) <= 4:
            if options[int(choice) - 1] == correct_answer:
                print("✅ Doğru!")
                correct += 1
            else:
                print(f"❌ Yanlış. Doğru cevap: {correct_answer}")
        else:
            print(f"⚠️ Geçersiz giriş. Doğru cevap: {correct_answer}")

    print(f"\n🏁 Quiz Bitti! Doğru sayısı: {correct}/{total}")
