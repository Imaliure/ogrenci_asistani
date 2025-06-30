
# 🎓 AI Öğrenci Asistanı

Bu proje, makine öğrenmesi ve yapay zeka konularında öğrencilere yardımcı olmak için geliştirilmiş bir **soru-cevap ve quiz tabanlı asistan**dır. Proje sohbet tabanlı çalışır ve istenirse kullanıcıya özel quiz hazırlayabilir. Ayrıca kullanıcı, verilen cevapların yetersiz olması durumunda eğitmene e-posta gönderebilir.

---

## 🚀 Başlangıç

### 1️⃣ **Gereksinimler:**
- Python 3.10+
- pip

### 2️⃣ **Bağımlılıkları Kur:**
```bash
pip install -r requirements.txt
```

### 3️⃣ **ChromaDB Başlangıç Verilerini Yükle:**
Projenin çalışabilmesi için ilk veri setinin ChromaDB'ye yüklenmesi gerekiyor. Bunun için:

```bash
python chroma_setup.py
```

> ✅ Bu işlem, `data.json` dosyasındaki başlangıç verilerini ChromaDB veri tabanına aktarır.

---

## 📦 Proje Yapısı

```
.
├── data.json                # Başlangıç veri seti
├── chroma_setup.py          # Başlangıç verilerini ChromaDB'ye yükler
├── main.py                  # Ana uygulama
├── services/                # OpenAI ve veri yönetimi servisleri
├── utils/                   # Preprocessing, quiz, e-posta ve benzeri yardımcı fonksiyonlar
├── chroma_local_db/         # Yerel ChromaDB veritabanı
├── requirements.txt         # Gerekli kütüphaneler
└── README.md                # Proje dökümantasyonu
```

---

## ⚙️ .env Ayarları

Proje kök dizininde `.env` dosyası oluşturun ve aşağıdaki bilgileri doldurun:

```env
OPENAI_API_KEY=your_openai_api_key
```

## 🏃‍♂️ Çalıştırmak için

```bash
python main.py
```

---

## 💡 Kullanım

- 📖 Kullanıcı sorular sorar.
- 🔍 Sistem önce veritabanından cevap arar.
- ❌ Cevap yoksa OpenAI'den cevap alır ve veritabanına ekler.
- ✅ 3 soru sonrası sistem **"Quiz yapmak ister misin?"** diye sorar.
- 🎯 Quiz, sohbet sırasında sorulan teknik sorulara bağlı olarak hazırlanır.
- 📩 Kullanıcı cevaplardan memnun değilse, **eğitmene e-posta gönderebilir.**
- 📝 E-posta gönderilirken, kullanıcı **kendi mesajını veya notunu** da ekleyebilir.

---

## 🏹 Quiz Sistemi Özellikleri
- Sohbet sırasında sorulan konulara dayalı.
- Çoktan seçmeli sorular üretir.
- Cevaplar ChromaDB'den alınan doğru ve yanlış cevaplarla oluşturulur.
- Quiz sonunda puan ve başarı durumu gösterilir.

---

## 📧 Öğretmene E-posta Bildirimi
- Quiz sonrası veya açıklamalar yetersizse kullanıcı, eğitmene e-posta gönderebilir.
- Kullanıcı ayrıca **kendi mesajını** ekleyebilir.
- Sistem otomatik olarak soru, verilen cevaplar ve öğrenci notunu öğretmene iletir.

---

## 👨‍💻 Geliştirici

- Ali Üre — [LinkedIn](https://www.linkedin.com/in/aliure) | [GitHub](https://github.com/Imaliure)

---

## ⭐ Desteklemek için
Projeyi beğendiyseniz ⭐ yıldız verip paylaşabilirsiniz!

---

## 🔥 Not:
**Başlamadan önce mutlaka şu adımları takip edin:**
1. `pip install -r requirements.txt`
2. `python chroma_setup.py` — **(Bu adım olmazsa veri tabanı boş olur ve sistem çalışmaz!)**
3. `python main.py`

---

## 📌 Özet:
Bu dosyaya kadar olan sistem şu şekilde işler:
- `chroma_setup.py` ile veri tabanı yüklemesi yapılır.
- `main.py` üzerinden sohbet başlar, sistem önce veritabanından cevap arar.
- 3 soru sonrası otomatik quiz teklifi gelir.
- Cevaplardan memnun olunmazsa, eğitmene kendi mesajınızı da içeren bir mail atabilirsiniz.
