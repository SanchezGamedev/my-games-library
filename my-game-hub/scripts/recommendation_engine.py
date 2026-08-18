import requests

def get_steampeek_recommendations(app_id):
    """
    Запрос к SteamPeek API для получения списка похожих игр.
    """
    url = f"https://steampeek.hu/api/game/{app_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            return data.get("response", {}).get("similar", [])
        return []
    except Exception as e:
        print(f"Ошибка при запросе к SteamPeek API для AppID {app_id}: {e}")
        return []

def generate_recommendations(playnite_data, limit_favorites=5):
    """
    Генерирует массив рекомендаций на основе лучших игр пользователя.
    """
    # 1. Собираем все имеющиеся AppID для строгой фильтрации
    owned_app_ids = set()
    for game in playnite_data:
        steam_id = game.get("SteamId")
        if steam_id:
            owned_app_ids.add(str(steam_id))
            
    # 2. Выбираем топ любимых игр (оценка >= 80)
    favorites = [g for g in playnite_data if g.get("UserScore", 0) >= 80 and g.get("SteamId")]
    favorites = sorted(favorites, key=lambda x: x.get("UserScore", 0), reverse=True)[:limit_favorites]
    
    recommendations = {}
    
    # 3. Для каждой любимой игры ищем похожие
    for fav in favorites:
        app_id = str(fav["SteamId"])
        similar_games = get_steampeek_recommendations(app_id)
        
        for sim in similar_games[:7]:  # Берем топ-7 похожих на каждую
            sim_app_id = str(sim.get("appid"))
            
            # Строгая фильтрация: пропускаем, если игра уже есть в библиотеке
            if sim_app_id in owned_app_ids:
                continue
                
            if sim_app_id not in recommendations:
                recommendations[sim_app_id] = {
                    "app_id": sim_app_id,
                    "name": sim.get("title"),
                    "similar_to": [fav["Name"]],
                    "match_score": sim.get("score", 0)
                }
            else:
                # Если игру рекомендовали несколько раз, добавляем источник
                recommendations[sim_app_id]["similar_to"].append(fav["Name"])
    
    # Сортируем итоговый список по Match Score (убыванию)
    result = list(recommendations.values())
    result = sorted(result, key=lambda x: x.get("match_score", 0), reverse=True)
    
    return result

# Для тестирования модуля
if __name__ == "__main__":
    # Мок-данные, имитирующие твой JSON из Playnite
    mock_playnite_data = [
        {"Name": "Timberborn", "SteamId": "1062090", "UserScore": 90},
        {"Name": "Cyberpunk 2077", "SteamId": "1091500", "UserScore": 85},
        {"Name": "Hollow Knight", "SteamId": "367520", "UserScore": 100} # Имеющаяся игра для проверки фильтра
    ]
    
    print("Генерируем рекомендации на основе тестовых данных...")
    recs = generate_recommendations(mock_playnite_data, limit_favorites=2)
    
    for i, rec in enumerate(recs[:5], 1):
        print(f"{i}. {rec['name']} (Match: {rec['match_score']}) - Похоже на: {', '.join(rec['similar_to'])}")