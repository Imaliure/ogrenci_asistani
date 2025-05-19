import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.special import softmax

def get_best_match(preprocessed_question, model, faiss_index, embedding_matrix, questions):
    query_vector = model.encode([preprocessed_question]).astype('float32')
    D, I = faiss_index.search(query_vector, k=5)

    similarities = cosine_similarity(query_vector, embedding_matrix[I[0]])[0]
    soft_scores = softmax(similarities)

    best_local_idx = soft_scores.argmax()
    best_index = I[0][best_local_idx]
    best_score = similarities[best_local_idx]
    return best_index, best_score, questions[best_index]
