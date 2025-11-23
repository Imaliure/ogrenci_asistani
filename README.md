# 🎓 AI Öğrenci Asistanı – Kurulum & Çalıştırma Rehberi

AI Öğrenci Asistanı; teknik soruları yanıtlayan, gerekirse Gemini kullanarak açıklama oluşturan, cevaplardan memnun kalınmadığında alternatif açıklamalar sağlayan ve 3 soruda bir otomatik quiz oluşturan bir yapay zeka destekli eğitim asistanıdır.

Bu doküman, projeyi **cloneladıktan sonra nasıl çalıştıracağınızı** eksiksiz şekilde anlatır.

---

# 📁 1. Proje Klasör Yapısı

Proje aşağıdaki şekilde organize edilmiştir:

```
ogrenci_asistani/
│
├── backend/
│   ├── api.py
│   ├── main.py
│   ├── chroma_setup.py
│   ├── requirements.txt
│   ├── services/
│   ├── utils/
│   ├── .env
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│
├── data/
│   └── chroma_db/   ← ChromaDB kalıcı veritabanı
```

---

# 🚀 2. Backend Kurulumu

### ✅ Adım 1 — Backend klasörüne gir
```bash
cd backend
```

### ✅ Adım 2 — Sanal ortam oluştur
```bash
python -m venv venv
```

### ✅ Adım 3 — Ortamı aktifleştir

Windows:
```bash
venv\Scripts\activate
```

Mac / Linux:
```bash
source venv/bin/activate
```

### ✅ Adım 4 — Gerekli kütüphaneleri kur
```bash
pip install -r requirements.txt
```

---

# 🧠 3. ChromaDB Veritabanını Hazırla

Başlangıç verilerinin yüklenmesi için:

```bash
python chroma_setup.py
```

Bu işlem **data.json** içindeki tüm soru/cevapları embedding’leriyle birlikte **ChromaDB’ye ekler**.

---

# 🏃‍♂️ 4. Backend’i Çalıştır

```bash
uvicorn api:app --reload --port 8000
```

Backend artık şu adreste çalışır:

👉 http://127.0.0.1:8000

---

# 🌐 5. Frontend’i Çalıştır

Frontend statik HTML/JS olduğu için bir yerel server ile çalıştırmanız gerekir.

### VSCode Live Server:
- index.html → sağ tık → **Open with Live Server**

### Python ile:
```bash
cd frontend
python -m http.server 5500
```

Frontend artık şu adreste açık olur:

👉 http://127.0.0.1:5500  
veya  
👉 Live Server kullanıyorsan otomatik açılır.

---
🎯 6. Sistem Nasıl Çalışır?

- Kullanıcı bir soru gönderdiğinde sistem ilk olarak soruyu işler ve teknik olup olmadığını denetler.
(Bu kontrol, makine öğrenmesi anahtar kelimeleri ve embedding benzerliği üzerinden yapılır.)

- Soru teknik değilse kullanıcı bilgilendirilir ve süreç sona erer.

- Soru teknikse embedding üretilir ve ChromaDB içinde benzer soru aranır.

- Benzerlik skoru yüksekse → aynı soru daha önce sorulmuş kabul edilir ve cevap veritabanından döndürülür.

- Benzerlik skoru düşükse → soru Gemini API’ye gönderilir, yeni bir cevap üretilir ve ChromaDB’ye kaydedilir.

- Kullanıcıya verilen cevap sonrası “Bu cevap yeterli miydi?” sorusu gösterilir.

- Kullanıcı “Hayır” derse sistem alternatif bir açıklama üretir; daha önce alternatif açıklama varsa veritabanından döner, yoksa Gemini’dan yeni bir açıklama alınır.

- Alternatif açıklama da yetersiz bulunursa kullanıcı isterse eğitmen için not bırakabilir ve sistem bu bilgilerle otomatik e-posta gönderir.

- Kullanıcı her 3 teknik soru sorduğunda sistem sohbet içinde otomatik olarak “Quiz başlatmak ister misiniz?” teklifi oluşturur.

- Quiz soruları, kullanıcının daha önce sorduğu teknik sorular üzerinden dinamik olarak oluşturulur; her soru için bir doğru ve üç yanlış seçenek hazırlanır.

- Quiz sonunda doğru/yanlış sayısı ve başarı oranı kullanıcıya gösterilir.

---

# 🙌 7. Destek

Her türlü geliştirme, hata veya fikir için katkı yapabilirsiniz.

**Geliştirici:** Ali Üre  
GitHub: https://github.com/Imaliure

