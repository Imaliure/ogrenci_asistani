import os
import uuid
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import torch


client = PersistentClient(path="chroma_db")

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
    embedding = model.encode(question).tolist()
    uid = str(uuid.uuid4())

    collection.add(
        ids=[uid],
        documents=[question],
        embeddings=[embedding],
        metadatas=[{"answer": answer}]
    )


def save_alternative_answer(question_text, alternative_answer):
    uid = str(uuid.uuid4())
    alt_collection.add(
        ids=[uid],
        documents=[question_text],
        metadatas=[{"alt_answer": alternative_answer}]
    )


def get_alternative_answer(question_text):
    results = alt_collection.get(include=["documents", "metadatas"])

    for doc, meta in zip(results['documents'], results['metadatas']):
        if doc.strip().lower() == question_text.strip().lower():
            return meta.get('alt_answer')
    return None
