from .board import ChessBoard
'''КЛАСС ПРОЦЕССОВ ИГРЫ'''
class Game:
    def __init__(self):
        self.board = ChessBoard()
        self.game_over = False
        self.player_names = {
            "white": "БЕЛЫЕ",
            "black": "ЧЕРНЫЕ"
        }
        
    '''ПОКАЗЫВАЕТ ЧЕЙ ХОД НА ДАННЫЙ МОМЕНТ'''
    def show_current_player_turn(self):
        player = self.player_names[self.board.current_player]
        print(f"[{player}],Сейчас ваш ход!")
    
    '''НАЧАЛО ИГРЫ'''    
    def play(self):
        print("   Добро пожаловать в игру!")
        #ПОТОМ ТУТ БУДУТ РАЗНЫЕ РЕЖИМЫ
        while True:
            if self.board.game_over:
                self.board.display()
                print("Игра завершена!")
                choice = input("Хотите сыграть еще раз? (да/нет): ")
                if choice.lower() == "да":
                    self.board = ChessBoard()
                    continue
                else:
                    break
                
            #ОТОБРАЖЕНИЕ ДОСКИ    
            self.board.display()    
            self.show_current_player_turn()
            move = input("Введите ход (например, e2 e4) или выход для завершения:")
            if move.lower() == 'выход':
                print("Игра завершена")
                break
            
            #ПРОВЕРЯЕТ ЧТОБЫ ДЛИНА ШАХМАТНЫХ НОТАЦИЙ БЫЛА ОБЯЗАТЕЛЬНО = 2
            parts = move.split()
            if len(parts) != 2:
                print("Формат: 'откуда куда', например: 'e2 e4'")
                continue
            
            #ВЫПОЛНЕНИЕ ХОДА
            if self.board.move_piece(parts[0], parts[1]):
                print("Ход выполнен!")
            else:
                print("Не удалось выполнить ход. Попробуйте снова.")