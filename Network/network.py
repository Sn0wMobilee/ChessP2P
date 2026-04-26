import socket
import pickle
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

class P2PNetwork(QObject):
    """СИГНАЛЫ ДЛЯ СВЯЗИ С GUI"""
    
    move_received = pyqtSignal(str, str)      # (from_pos, to_pos)
    opponent_connected = pyqtSignal()
    opponent_disconnected = pyqtSignal()
    status_message = pyqtSignal(str)
    resign_received = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.connection = None
        self.is_host = False
        self.connected = False
        self.server = None
        self.am_i_white = None
        self.opponent_color = None

    def host_game(self, port=5555):
        """СОЗДАТЬ ИГРУ (БЫТЬ СЕРВЕРОМ)"""
        
        self.am_i_white = True
        self.opponent_color = "black"
        print(f"ХОСТ: я белый, противник чёрный")
        try:
            self.is_host = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', port))
            self.server.listen(1)
            self.status_message.emit(f"Ожидание игрока на порту {port}...")
    
            self.status_message.emit(f"Ожидание игрока на порту {port}...")
            threading.Thread(target=self._accept_connection, daemon=True).start()
            return True
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")
            return False

    def join_game(self, ip, port=5555):
        """ПОДКЛЮЧИТЬСЯ К ИГРЕ"""
        
        try:
            self.is_host = False
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((ip, port))
            
            #ПОЛУЧАЕМ СВОЙ ЦВЕТ ОТ СЕРВЕРА
            data = self.connection.recv(1024)
            color_info = pickle.loads(data)
            self.am_i_white = (color_info["your_color"] == "white")
            print(f"КЛИЕНТ: я {'белый' if self.am_i_white else 'черный'}")
            
            self.connected = True
            threading.Thread(target=self._listen, daemon=True).start()
            self.opponent_connected.emit()
            self.status_message.emit("Подключено к игре!")
            return True
        except Exception as e:
            self.status_message.emit(f"Ошибка подключения: {e}")
            return False

    def _accept_connection(self):
        try:
            self.connection, addr = self.server.accept()
            print(f"Подключение от {addr}")
            
            # Добавляем type
            color_data = pickle.dumps({"type": "color_info", "your_color": "black"})
            self.connection.send(color_data)
            
            self.connected = True
            threading.Thread(target=self._listen, daemon=True).start()
            self.opponent_connected.emit()
            self.status_message.emit(f"Противник подключился!")
        except Exception as e:
            print(f"Ошибка при принятии: {e}")
                
    def _listen(self):
        """СЛУШАТЬ ВХОДЯЩИЕ СООБЩЕНИЯ"""
        
        print(f"Запуск слушателя для {'хост' if self.is_host else 'клиент'}")
        while self.connected:
            try:
                self.connection.settimeout(1.0)
                data = self.connection.recv(1024)
                if not data:
                    print("Соединение закрыто")
                    break
                
                # ПРОВЕРКА НЕ СЛУЖЕБНРЕ ЛИ СООБЩЕНИЕ
                try:
                    msg = pickle.loads(data)
                    # ЕСОИ ЭТО СЛОВАРЬ С КЛЮЧОМ 'type' ТО ЭТО СЛУЖЕБНОЕ СООБЩЕНИЕ
                    if isinstance(msg, dict) and 'type' in msg:
                        if msg['type'] == 'color_info':
                            print(f"Получена информация о цвете: {msg}")
                            continue
                        elif msg['type'] == 'resign':
                            print("Противник сдался")
                            self.resign_received.emit()
                            continue
                    else:
                        # Это ход
                        from_pos, to_pos = msg
                        print(f"Получен ход: {from_pos}→{to_pos}")
                        self.move_received.emit(from_pos, to_pos)
                except:
                    pass
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Ошибка при получении: {e}")
                break
        
        print("Слушатель остановлен")
        self.connected = False
        self.opponent_disconnected.emit()

    def send_move(self, from_pos, to_pos):
        """ОТПРАВИТЬ ХОД"""
        
        if self.connection and self.connected:
            try:
                data = pickle.dumps((from_pos, to_pos))
                self.connection.send(data)
                return True
            except:
                self.connected = False
                return False
        return False

    def disconnect(self):
        """ОТКЛЮЧИЛСЯ"""
        
        self.connected = False
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
            
    def send_resign(self):
        """Отправить уведомление о сдаче"""
        if self.connection and self.connected:
            try:
                data = pickle.dumps({"type": "resign"})
                self.connection.send(data)
                return True
            except:
                return False
                   
    def get_local_ip(self):
        """УЗНАТЬ СВОЙ IP В ЛОКАЛЬНОЙ СЕТИ"""
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
        
    def is_connected(self):
        return self.connected
    
    def on_opponent_connected(self):
        """ПРОТИВНИК ПОДКЛЮЧИЛСЯ"""
        
        if self.network.am_i_white:
            QMessageBox.information(self,"Сеть", "Ты играешь белыми")
        else:
            QMessageBox.information(self,"Сеть", "Ты играешь черными")
        self.update_network_status("Противник в игре!")
        
        my_color = "белые" if self.network.am_i_white else "чёрные"
        self.statusBar().showMessage(f"Ты играешь {my_color}. Жди своего хода.", 3000)
        
        self.update_turn_status()
        
        QMessageBox.information(self, "Сеть", 
                            f"Противник подключился!\nТы играешь {my_color}.")