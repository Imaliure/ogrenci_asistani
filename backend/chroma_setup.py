# backend/chroma_setup.py
import json
import uuid
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer


# ✅ Model ve ChromaDB başlat
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
client = PersistentClient(path="../data/chroma_db")

# ✅ Koleksiyonları oluştur
questions_collection = client.get_or_create_collection("questions")
keywords_collection = client.get_or_create_collection("ml_keywords")

# ✅ JSON'u yükle
with open("./data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# ✅ Sütun verilerini çek
ticket_ids = data["Ticket ID"]
titles = data["Soru Başlığı"]
questions = data["Sorular"]
answers = data["Cevaplar"]
keywords_list = data["Keywords"]

# ✅ Her satır için işle
for i in range(len(ticket_ids)):
    ticket_id = ticket_ids[i]
    soru = questions[i]
    cevap = answers[i]
    soru_basligi = titles[i]
    keywords = keywords_list[i] if isinstance(keywords_list[i], list) else []

    # 🚀 Soru embedding ve kaydetme
    soru_embedding = model.encode(soru).tolist()
    uid = str(uuid.uuid4())

    questions_collection.add(
        ids=[uid],
        documents=[soru],
        embeddings=[soru_embedding],
        metadatas=[{
            "ticket_id": ticket_id,
            "title": soru_basligi,
            "answer": cevap
        }]
    )

    # 🚀 Keywords embedding ve kaydetme
    for keyword in keywords:
        keyword_embedding = model.encode(keyword).tolist()
        kid = str(uuid.uuid4())

        keywords_collection.add(
            ids=[kid],
            documents=[keyword],
            embeddings=[keyword_embedding],
            metadatas=[{"source": "keyword"}]
        )

print("✅ Tüm veriler başarıyla ChromaDB'ye yüklendi.")
