# services/chroma_service.py
import os
import uuid
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import torch
from chromadb.config import Settings
from utils.preprocessing import preprocess_text

client = PersistentClient(path="chroma_db",settings=Settings(anonymized_telemetry=False))

collection = client.get_or_create_collection("questions")
alt_collection = client.get_or_create_collection("alternative_answers")

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def load_data_from_chroma():
    results = collection.get(include=["embeddings", "metadatas", "documents"])
    questions = results['documents']
    answers = [m['answer'] for m in results['metadatas']]
    embeddings = results['embeddings']
    return questions, embeddings, answers

def save_to_chroma(question, answer):
    uid = str(uuid.uuid4())
    processed = preprocess_text(question)
    embedding = model.encode(processed).tolist()

    collection.add(
        ids=[uid],
        documents=[question],
        embeddings=[embedding],
        metadatas=[{
            "question": question,
            "answer": answer,
            "title": question[:40],
            "ticket_id": uid[:8]
        }]
    )

def save_alternative_answer(question_text, alternative_answer):
    uid = str(uuid.uuid4())
    alt_collection.add(
        ids=[uid],
        documents=[question_text],
        metadatas=[{
            "question": question_text,
            "alt_answer": alternative_answer
        }]
    )

def get_alternative_answer(question_text):
    results = alt_collection.get(include=["documents", "metadatas"])

    for doc, meta in zip(results['documents'], results['metadatas']):
        if doc.strip().lower() == question_text.strip().lower():
            return meta.get('alt_answer')
    return None
