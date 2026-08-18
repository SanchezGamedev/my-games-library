import json
import os
from datetime import datetime

# Импортируем наши модули
from wishlist_parser import fetch_steam_wishlist
from price_aggregator import get_itad_prices, get_imggg_price
from recommendation_engine import generate_recommendations
from telegram_notifier import send_telegram_push

# === НАСТРОЙКИ ===
# Вставь сюда свой SteamID64, который ты узнал
STEAM_ID = "fucking_nigga" 

# Пути к файлам (предполагается, что скрипт запускается из корня репозитория)
LIBRARY_FILE = "games.json"
HUB_DATA_FILE = "data/generated_hub.json"
NOTIFIED_FILE = "data/notified_deals.json"

def load_json(filepath):
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_json(filepath, data):
    # Убедимся, что папка существует
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("=== Старт обновления Game Hub ===")
    
    # 1. Загрузка данных библиотеки
    playnite_data = load_json(LIBRARY_FILE)
    print(f"Загружено игр из библиотеки: {len(playnite_data)}")

    # 2. Получение вишлиста
    wishlist = fetch_steam_wishlist(STEAM_ID)
    print(f"Загружено игр из вишлиста: {len(wishlist)}")

    # 3. Генерация рекомендаций
    recommendations = generate_recommendations(playnite_data, limit_favorites=5)
    print(f"Сгенерировано рекомендаций: {len(recommendations)}")

    # 4. Загрузка состояния уведомлений (чтобы не спамить)
    notified_deals = load_json(NOTIFIED_FILE)
    if not isinstance(notified_deals, dict):
        notified_deals = {}

    deals_list = []

    # 5. Сбор цен для вишлиста
    for game in wishlist:
        app_id = str(game['app_id'])
        game_name = game['name']
        
        # Проверяем ITAD
        itad_info = get_itad_prices(app_id)
        # Проверяем img.gg
        img_info = get_imggg_price(game_name)
        
        best_price = None
        store = None
        is_historical_low = False
        link = ""

        if itad_info and itad_info.get("current_lowest"):
            best_price = itad_info["current_lowest"]
            store = itad_info["store_name"]
            if itad_info.get("historical_low") and best_price <= itad_info["historical_low"]:
                is_historical_low = True

        if img_info and img_info.get("price"):
            # Если на img.gg дешевле, выбираем его
            if best_price is None or img_info["price"] < best_price:
                best_price = img_info["price"]
                store = "img.gg"
                link = img_info["store_url"]
                # Считаем любую лучшую цену на ключи выгодной
                is_historical_low = True 
        
        if best_price is not None:
            deal_data = {
                "app_id": app_id,
                "name": game_name,
                "price": best_price,
                "store": store,
                "is_historical_low": is_historical_low,
                "link": link
            }
            deals_list.append(deal_data)

            # 6. Логика отправки Telegram-уведомлений
            # Отправляем, если цена <= исторического минимума ИЛИ это магазин ключей, 
            # и мы еще не уведомляли об этой цене
            prev_notified = notified_deals.get(app_id, {}).get("lowest_price_notified", float('inf'))
            
            if is_historical_low and best_price < prev_notified:
                send_telegram_push(
                    game_name=game_name,
                    current_price=best_price,
                    store_name=store,
                    is_historical_low=is_historical_low,
                    link=link
                )
                # Обновляем состояние
                notified_deals[app_id] = {
                    "lowest_price_notified": best_price,
                    "date": datetime.now().isoformat()
                }

    # 7. Формирование финального файла для сайта
    hub_data = {
        "last_updated": datetime.now().isoformat(),
        "library_count": len(playnite_data),
        "deals": deals_list,
        "recommendations": recommendations
    }

    save_json(HUB_DATA_FILE, hub_data)
    save_json(NOTIFIED_FILE, notified_deals)
    
    print("=== Обновление успешно завершено ===")

if __name__ == "__main__":
    main()
