# Flight-Planner Configuration Automation

Este projeto automatiza a coleta de dados de uma API e o envio desses dados por e-mail em um horário agendado. Ele é útil para monitorar e compartilhar configurações ou dados atualizados de sistemas, como o Flight-Planner.

## Funcionalidades

- **Requisição HTTP**: Faz uma requisição GET para uma URL configurada.
- **Salvamento de Dados**: Salva a resposta da API em um arquivo JSON com carimbo de data/hora.
- **Agendamento**: Executa a tarefa diariamente em um horário específico.
- **Envio de E-mail**: Envia o arquivo JSON gerado como anexo para uma lista de destinatários via e-mail.

## Pré-requisitos

- Python 3.x
- Bibliotecas Python: `requests`, `schedule`, `python-dotenv`, `smtplib`
- Conta de e-mail do Gmail para envio de e-mails (ou ajuste o SMTP para outro provedor).

## Configuração

1. **Instale as dependências**:
   ```bash
   pip install requests schedule python-dotenv
   ```

2. **Crie um arquivo `.env`** na raiz do projeto com as seguintes variáveis de ambiente:
   ```plaintext
   REQUEST_URL=<URL_da_API>
   MAIL_AUTH_USER=<seu_email@gmail.com>
   MAIL_AUTH_PASS=<sua_senha_do_email>
   SCHEDULE_RECIPIENTS=<email1@example.com,email2@example.com>
   SCHEDULE_TIME=<HH:MM:SS>  # Horário padrão: "20:00:00"
   ```

   - `REQUEST_URL`: URL da API que será consultada.
   - `MAIL_AUTH_USER`: E-mail do remetente (Gmail).
   - `MAIL_AUTH_PASS`: Senha do e-mail (ou senha de app, se usar autenticação de dois fatores).
   - `SCHEDULE_RECIPIENTS`: Lista de e-mails dos destinatários, separados por vírgula.
   - `SCHEDULE_TIME`: Horário diário para execução (formato `HH:MM:SS`).

3. **Execute o script**:
   ```bash
   python main.py
   ```

## Como Funciona

1. O script valida as variáveis de ambiente e carrega as configurações.
2. Diariamente, no horário agendado (`SCHEDULE_TIME`), ele:
   - Faz uma requisição GET para a URL configurada.
   - Salva a resposta em um arquivo JSON com o nome no formato `response_AAAA-MM-DD_HH-MM-SS.json`.
   - Envia o arquivo como anexo por e-mail para os destinatários configurados.

## Exemplo de Saída

- **Arquivo JSON**:
  ```json
  {
      "config": {
          "status": "scheduled"
      }
  }
  ```

- **E-mail**:
  - Assunto: `API Response - DD/MM/YYYY HH:MM`
  - Corpo: `Arquivo JSON anexo: response_AAAA-MM-DD_HH-MM-SS.json`
  - Anexo: Arquivo JSON gerado.

## Personalização

- **SMTP**: Para usar outro provedor de e-mail, altere as configurações do SMTP no método `send_email`.
- **Formato do JSON**: Ajuste o tratamento da resposta da API no método `fetch_and_save` conforme necessário.

## Observações

- **Segurança**: Não compartilhe o arquivo `.env` ou credenciais de e-mail publicamente.
- **Logs**: O script imprime logs no console para facilitar a depuração.

## Licença

Este projeto é open-source. Sinta-se à vontade para utilizá-lo e modificá-lo conforme suas necessidades.

---