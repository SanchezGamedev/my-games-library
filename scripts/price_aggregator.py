import os
import requests
import urllib.parse
from bs4 import BeautifulSoup

# Получаем ключ ITAD из переменных окружения (в будущем из GitHub Secrets)
ITAD_API_KEY = os.environ.get("ITAD_API_KEY", "")

def get_itad_prices(steam_app_id):
    """
    Получает текущую минимальную цену и исторический минимум через IsThereAnyDeal API v2.
    Документация ITAD v2 требует сначала найти ID игры в их системе по Steam AppID.
    """
    if not ITAD_API_KEY:
        print("Внимание: ITAD_API_KEY не установлен.")
        return None

    try:
        # 1. Ищем ITAD ID по Steam AppID
        lookup_url = f"https://api.isthereanydeal.com/games/lookup/v1?key={ITAD_API_KEY}&appid={steam_app_id}"
        lookup_res = requests.get(lookup_url)
        lookup_res.raise_for_status()
        lookup_data = lookup_res.json()

        if not lookup_data.get("found"):
            return None
        
        itad_game_id = lookup_data["game"]["id"]

        # 2. Запрашиваем цены (Info)
        prices_url = f"https://api.isthereanydeal.com/games/info/v2?key={ITAD_API_KEY}&id={itad_game_id}"
        prices_res = requests.get(prices_url)
        prices_res.raise_for_status()
        price_data = prices_res.json()

        # Формируем ответ
        result = {
            "historical_low": price_data.get("historical_low", {}).get("price"),
            "current_lowest": price_data.get("deals", [{}])[0].get("price"),
            "store_name": price_data.get("deals", [{}])[0].get("shop", {}).get("name")
        }
        return result
    except Exception as e:
        print(f"Ошибка при запросе к ITAD для AppID {steam_app_id}: {e}")
        return None


def get_imggg_price(game_name):
    """
    Парсит сайт Instant Gaming (img.gg) по названию игры для поиска цены на ключи.
    Использует User-Agent для обхода базовых блокировок.
    """
    query = urllib.parse.quote(game_name)
    url = f"https://www.instant-gaming.com/en/search/?q={query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем первый результат в сетке товаров
        # Структура может немного меняться, ориентируемся на классы карточек IG
        first_item = soup.find('div', class_='item') 
        
        if first_item:
            title_elem = first_item.find('div', class_='name')
            price_elem = first_item.find('div', class_='price')
            
            if title_elem and price_elem:
                found_title = title_elem.text.strip()
                price_text = price_elem.text.strip().replace('€', '').replace('$', '').strip()
                
                try:
                    price_val = float(price_text)
                except ValueError:
                    price_val = None

                return {
                    "found_name": found_title,
                    "price": price_val,
                    "store_url": first_item.find('a', class_='cover')['href'] if first_item.find('a', class_='cover') else url
                }
    except Exception as e:
        print(f"Ошибка парсинга img.gg для {game_name}: {e}")
    
    return None

# Для тестирования модуля
if __name__ == "__main__":
    test_game = "Timberborn"
    test_appid = "1062090"
    
    print(f"Тестируем поиск на img.gg для {test_game}...")
    ig_data = get_imggg_price(test_game)
    print("Результат img.gg:", ig_data)
    
    print(f"\nТестируем API ITAD для AppID {test_appid} (нужен API ключ)...")
    itad_data = get_itad_prices(test_appid)
    print("Результат ITAD:", itad_data)