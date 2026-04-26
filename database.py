import sqlite3
import hashlib
from config import DB_PATH
import sys
import os
def get_db_path():
    """Возвращает путь к БД в зависимости от способа запуска"""
    if getattr(sys, 'frozen', False):
        # Запущено как .exe — БД рядом с программой
        return os.path.join(os.path.dirname(sys.executable), 'chess_stats.db')
    else:
        # Запущено как скрипт — БД в папке проекта
        return DB_PATH  # или 'chess_stats.db'
class Database:
    """Класс для работы с базой данных пользователей"""
    
    def __init__(self):
        self.db_path = get_db_path()
        self.create_tables()
    
    def create_tables(self):
        """Создаёт таблицы, если их нет"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str) -> tuple:
        """
        Регистрирует нового пользователя
        Возвращает: (успех, сообщение)
        """
        username = username.strip()
        
        if not username or not password:
            return False, "Заполните все поля!"
        
        if len(password) < 4:
            return False, "Пароль должен быть минимум 4 символа!"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Имя пользователя уже занято!"
        
        # Регистрируем
        password_hash = self.hash_password(password)
        cursor.execute(
            "INSERT INTO Users (name, password) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        conn.close()
        
        return True, "Регистрация успешна!"
    
    def login_user(self, username: str, password: str) -> tuple:
        """
        Вход пользователя
        Возвращает: (успех, данные_пользователя_или_сообщение)
        """
        username = username.strip()
        
        if not username or not password:
            return False, "Заполните все поля!"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and self.hash_password(password) == user[2]:
            # user: (id, name, password, wins, losses, draws)
            return True, user
        return False, "Неверное имя или пароль!"
    
    def get_stats(self, username: str) -> dict:
        """
        Получает статистику пользователя
        Возвращает: словарь с wins, losses, draws или None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT wins, losses, draws FROM Users WHERE name = ?",
            (username,)
        )
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return {
                "wins": stats[0],
                "losses": stats[1],
                "draws": stats[2]
            }
        return None
    
    def update_stats(self, username: str, result: str) -> None:
        """
        Обновляет статистику после игры
        result: 'win', 'loss', 'draw'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if result == 'win':
            cursor.execute(
                "UPDATE Users SET wins = wins + 1 WHERE name = ?",
                (username,)
            )
        elif result == 'loss':
            cursor.execute(
                "UPDATE Users SET losses = losses + 1 WHERE name = ?",
                (username,)
            )
        elif result == 'draw':
            cursor.execute(
                "UPDATE Users SET draws = draws + 1 WHERE name = ?",
                (username,)
            )
        
        conn.commit()
        conn.close()
    
    def get_all_users(self) -> list:
        """Возвращает список всех пользователей (для таблицы лидеров)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, wins, losses, draws FROM Users ORDER BY wins DESC"
        )
        users = cursor.fetchall()
        conn.close()
        return users
    
    def auto_login(self, username):
        """Автоматический вход по имени (без проверки пароля)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, user
        return False, "Пользователь не найден"
    
    def delete_user(self, username: str) -> bool:
        """Удаляет пользователя (для администрирования)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE name = ?", (username,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0