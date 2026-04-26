# Chess/session.py
import os
import json

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.json")

def save_session(username):
    """Сохранить имя пользователя"""
    print(f"Путь к файлу сессии {SESSION_FILE}")

    print(f"Сохраняем сессию {username}")
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump({"username": username}, f)
        return True
    except Exception as e:
        print(f"Ошибка сохранения {e}")
        return False

def load_session():
    """Загрузить имя пользователя"""
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            print(f"Загружено из сессии: {data}")
            return data.get("username")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None

def clear_session():
    print("Очищаем сессию")
    """Очистить сохранённого пользователя"""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return True
    except Exception as e:
            print(f"Ошибка очистки: {e}")
            return None
