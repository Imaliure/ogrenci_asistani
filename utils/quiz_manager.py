import random

def start_quiz(question_list, model, chroma_collection, num_questions=3):
    print("\n🎯 Sohbet bazlı quiz başlıyor!")

    if len(question_list) == 0:
        print("Sohbetten quiz oluşturmak için yeterli veri yok.")
        return

    selected_questions = random.sample(question_list, min(num_questions, len(question_list)))

    total = 0
    correct = 0

    for q in selected_questions:
        query_emb = model.encode(q).tolist()

        results = chroma_collection.query(
            query_embeddings=[query_emb],
            n_results=5,
            include=["documents", "metadatas"]
        )

        if not results.get("documents") or len(results["documents"][0]) == 0:
            print(f"Soru için yeterli veri yok: {q}")
            continue

        correct_question = results["documents"][0][0]
        correct_answer = results["metadatas"][0][0]["answer"]

        wrong_answers = []
        for item in results["metadatas"][0][1:]:
            wrong_answers.append(item["answer"])
            if len(wrong_answers) >= 3:
                break

        while len(wrong_answers) < 3:
            wrong_answers.append("Diğer")

        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        print(f"\n❓ {correct_question}")
        for i, opt in enumerate(options):
            print(f"{i + 1}. {opt}")

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
