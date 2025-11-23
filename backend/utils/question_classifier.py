## utils/question_classifier.py
from utils.preprocessing import preprocess_text, get_keyword_match_score
from utils.chroma_helper import get_best_match


def is_technical_question(user_input, model, chroma_collection, questions, embeddings, keyword_threshold=0.5, embedding_threshold=0.5):
    keyword_score = get_keyword_match_score(user_input)
    print(f"Anahtar kelime skoru: {keyword_score:.4f}")

    if keyword_score >= keyword_threshold:
        return True
    else:
        preprocessed = preprocess_text(user_input)
        _, embedding_score, _ = get_best_match(preprocessed, model, chroma_collection, questions, embeddings)
        return embedding_score >= embedding_threshold
