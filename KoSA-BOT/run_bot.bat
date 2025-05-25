:: --- run_bot.bat (для Windows) ---

@echo off
echo Запускаємо Telegram-бота Kosa Service...

:: Якщо ти використовуєш віртуальне середовище (рекомендовано):
:: echo Активуємо віртуальне середовище...
:: REM Заміни C:\шлях\до\твого\venv\Scripts\activate.bat на реальний шлях до твого venv
:: CALL C:\шлях\до\твого\venv\Scripts\activate.bat

:: Запуск Python-скрипта
:: Нижче вказано повний шлях до Python-скрипта.
:: Переконайся, що 'python' додано до PATH, або вкажи повний шлях до python.exe

:: наприклад: C:\Python39\python.exe "D:\Projekts\KoSA-BOT\kosa_bot_v3.py"
python "kosa_bot_v3.py"

echo Роботу бота завершено або виникла помилка.
pause :: Щоб вікно не закривалося одразу

set TELEGRAM_BOT_TOKEN=7589770061:AAGRFTtTSi49bipuejyaVB5hPUWLYEJHwGA
set CHAT_ID=-1002596870519