from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sqlite3
import hashlib
import os
import sys
from database import Database
from Gui.chessgame import ChessWindow
from session import load_session, clear_session, save_session
from Network.network import P2PNetwork
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.auto_login_done = False
        self.init_ui()
        self.hide()
        self.check_auto_login()

        
    def check_auto_login(self):
        """Проверить, есть ли сохранённый пользователь"""
        saved_user = load_session()
        print(f"Загружен пользователь {saved_user}")
        if saved_user:
            # Проверяем, существует ли пользователь в БД
            success, result = self.db.auto_login(saved_user)
            print(f"Авто-вход: {success}, {result}")
            
            if success:
                self.current_user = saved_user
                self.auto_login_done = True
                self.open_game_menu()
                return
        if not self.auto_login_done:   
            self.show()
    
    def showEvent(self, event):
        """Если авто-вход уже выполнен — не показываем окно"""
        if self.auto_login_done:
            event.ignore()  # не показываем
        else:
            super().showEvent(event)
            
    def open_game_menu(self):
        self.menu_window = GameMenuWindow(self.current_user)
        self.menu_window.show()
        self.close()
                    
    def init_ui(self):
        self.setWindowTitle("Шахматы - Вход")
        self.setGeometry(400, 200, 400, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        # Заголовок
        title = QLabel("Шахматы")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title)
        
        # Вкладки
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Вход")
        self.tabs.addTab(self.register_tab, "Регистрация")
        main_layout.addWidget(self.tabs)
        
        # === ВКЛАДКА ВХОДА ===
        login_layout = QVBoxLayout()
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        login_layout.addWidget(self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)
        
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.do_login)
        login_layout.addWidget(login_btn)
        
        login_layout.addStretch()
        self.login_tab.setLayout(login_layout)
        
        # === ВКЛАДКА РЕГИСТРАЦИИ ===
        register_layout = QVBoxLayout()
        
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Имя пользователя")
        register_layout.addWidget(self.reg_username)
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.reg_password)
        
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Подтвердите пароль")
        self.reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.reg_confirm)
        
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.do_register)
        register_layout.addWidget(register_btn)
        
        register_layout.addStretch()
        self.register_tab.setLayout(register_layout)
        
        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def show_message(self, text, is_error=False):
        self.status_label.setText(text)
        if is_error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: green;")
    
    def do_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            self.show_message("Заполните все поля!", True)
            return
        
        success, result = self.db.login_user(username, password)
        
        if success:
            self.current_user = username
            save_session(username)
            print(f"Сессия сохранена для {username}")
            self.show_message(f"Добро пожаловать, {username}!")
            self.open_game_menu()
        else:
            self.show_message(result, True)
    
    def do_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        
        if not username or not password:
            self.show_message("Заполните все поля!", True)
            return
        
        if password != confirm:
            self.show_message("Пароли не совпадают!", True)
            return
        
        success, message = self.db.register_user(username, password)
        self.show_message(message, not success)
        
        if success:
            self.tabs.setCurrentIndex(0)
            self.login_username.setText(username)
            self.login_password.setText("")
    
                
class GameMenuWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.db = Database()
        self.init_ui()
        self.load_stats()
    
    def load_stats(self):
        stats = self.db.get_stats(self.username)
        
        if stats:
            wins = stats['wins']    
            losses = stats['losses']
            draws = stats['draws']
            total = wins + losses + draws
            self.stats_label.setText(
                f"📊 Статистика: Побед: {wins}  Поражений: {losses}  Ничьих: {draws}  Всего: {total}"
            )
        else:
            self.stats_label.setText("📊 Статистика: Нет данных")
    
    def init_ui(self):
        self.setWindowTitle("Шахматы - Выбор режима")
        self.setGeometry(400, 200, 500, 450)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        logout_btn = QPushButton("🚪 Выйти из аккаунта")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        # Приветствие
        welcome = QLabel(f"Добро пожаловать, {self.username}!")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout.addWidget(welcome)
        
        # Статистика
        self.stats_label = QLabel("Загрузка статистики...")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)
        
        layout.addSpacing(20)
        
        # Кнопки режимов
        buttons = [
            ("🎮 Играть" , "classic"),
           # ("⚡️ Блиц (5 минут)", "blitz"),
          #  ("🚀 Рапид (10 минут)", "rapid"),
            ("🌐 Сетевая игра", "network"),
            ("⚙️ Настройки", "settings"),
        ]
        
        for text, mode in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, m=mode: self.select_mode(m))
            layout.addWidget(btn)
        
        layout.addStretch()
    
    def logout(self):
        """Выйти из аккаунта"""
        clear_session()  # удаляем сохранённого пользователя
        self.close()
        # Возвращаемся в окно входа
        self.login_window = LoginWindow()
        self.login_window.show()
        
    def select_mode(self, mode):
        if mode == "classic":
            self.start_game()
        elif mode == "blitz":
            self.start_game(time_control={"type": "blitz", "minutes": 5})
        elif mode == "rapid":
            self.start_game(time_control={"type": "rapid", "minutes": 10})
        elif mode == "network":
            self.start_network_setup()
        elif mode == "settings":
            QMessageBox.information(self, "Настройки", "Настройки в разработке")
        elif mode == "exit":
            self.close()
    
    def start_game(self, time_control=None):
        self.game_window = ChessWindow(game=None, time_control=time_control, username=self.username)
        self.game_window.show()
        self.close()
        
    def closeEvent(self, event):
        """
        Событие закрытия окна (Alt+F4, крестик)
        НЕ очищаем сессию, просто закрываем
        """
        print("closeEvent вызван")
        event.accept()  # закрываем окно, сессия остаётся
        
    def start_network_setup(self):
        """Открыть окно настройки сетевой игры"""
        self.network_window = NetworkSetupWindow(self.username)
        self.network_window.show()
        self.close()

class NetworkSetupWindow(QMainWindow):
    """Окно настройки сетевой игры"""
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.network = P2PNetwork()
        self.network.move_received.connect(self.on_network_move)
        self.network.opponent_connected.connect(self.on_opponent_connected)
        self.network.opponent_disconnected.connect(self.on_opponent_disconnected)
        self.network.status_message.connect(self.update_network_status)
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Сетевая игра")
        self.setGeometry(500, 300, 400, 300)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Заголовок
        title = QLabel("🌐 Сетевая игра")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Статус сети
        self.network_status = QLabel("Офлайн")
        self.network_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.network_status.setStyleSheet("color: gray; font-weight: bold;")
        layout.addWidget(self.network_status)
        
        # IP
        self.ip_label = QLabel(f"Ваш IP: {self.network.get_local_ip()}")
        self.ip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ip_label)
        
        layout.addSpacing(20)
        
        # Кнопки
        self.host_btn = QPushButton("🎮 Создать игру (сервер)")
        self.host_btn.clicked.connect(self.host_game)
        layout.addWidget(self.host_btn)
        
        self.join_btn = QPushButton("🔌 Подключиться к игре")
        self.join_btn.clicked.connect(self.join_game)
        layout.addWidget(self.join_btn)
        
        self.disconnect_btn = QPushButton("❌ Отключиться")
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)
        
        layout.addSpacing(20)
        
        # Кнопка назад
        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)
        
        layout.addStretch()
    
    def host_game(self):
        if self.network.host_game(5555):
            self.host_btn.setEnabled(False)
            self.join_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.update_network_status("Ожидание игрока...")
    
    def join_game(self):
        ip, ok = QInputDialog.getText(
            self, 
            "Подключение", 
            "Введите IP противника:",
            text=self.network.get_local_ip()
        )
        if ok and ip:
            if self.network.join_game(ip, 5555):
                self.host_btn.setEnabled(False)
                self.join_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
    
    def disconnect(self):
        self.network.disconnect()
        self.host_btn.setEnabled(True)
        self.join_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.update_network_status("Отключён")
    
    def update_network_status(self, message):
        self.network_status.setText(message)
        if "ошибка" in message.lower():
            self.network_status.setStyleSheet("color: red; font-weight: bold;")
        elif "подключ" in message.lower() or "игрок" in message.lower():
            self.network_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.network_status.setStyleSheet("color: blue; font-weight: bold;")
    def on_opponent_connected(self):
        self.update_network_status("Противник подключился!")
        QMessageBox.information(self, "Сеть", "Противник подключён!\nНачинаем игру.")
        self.start_network_game()
    
    def on_opponent_disconnected(self):
        self.update_network_status("Противник отключился")
        QMessageBox.warning(self, "Сеть", "Противник отключился.")
        self.disconnect()
    
    def on_network_move(self, from_pos, to_pos):
        """Получен ход от противника (передаётся в игровое окно)"""
        if hasattr(self, 'game_window') and self.game_window:
            self.game_window.on_network_move(from_pos, to_pos)
    
    def start_network_game(self):
        """Запустить игру с сетью"""
        self.game_window = ChessWindow(
            game=None, 
            time_control=None, 
            username=self.username,
            network=self.network  # ← передаём сеть
        )
        self.game_window.show()
        self.close()
    
    def go_back(self):
        """Вернуться в главное меню"""
        self.network.disconnect()
        self.close()
        self.menu_window = GameMenuWindow(self.username)
        self.menu_window.show()