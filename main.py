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

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Configurações via variáveis de ambiente
ENV_CONFIG = {
    "URL": os.getenv("REQUEST_URL"),
    "SCHEDULE_TIME": os.getenv("SCHEDULE_TIME", "20:00:00"),
    "MAIL_USER": os.getenv("MAIL_AUTH_USER"),
    "MAIL_PASSWORD": os.getenv("MAIL_AUTH_PASS"),
    "MAIL_RECIPIENTS": os.getenv("SCHEDULE_RECIPIENTS").split(","),
    "SUBJECT": os.getenv("SUBJECT"),
    "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "144")),  
    "ENABLE_EMAIL": os.getenv("ENABLE_EMAIL", False).capitalize()
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
        msg["To"] = ENV_CONFIG["MAIL_USER"]
        msg["Subject"] = f"{ENV_CONFIG['SUBJECT']} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        msg["Bcc"] = ", ".join(ENV_CONFIG["MAIL_RECIPIENTS"])

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

def fetch_with_retry():
    attempt = 0
    while attempt < ENV_CONFIG["MAX_RETRIES"]:
        try:
            response = requests.get(ENV_CONFIG["URL"])
            response.raise_for_status()
            return response
        except Exception as e:
            attempt += 1
            print(f"Tentativa {attempt}/{ENV_CONFIG['MAX_RETRIES']} falhou: {str(e)}")
            if attempt < ENV_CONFIG["MAX_RETRIES"]:
                print("Nova tentativa em 10 minutos...")
                time.sleep(600)  # 10 minutos
    return None

def fetch_and_save():
    print("\nIniciando processo de coleta de dados...")
    response = fetch_with_retry()
    
    if response:
        filename = f"response_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(response.json(), file, ensure_ascii=False, indent=4)
            print(f"Dados salvos em {filename}")
            
            # Verifica se o envio de e-mails está habilitado
            if ENV_CONFIG["ENABLE_EMAIL"]:
                send_email(filename)
            else:
                print("Envio de e-mails desabilitado.")
        except Exception as e:
            print(f"Erro ao salvar/enviar dados: {str(e)}")
    else:
        print("Todas as tentativas falharam. Abortando processo.")

def main():
    validate_env()
    
    print(f'''
    Configurações carregadas:
    - URL: {ENV_CONFIG["URL"]}
    - Horário: {ENV_CONFIG["SCHEDULE_TIME"]}
    - Destinatários: {ENV_CONFIG["MAIL_RECIPIENTS"]}
    - Tentativas máximas: {ENV_CONFIG["MAX_RETRIES"]}
    - Envio de e-mails: {"Habilitado" if ENV_CONFIG["ENABLE_EMAIL"] else "Desabilitado"}
    ''')
    
    schedule.every().day.at(ENV_CONFIG["SCHEDULE_TIME"]).do(fetch_and_save)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()