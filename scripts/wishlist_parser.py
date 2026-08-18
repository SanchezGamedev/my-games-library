import requests

def fetch_steam_wishlist(steam_id64):
    """
    Загружает публичный вишлист Steam.
    Внимание: Профиль Steam и список желаемого должны быть открыты (Public) в настройках приватности!
    """
    url = f"https://store.steampowered.com/wishlist/id/{steam_id64}/wishlistdata/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        wishlist = []
        for app_id, info in data.items():
            # Steam возвращает список как словарь объектов. Проверяем, что данные корректны.
            if isinstance(info, dict):
                wishlist.append({
                    "app_id": str(app_id),
                    "name": info.get("name"),
                    "priority": info.get("priority", 0),
                    "source": "Steam"
                })
        return wishlist
    except Exception as e:
        print(f"Ошибка при получении вишлиста Steam: {e}")
        return []

if __name__ == "__main__":
    # ТЕСТ: Замени на свой SteamID64 (набор из 17 цифр, обычно начинается на 7656119...)
    test_steam_id = "76561198982814522" 
    
    print(f"Пытаемся получить вишлист для ID: {test_steam_id}...")
    my_wishlist = fetch_steam_wishlist(test_steam_id)
    print(f"Найдено игр: {len(my_wishlist)}")
    if my_wishlist:
        print("Первые 3 игры:", my_wishlist[:3])
