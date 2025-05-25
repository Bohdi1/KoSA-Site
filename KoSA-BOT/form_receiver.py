from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '7589770061:AAGRFTtTSi49bipuejyaVB5hPUWLYEJHwGA'
CHAT_ID = 'ВАШ_CHAT_ID'  # Вкажіть chat_id вашого бота або групи

@app.route('/send_form', methods=['POST'])
def send_form():
    name = request.form.get('name')
    phone = request.form.get('phone')
    message = request.form.get('message')
    text = f"Нова заявка з сайту:\nІм'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': text})
    return 'OK'

if __name__ == '__main__':
    app.run(port=5000)
