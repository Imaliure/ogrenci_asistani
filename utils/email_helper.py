import smtplib
from email.message import EmailMessage

def send_email_to_teacher(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "urea3832@gmail.com"         # Gönderen
    msg['To'] = "ureali90@gmail.com"           # Eğitmen (alıcının maili)

    try:
        # Gmail için SSL kullanarak SMTP bağlantısı
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("urea3832@gmail.com", "eqvxguuhrlcqtnyq")  # Giriş yap
            smtp.send_message(msg)
            print("Eğitmene e-posta gönderildi.")
    except Exception as e:
        print("E-posta gönderilemedi:", e)
