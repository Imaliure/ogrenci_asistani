import os
import json
import numpy as np
from pyairtable import Table
from sentence_transformers import SentenceTransformer
import faiss
from dotenv import load_dotenv

load_dotenv()

def load_data_from_airtable():
    table = Table(os.getenv("AIRTABLE_API_KEY"), os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_NAME"))
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    records = table.all(fields=["Soru", "Embedding", "Cevap", "AlternatifCevap"])
    questions, embeddings, answers, alt_answers = [], [], [], []

    for record in records:
        fields = record["fields"]
        questions.append(fields["Soru"])
        embeddings.append(np.array(json.loads(fields["Embedding"])))
        answers.append(fields.get("Cevap", ""))
        alt_answers.append(fields.get("AlternatifCevap", ""))
    
    embedding_matrix = np.vstack(embeddings).astype('float32')
    faiss_index = faiss.IndexFlatL2(len(embeddings[0]))
    faiss_index.add(embedding_matrix)

    return questions, embeddings, answers, alt_answers, faiss_index, embedding_matrix, model


def save_to_airtable(question, answer, model):
    table = Table(os.getenv("AIRTABLE_API_KEY"), os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_NAME"))
    embedding = model.encode([question]).tolist()
    table.create({
        "Soru": question,
        "Cevap": answer,
        "Embedding": json.dumps(embedding)
    })


def update_alternative_answer_in_airtable(question_text, alternative_answer):
    table = Table(os.getenv("AIRTABLE_API_KEY"), os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_NAME"))
    records = table.all(fields=["Soru"])
    record_id = None

    for record in records:
        if record["fields"]["Soru"].strip().lower() == question_text.strip().lower():
            record_id = record["id"]
            break

    if record_id:
        table.update(record_id, {"AlternatifCevap": alternative_answer})
        return True
    return False
