## utils/chroma_helper.py
import torch
from sentence_transformers.util import cos_sim


def get_best_match(preprocessed_question, model, chroma_collection, questions, embeddings):
    query_emb = torch.tensor(model.encode(preprocessed_question), dtype=torch.float32).unsqueeze(0)

    best_score = -1
    best_index = -1

    for idx, emb in enumerate(embeddings):
        emb_tensor = torch.tensor(emb, dtype=torch.float32).unsqueeze(0)

        score = cos_sim(query_emb, emb_tensor).item()

        if score > best_score:
            best_score = score
            best_index = idx

    best_question = questions[best_index] if best_index != -1 else None

    return best_index, best_score, best_question
