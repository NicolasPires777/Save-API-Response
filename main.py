import os
import requests
import json
import schedule
import time
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Carregar variáveis de ambiente (crie um arquivo .env na mesma pasta)
from dotenv import load_dotenv
load_dotenv()

# Configurações via variáveis de ambiente (OBRIGATÓRIAS)
ENV_CONFIG = {
    "URL": os.getenv("REQUEST_URL"),
    "SCHEDULE_TIME": os.getenv("SCHEDULE_TIME", "20:00:00"),
    "MAIL_USER": os.getenv("MAIL_AUTH_USER"),
    "MAIL_PASSWORD": os.getenv("MAIL_AUTH_PASS"),
    "MAIL_RECIPIENTS": os.getenv("SCHEDULE_RECIPIENTS").split(","),  # Lista separada por vírgulas
    "SUBJECT": os.getenv("SUBJECT")
}

def validate_env():
    required_vars = ["REQUEST_URL", "MAIL_AUTH_USER", "MAIL_AUTH_PASS", "SCHEDULE_RECIPIENTS"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Variável de ambiente {var} não configurada!")

def send_email(filename):
    try:
        msg = MIMEMultipart()
        msg["From"] = ENV_CONFIG["MAIL_USER"]
        msg["To"] = ENV_CONFIG["MAIL_USER"]  # Remetente como destinatário visível
        msg["Subject"] = f"{ENV_CONFIG['SUBJECT']} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        msg["Bcc"] = ", ".join(ENV_CONFIG["MAIL_RECIPIENTS"])  # Destinatários ocultos

        body = f"Arquivo JSON anexo: {filename}"
        msg.attach(MIMEText(body, "plain"))

        with open(filename, "rb") as file:
            attachment = MIMEApplication(file.read(), Name=filename)
            attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
            msg.attach(attachment)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(ENV_CONFIG["MAIL_USER"], ENV_CONFIG["MAIL_PASSWORD"])
            server.send_message(msg)
        
        print(f"E-mail enviado para {len(ENV_CONFIG['MAIL_RECIPIENTS'])} destinatários")

    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

def fetch_and_save():
    try:
        response = requests.get(ENV_CONFIG["URL"])
        response.raise_for_status()

        filename = f"response_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(response.json(), file, ensure_ascii=False, indent=4)

        print(f"Dados salvos em {filename}")
        send_email(filename)

    except Exception as e:
        print(f"Erro na requisição: {str(e)}")

def main():
    validate_env()

    schedule.every().day.at(ENV_CONFIG["SCHEDULE_TIME"]).do(fetch_and_save)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    print(f'''
    Configurações carregadas:
    - URL: {ENV_CONFIG["URL"]}
    - Horário: {ENV_CONFIG["SCHEDULE_TIME"]}
    - Destinatários: {ENV_CONFIG["MAIL_RECIPIENTS"]}
    ''')
    main()