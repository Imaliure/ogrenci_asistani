## File: utils/email_helper.py
import smtplib
from email.message import EmailMessage

def send_email_to_teacher(subject, body, student_message=None):
    msg = EmailMessage()

    full_body = body
    if student_message and student_message.strip() != "":
        full_body += f"\n\n📨 Öğrenci Notu:\n{student_message}"

    msg.set_content(full_body)
    msg['Subject'] = subject
    msg['From'] = "urea3832@gmail.com"
    msg['To'] = "ureali90@gmail.com"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("urea3832@gmail.com", "eqvxguuhrlcqtnyq")
            smtp.send_message(msg)
            print("✅ Eğitmene e-posta gönderildi.")
    except Exception as e:
        print("❌ E-posta gönderilemedi:", e)

