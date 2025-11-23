## File: utils/preprocessing.py
import re
import string

from data.anahtar_kelimeler import A

def preprocess_text(text: str) -> str:
    # Manuel Türkçe stopword listesi
    stop_words = {
        "ve", "bir", "bu", "ile", "de", "da", "için", "ama", "fakat", "gibi", "çok",
        "daha", "en", "mi", "mı", "mu", "mü", "ben", "sen", "o", "biz", "siz", "onlar",
        "ki", "ne", "niçin", "neden", "nasıl", "hangi", "şu", "şey", "hep", "her", "hiç"
    }

    # 1. Küçük harfe çevirme
    text = text.lower()

    # 2. Noktalama işaretlerini kaldırma
    text = text.translate(str.maketrans('', '', string.punctuation))

    # 3. Fazla boşlukları temizleme
    text = re.sub(r'\s+', ' ', text).strip()

    # 4. Stopword'leri kaldırma
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]

    return ' '.join(filtered_words)


def get_keyword_match_score(text):
    count = sum(1 for keyword in A if keyword in text.lower())
    return min(count / 3, 1.0)  # Max 1.0, normalize edilmiş
