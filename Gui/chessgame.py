from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from Engine.game import Game
from Network.network import P2PNetwork 
from Engine.pieces import Queen, Rook, Bishop, Knight, Pawn
import os
import sys
from database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ChessSquare(QLabel):
    """ШАХМАТНАЯ КЛЕТКА"""
    
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.is_light = (row + col) % 2 == 0
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(60, 60)
        self.update_style()
    
    def update_style(self):
        """КРАСКА КЛЕТОК"""
        if self.is_light:
            self.setStyleSheet("background-color: #f0d9b5; border: 1px solid #8b4513;")
        else:
            self.setStyleSheet("background-color: #b58863; border: 1px solid #8b4513;")


class ChessWindow(QMainWindow):
    """ГЛАВНОЕ ОКНО"""
    
    def __init__(self, game=None, time_control=None, username=None, network=None):
        super().__init__()
        self.username = username  # сохраняем имя для статистики
        self.time_control = time_control  # сохраняем настройки времени
        self.db = Database()
        self.network = network
        
        #ЗАГРУЗКА ИГРЫ
        if game:
            self.game = game
        else:
            from Engine.game import Game
            self.game = Game()
        
        #СЕТЕВЫЕ МОДУЛИ
        if self.network:
            self.network.move_received.connect(self.on_network_move)
            self.network.opponent_connected.connect(self.on_opponent_connected)
            self.network.opponent_disconnected.connect(self.on_opponent_disconnected)
            self.network.status_message.connect(self.update_network_status)
            self.network.resign_received.connect(self.on_opponent_resign)
        
        #КЛЕТКИ НЕ ВЫБРАНЫ
        self.selected_square = None
        
        #ЗАПУСК ПРОГИ
        self.init_ui()
        self.update_board()
    
    
    def exit_to_menu(self):
        """Выйти в главное меню с предупреждением"""
        reply = QMessageBox.question(
            self,
            "Выход в меню",
            "Вы уверены, что хотите выйти?\nТекущая игра будет потеряна.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Если есть сеть — отключаемся
            if self.network:
                self.network.disconnect()
            
            self.close()
            
            # Открываем главное меню
            from Gui.main_menu import GameMenuWindow
            self.menu_window = GameMenuWindow(self.username if self.username else "Гость")
            self.menu_window.show()
                
    def update_stats_after_game(self, result):
        """Вызвать после окончания игры"""
        if self.username:
            if result == 'win':
                self.db.update_stats(self.username, 'win')
            elif result == 'loss':
                self.db.update_stats(self.username, 'loss')
            elif result == 'draw':
                self.db.update_stats(self.username, 'draw')

            
    def init_ui(self):
        """САМ ГРАФИЧЕСКИЙ ИНТЕРФЕЙС"""
        
        self.setWindowTitle("Шахматы")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        #ГОРИЗОНТАЛЬНЫЙ LAYOUT
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        
        #ЛЕВАЯ ЧАСТЬ: ДОСКА
        board_widget = QWidget() #ВИДЖЕТ ДОСКИ
        board_widget.setFixedSize(480, 480) #РАЗМЕРЫ ДОСКИ (8X8 КЛЕТОК)
        board_layout = QGridLayout() #СЕТКА (LAYOUT)
        board_layout.setSpacing(0) #РАССТОЯНИЕ МЕЖДУ КЛЕТКАМИ = 0
        board_widget.setLayout(board_layout) #УСТАНОВКА LAYOUT НА ВИДЖЕТ ДОСКИ (ПОКА ЧТО НЕВИДИМО)
        
        #СОЗДАНИЕ КЛЕТОК
        self.squares = [] #МАССИВ ДЛЯ ХРАНЕНИЯ ВСЕХ КЛЕТОК
        for row in range(8):
            row_squares = [] #ВРЕМЕННЫЙ МАССИВ ДЛЯ ХРАНЕНИЯ ОДНОЙ СТРОКИ
            for col in range(8):
                square = ChessSquare(row, col) #СОЗДАЕМ КЛЕТКУ
                square.mousePressEvent = lambda _, r=row, c=col: self.on_square_click(r, c) #ОБРАБОТЧИК КЛИКА ДЛЯ ПОСЛЕДУЮЩЕЙ СВЯЗИ С ЛОГИКОЙ
                row_squares.append(square) 
                board_layout.addWidget(square, row, col) #ДОБАВЛЕНИЕ КЛЕТОК В РАЗМЕТКУ
            self.squares.append(row_squares) #СОХРАНЕНИЕ В ОБЩИЙ МАССИВ
        
        main_layout.addWidget(board_widget) #СОХРАНЕНИЕ СТРОКИ В ОБЩИЙ МАССИВ
        
        # ПРАВАЯ ЧАСТЬ: ПАНЕЛЬ УПРАВЛЕНИЯ

        panel = QVBoxLayout()
        panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # СТАТУС СЕТИ (только если есть сеть)
        if self.network:
            panel.addWidget(QLabel("Сетевая игра"))
            self.network_status = QLabel("Подключено" if self.network.is_connected() else "Офлайн")
            self.network_status.setStyleSheet("color: gray; font-weight: bold;")
            panel.addWidget(self.network_status)
            
            self.ip_label = QLabel(f"Ваш IP: {self.network.get_local_ip()}")
            panel.addWidget(self.ip_label)
        
        # КНОПКА ВЫХОДА В МЕНЮ (всегда)
        self.menu_btn = QPushButton("🏠 Выйти в меню")
        self.menu_btn.setStyleSheet("background-color: #ffc107; color: black;")
        self.menu_btn.clicked.connect(self.exit_to_menu)
        panel.addWidget(self.menu_btn)
        
        panel.addStretch()
        
        panel_widget = QWidget()
        panel_widget.setLayout(panel)
        panel_widget.setFixedWidth(200)
        main_layout.addWidget(panel_widget)
        
        if self.network:
            self.resign_btn = QPushButton("🏳️ Сдаться")
            self.resign_btn.setStyleSheet("background-color: #dc3545; color: white;")
            self.resign_btn.clicked.connect(self.resign_game)
            panel.addWidget(self.resign_btn)
        
    def check_game_over(self):
        """Проверяет, закончилась ли игра, и обновляет статистику"""
        
        board = self.game.board
        current_color = board.current_player
        if board.is_checkmate(current_color):
            # Определяем победителя (тот, кто НЕ должен ходить, потому что у него мат)
            loser_color = board.current_player
            winner_color = 'black' if loser_color == 'white' else 'white'
            
            # Определяем результат для текущего игрока
            if hasattr(self, 'network') and self.network and self.network.is_connected():
                # Сетевая игра
                if (winner_color == 'white' and self.network.am_i_white) or \
                (winner_color == 'black' and not self.network.am_i_white):
                    result = 'win'
                else:
                    result = 'loss'
                self.update_stats_after_game(result)     
                
            QMessageBox.information(self, "Шах и мат!", f"Победили {winner_color}!")
            self.offer_rematch()
            return True
            
        elif board.is_stalemate(current_color):
            self.update_stats_after_game('draw')
            QMessageBox.information(self, "Пат!", "Ничья!")
            self.offer_rematch()
            return True
            
        return False
    
    
    def resign_game(self):
        """Сдаться в текущей партии"""
        reply = QMessageBox.question(
            self,
            "Сдача",
            "Вы уверены, что хотите сдаться?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Только для сетевой игры
            if hasattr(self, 'network') and self.network and self.network.is_connected():
                result = 'loss'
                self.update_stats_after_game(result)
                
                # Уведомить противника (если метод есть в P2PNetwork)
                if hasattr(self.network, 'send_resign'):
                    self.network.send_resign()
                
                QMessageBox.information(self, "Сдача", "Вы сдались. Противник уведомлён.")
            else:
                QMessageBox.information(self, "Сдача", "В локальной игре статистика не сохраняется.")
            
            # Предложить новую игру
            self.offer_rematch()

    def offer_rematch(self):
        """Предлагает сыграть ещё раз"""
        reply = QMessageBox.question(
            self,
            "Игра окончена",
            "Сыграть ещё раз?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.game.board.reset()
            self.selected_square = None
            self.update_board()
        else:
            self.exit_to_menu()
            
    def on_opponent_resign(self):
        """Противник сдался"""
        self.update_stats_after_game('win')
        QMessageBox.information(self, "Победа!", "Противник сдался!")
        self.offer_rematch()
        
    def update_network_status(self, message):
        """ОБНОВА СТАТУСА СЕТИ"""
        
        self.network_status.setText(message)
        if "ошибка" in message.lower():
            self.network_status.setStyleSheet("color: red; font-weight: bold;")
        elif "подключ" in message.lower():
            self.network_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.network_status.setStyleSheet("color: blue; font-weight: bold;")
    
    def on_opponent_connected(self):
        """ПРОТИВНИК ПОДКЛЛЮЧИЛСЯ"""
        
        self.update_network_status("Противник в игре!")
        
        my_color = "белые" if self.network.am_i_white else "чёрные"
        self.statusBar().showMessage(f"СТОЙ!. ЖДИ ПОКА ПОХОДИТ ПРОТИВНИК.", 3000)
        
        # ОБНОВА СТАТУСА ХОДА
        self.update_turn_status()
        
        QMessageBox.information(self, "Сеть", 
                            f"ЕЕЕ ПРОТИВНИК ПОДКЛЮЧИЛСЯ!!!!!!!!\nТы играешь {my_color}.")
    
    def on_opponent_disconnected(self):
        """ПРОТИВНИК ОТРУБИЛСЯ"""
        
        self.update_network_status("Противник отключился")
        if hasattr(self, 'network') and self.network and self.network.is_connected():
            self.update_stats_after_game('win')
        QMessageBox.warning(self, "Сеть", "Противник отключился. Игра прервана.")
        
    def update_turn_status(self):
        """ПОКАЗЫВАЕТ ЧЕЙ ЩА ХОД"""
        
        if hasattr(self, 'network') and self.network and self.network.is_connected:
            current = self.game.board.current_player
            i_should_move = (current == "white" and self.network.am_i_white) or \
                            (current == "black" and not self.network.am_i_white)
            
            if i_should_move:
                self.statusBar().showMessage(f"ТВОЙ ХОД! ({current})", 2000)
            else:
                self.statusBar().showMessage(f"ЖДИ... Ход {current}", 2000)
        else:
            # ОБЫЧНАЯ ИГРУЛЬКА БЕЗ СЕТИ
            self.statusBar().showMessage(f"Ход: {self.game.board.current_player}", 2000)
    
    def on_network_move(self, from_pos, to_pos):
        """ПОЛУЧЕН ХОД ОТ ПРОТИВНИКА"""
        
        print(f"Получен ход от противника: {from_pos}→{to_pos}")
        success = self.game.board.move_piece(from_pos, to_pos)
        if success:
            self.update_board()
            self.update_turn_status()
            self.statusBar().showMessage(f"Ход противника: {from_pos}→{to_pos}", 2000)
            if self.check_game_over():
                return

    def show_promotion_dialog(self, color):
        """Показывает диалог выбора фигуры"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Превращение пешки")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите фигуру:"))
        
        buttons_layout = QHBoxLayout()
        
        if color == "white":
            pieces = {
                "queen": "♕",
                "rook": "♖",
                "bishop": "♗",
                "knight": "♘"
            }
        else:
            pieces = {
                "queen": "♛",
                "rook": "♜",
                "bishop": "♝",
                "knight": "♞"
            }
        
        selected = [None]
        
        for piece_type, symbol in pieces.items():
            btn = QPushButton(symbol)
            btn.setFixedSize(60, 60)
            btn.setFont(QFont("Segoe UI", 24))
            btn.clicked.connect(lambda checked, pt=piece_type: self.select_piece(pt, dialog, selected))
            buttons_layout.addWidget(btn)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        
        if dialog.exec():
            return selected[0]
        return None

    def select_piece(self, piece_type, dialog, selected):
        """Выбрана фигура"""
        selected[0] = piece_type
        dialog.accept()
    
    def on_square_click(self, row, col):
        """ПЕРЕДАЕМ КООРДИНАТЫ КАК ЕСТЬ"""
        
        print(f"Клик: {row}, {col}")
        
        # ПРОВЕРКА ОЧЕРЕДИ ДЛЯ СЕТЕВОЙ ИГРЫ
        if hasattr(self, 'network') and self.network and self.network.is_connected():
            current = self.game.board.current_player
            i_should_move = (current == "white" and self.network.am_i_white) or \
                            (current == "black" and not self.network.am_i_white)
            
            if not i_should_move: # ПОКАЗЫВАЕТ, ЧТОБЫ ТЫ ПОДОЖДАЛ ПОКА ПОХОДИТ ДРУГОЙ (ДЛЯ СЕТЕВОЙ ИГРЫ)
                print(f"Сейчас ход {current}, жди!")
                self.statusBar().showMessage(f"Сейчас ход {current}, жди!", 2000)
                return
        
        if self.selected_square: #ВЫБРАНА КЛЕТКА
            from_row, from_col = self.selected_square #ЧИСТО БЕРЕМ ПОДСВЕЧЕННУЮ КЛЕТКУ КАК ИСХОДНУЮ ПОЗИЦИЮ
            from_pos = self.index_to_notation(from_row, from_col) #ПЕРЕВОДИМ В ШАХМАТНУЮ НОТАЦИЮ
            to_pos = self.index_to_notation(row, col) #ПЕРЕВОДИМ В ШАХМАТНУЮ НОТАЦИЮ ТАКУЮ ПОЗИЦИЮ, КУДА ХОТИМ ПОХОДИТЬ
            
            success = self.game.board.move_piece(from_pos, to_pos) #УДАЧНЫЙ ХОД
            
            if success: #ЕСЛИ УДАЧНЫЙ ХОД, ТО ОТПРАВЛЯЕМ ХОД СОПЕРНИКУ, УБИРАЕМ ПОДСВЕТКУ КЛЕТКИ И ОБНОВЛЯЕМ ДОСКУ

                # Проверяем превращение
                piece = self.game.board.board[row][col]
                if isinstance(piece, Pawn):
                    if (piece.color == "white" and row == 0) or (piece.color == "black" and row == 7):
                        # Показываем диалог
                        new_piece_type = self.show_promotion_dialog(piece.color)
                        
                        if new_piece_type:
                            # Заменяем пешку
                            if new_piece_type == "queen":
                                self.game.board.board[row][col] = Queen(piece.color)
                            elif new_piece_type == "rook":
                                self.game.board.board[row][col] = Rook(piece.color)
                            elif new_piece_type == "bishop":
                                self.game.board.board[row][col] = Bishop(piece.color)
                            elif new_piece_type == "knight":
                                self.game.board.board[row][col] = Knight(piece.color)
                            self.update_board()
                            
                
                print(f"Ход {from_pos}→{to_pos} успешен!")
                
                if hasattr(self, 'network') and self.network and self.network.is_connected():
                    self.network.send_move(from_pos, to_pos)
                    self.statusBar().showMessage(f"Ход отправлен: {from_pos}→{to_pos}", 2000)
                
                self.selected_square = None
                self.update_board()
                if self.check_game_over():
                    return
             
            else:
                print("Ход невозможен")
                self.selected_square = None
                self.update_board() #ТУТ ПРОСТО ОТМЕНЯЕМ ПОДСВЕТКУ И ВСЕ
                
                piece = self.game.board.board[row][col]
                if piece and piece.color == self.game.board.current_player:
                    self.selected_square = (row, col)
                    self.highlight_square(row, col, True) #Это нужно для того, чтобы ты мог переключаться между своими фигурами одним кликом
        
        else:
            piece = self.game.board.board[row][col]
            if piece and piece.color == self.game.board.current_player:
                self.selected_square = (row, col)
                self.highlight_square(row, col, True) #Тоже самое
            
    def highlight_square(self, row, col, highlight):
        """ПОДСВЕТКА КЛЕТКИ КОТОРУЮ ВЫ ВЫБРАЛИ"""
        
        if highlight:
            self.squares[row][col].setStyleSheet(
                "background-color: yellow; border: 2px solid red; font-size: 40px;"
            )
        else:
            is_light = (row + col) % 2 == 0
            color = "#f0d9b5" if is_light else "#b58863"
            self.squares[row][col].setStyleSheet(
                f"background-color: {color}; border: 1px solid #8b4513; font-size: 40px;"
            )
    
    def update_board(self):
        """ОБНОВА ДОСКИ"""
        
        for row in range(8):
            for col in range(8):
                piece = self.game.board.board[row][col]
                square = self.squares[row][col] #Заново создаем доску
                
                self.highlight_square(row, col, False)
                if piece:
                    square.setText(str(piece)) #Вставляем символ фигуры, если таковая на клетке имеется
                    if piece.color == "white":
                        square.setStyleSheet(
                            square.styleSheet() + "color: white;"
                        )
                    else:
                        square.setStyleSheet(
                            square.styleSheet() + "color: black;"
                        )
                else:
                    square.setText("")
        self.update_turn_status() #Ну и показываем чей ход
    
    def index_to_notation(self, row, col):
        col_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        return f"{col_letters[col]}{8 - row}"