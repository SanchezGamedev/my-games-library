import os
import requests

# Ключи будут браться из GitHub Secrets при работе в облаке
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

def send_telegram_push(game_name, current_price, store_name, is_historical_low, match_score=None, link=""):
    """
    Формирует и отправляет сообщение в Telegram.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print(f"Telegram уведомление для {game_name} пропущено (не заданы ключи).")
        return

    # Формируем текст сообщения
    message = f"🎮 *Отличная скидка!*\n\n*{game_name}*\n"
    message += f"📉 Цена: {current_price}\n"
    message += f"🏪 Магазин: {store_name}\n"
    
    if is_historical_low:
        message += "🔥 *Это исторический минимум!*\n"
        
    if match_score:
        message += f"🎯 Совпадение вкуса: {match_score}%\n"
        
    if link:
        message += f"\n🔗 [Ссылка на игру]({link})"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Уведомление для {game_name} успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")