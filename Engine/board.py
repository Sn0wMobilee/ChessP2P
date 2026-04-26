from .pieces import *
from .utils import notation_to_index, index_to_notation

class ChessBoard:
    '''ШАХМАТНАЯ ДОСКА'''
    def __init__(self):
        self.board = self.create_initial_board() #атрибут - сама доска
        self.current_player = "white" #атрибут - Первый текущий игрок
        self.game_over = False #атрибут - Игра еще не закончена
        self.last_move = None #атрибут - последнего хода еще нет
        self.last_move_pawn_double = False #атрибут - последний ход - двойной ход пешкой не выполнен еще
        self.half_moves = 0 #счетчик полуходов
        
    """СОЗДАНИЕ ШАХМАТНОЙ ДОСКИ С НАЧАЛЬНОЙ РАССТАНОВКОЙ ФИГУР"""
    def create_initial_board(self):
        board = [[None for _ in range(8)] for _ in range(8)] #создание пустого списка списков 8x8         
        for col in range(8): #col - столбец. В шахматной доске 8 столбцов
            board[6][col] = Pawn('white') #на 2-й горизонтали белые пешки (пишет 6, потому что списки идут снизу вверх по счету от 0 до 7)
            board[1][col] = Pawn('black') #на 7-й горизонтали белые пешки
        pieces_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook] #это порядок объектов фигур
        for col, piece_class in enumerate(pieces_order): #перебор и нумерация порядка фигур
            board[7][col] = piece_class('white') #на самой нижней горизонтали белые фигуры
            board[0][col] = piece_class('black') #на самой верхней горизонтали белые фигуры
        return board
    
    """ПРОВЕРКА АТАКОВАННЫХ КЛЕТОК"""
    def square_is_under_attack(self, square, attacker_color): #метод для определения атакована ли клетка
        target_row, target_col = square #клетка которую будем проверять. Называется target, так как это клетка, на которую хотим пойти
        for row in range(8): #8 рядов
            for col in range(8): #8 столбцов
                piece = self.board[row][col] #перебор всех клеток
                if piece and piece.color == attacker_color: #если на клетке есть фигура и ее цвет вражеский
                    attacking_squares = piece.get_attacking_squares((row,col), self) #получение всех клеток, которые может проатаковать фигура без учета шаха (row,col - позиция)
                    for r, c in attacking_squares: #r - ряд, c - столбец
                        if 0 <= r < 8 and 0 <= c < 8: #чтобы не вылезало за пределы доски
                            if r == target_row and c == target_col: #если координаты на которые ты хочешь походить под боем вражеских фигур
                                return True #значит square is under attack
        return False #если нет то они не проатакованы
    
    """ПУБЛИЧНАЯ ПРОВЕРКА НА ВОЗМОЖНОСТЬ КОРОТКОЙ РОКИРОВКИ"""
    def can_castle_kingside(self, king_position, king_color): #это нужно для того чтобы не возникло лишних ошибок при вызове основного метода
        row, col = king_position #позиция
        king = self.board[row][col] #фигура
        if not king or not isinstance(king, King) or king.color != king_color: #если это не король или он не того цвета
            return False #незя
        return king._can_castle_kingside(king_position, self) #или можно если все подходит
    
    """ПУБЛИЧНАЯ ПРОВЕРКА НА ВОЗМОЖНОСТЬ ДЛИННОЙ РОКИРОВКИ"""
    def can_castle_queenside(self, king_position, king_color): #то же самое
        row, col = king_position
        king = self.board[row][col]
        if not king or not isinstance(king, King) or king.color != king_color:
            return False
        return king._can_castle_queenside(king_position, self)

    
    '''НАЙТИ КОРОЛЯ'''
    def find_king_position(self,color): #просто найти короля
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece and  
                   isinstance(piece, King) and
                    piece.color == color):
                    return (row,col)
        raise Exception(f"Король цвета {color} не найден!")
    
    '''НАЙТИ ВОЗМОЖНЫЕ ХОДЫ ПРОТИВНИКА'''
    def find_opponent_possible_moves(self,color):
        opponent_possible_moves = []
        opponent_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = piece.get_possible_moves((row, col), self, self.last_move)
                    opponent_possible_moves.extend(moves)
        return opponent_possible_moves
    
    def find_opponent_attacking_squares(self,color):
        opponent_attacking_squares = []
        opponent_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = piece.get_attacking_squares((row, col), self)
                    opponent_attacking_squares.extend(moves)
        return opponent_attacking_squares
    
    '''ПРОВЕРКА НА ШАХ'''
    def is_in_check(self, color):
        king_position = self.find_king_position(color)
        opponent_moves = self.find_opponent_attacking_squares(color)
        return king_position in opponent_moves
    
    '''ПРОВЕРКА НА МАТ'''
    def is_checkmate(self,color):
        if not self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = piece.get_possible_moves((row, col), self, self.last_move)
                    for move_row, move_col in moves:
                        if not (0 <= move_row < 8 and 0 <= move_col < 8):
                            continue
                        saved_piece = self.board[move_row][move_col]
                        self.board[move_row][move_col] = piece
                        self.board[row][col] = None
                        still_in_check = self.is_in_check(color)
                        self.board[row][col] = piece
                        self.board[move_row][move_col] = saved_piece
                        if not still_in_check:
                            return False
        return True

    '''ПРОВЕРКА НА ПАТ'''        
    def is_stalemate(self,color):
        if self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = piece.get_possible_moves((row, col), self, self.last_move)
                    for move_row, move_col in moves:
                        if not (0 <= move_row < 8 and 0 <= move_col < 8):
                            continue
                        target_piece = self.board[move_row][move_col]
                        self.board[move_row][move_col] = piece
                        self.board[row][col] = None
                        creates_check = self.is_in_check(color)
                        self.board[row][col] = piece
                        self.board[move_row][move_col] = target_piece
                        if not creates_check:
                            return False
    def not_enough_pieces(self):
        white_pawn_counter = 0
        black_pawn_counter = 0
        white_knight_counter = 0
        black_knight_counter = 0
        white_bishop_whitefielded_counter = 0
        white_bishop_blackfielded_counter = 0
        black_bishop_whitefielded_counter = 0
        black_bishop_blackfielded_counter = 0
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece,Queen) or isinstance(piece,Rook):
                    return False
                if isinstance(piece, Pawn) and piece.color == 'white':
                    white_pawn_counter += 1
                if isinstance(piece, Pawn) and piece.color == 'black':
                    black_pawn_counter += 1
                if isinstance(piece, Knight) and piece.color == 'white':
                    white_knight_counter += 1
                if isinstance(piece, Knight) and piece.color == 'black':
                    black_knight_counter += 1
                if isinstance(piece, Bishop) and piece.color == 'white':
                    is_dark_square =  (row + col) % 2 == 1
                    if is_dark_square:
                        white_bishop_blackfielded_counter += 1
                    else:
                        white_bishop_whitefielded_counter += 1          
                if isinstance(piece, Bishop) and piece.color == 'black':
                    is_dark_square =  (row + col) % 2 == 1
                    if is_dark_square:
                        black_bishop_blackfielded_counter += 1
                    else:
                        black_bishop_whitefielded_counter += 1
                        
        white_bishop_counter = white_bishop_whitefielded_counter + white_bishop_blackfielded_counter
        black_bishop_counter = black_bishop_whitefielded_counter + black_bishop_blackfielded_counter  
                     
        if white_knight_counter >= 1 and white_bishop_counter >= 1 or black_knight_counter >= 1 and black_bishop_counter >= 1:
            return False
        if white_bishop_counter >= 2 or black_bishop_counter >= 2:
            return False
        if white_pawn_counter >= 1 or black_pawn_counter >= 1:
            return False
        if white_bishop_blackfielded_counter >= 1 and black_bishop_whitefielded_counter >= 1:
            return False
        if white_bishop_whitefielded_counter >= 1 and black_bishop_blackfielded_counter >= 1:
            return False  
        return True
                      

    '''ПЕРЕМЕЩЕНИЕ ФИГУРЫ'''
    def move_piece(self, from_pos, to_pos):
        if self.game_over:
            print("Игра завершена!")
            return False
        # ПРЕОБРАЗУЕМ НОТАЦИЮ В ИНДЕКСЫ
        from_idx = notation_to_index(from_pos)
        to_idx = notation_to_index(to_pos)
        if not from_idx or not to_idx:
            print("Неверный формат координат!")
            return False

        row_from, col_from = from_idx
        row_to, col_to = to_idx
        
        #БАЗОВЫЕ ПРОВЕРКИ
        piece = self.board[row_from][col_from]
        if piece is None:
            print(f"На позиции {from_pos} нет фигуры!")
            return False
        
        if piece.color != self.current_player:
            print(f"Сейчас ходят {self.current_player}, а не {piece.color}")
            return False
        
        possible_moves = piece.get_possible_moves((row_from, col_from), self, self.last_move)
        if (row_to, col_to) not in possible_moves:
            print("Этот ход запрещен! Походите как-нибудь по другому")
            return False
    
        #ОБРАБОТКА ВЗЯТИЯ НА ПРОХОДЕ
        is_en_passant = False
        captured_row, captured_col = None,None
        if isinstance(piece, Pawn):
            if (self.board[row_to][col_to] is None and
                col_to != col_from and
                abs(col_to - col_from) == 1):
                
                if (self.last_move and
                self.last_move.get('was_pawn_double') and
                self.last_move.get('piece') and               
                isinstance(self.last_move['piece'], Pawn)):    
                    
                    last_to = self.last_move.get('to')
                    last_from = self.last_move.get('from')
                    if (last_to[0] == row_from and
                        last_to[1] == col_to):           
                        if piece.color == 'white' and row_from == 3 and row_to == 2:
                            is_en_passant = True       
                            captured_row, captured_col = row_from, col_to
                        elif piece.color == 'black' and row_from == 4 and row_to == 5:
                            is_en_passant = True
                            captured_row, captured_col = row_from, col_to
                            
        original_target = self.board[row_to][col_to]
        captured_piece = None
        if is_en_passant:
            captured_row = row_from
            captured_col = col_to
            captured_piece = self.board[captured_row][captured_col]
            self.board[captured_row][captured_col] = None
            
        #ОБРАБОТКА РОКИРОВКИ
        is_castling = isinstance(piece, King) and abs(col_to - col_from) == 2
        saved_state = {
        'king_from': piece,
        'king_to_cell': self.board[row_to][col_to],
        }
        if is_castling:
            if col_to > col_from:
                saved_state['rook'] = self.board[row_from][7]
                saved_state['rook_from_col'] = 7
                saved_state['rook_to_col'] = col_to - 1
            else:
                saved_state['rook'] = self.board[row_from][0]
                saved_state['rook_from_col'] = 0
                saved_state['rook_to_col'] = col_to + 1
        self.board[row_to][col_to] = piece
        self.board[row_from][col_from] = None
        if is_castling:
            rook = saved_state['rook']
            rook_to_col = saved_state['rook_to_col']
            rook_from_col = saved_state['rook_from_col']
            self.board[row_from][rook_to_col] = rook
            self.board[row_from][rook_from_col] = None

        #ОБРАБОТКА ШАХА
        self.board[row_to][col_to] = piece
        self.board[row_from][col_from] = None
        if self.is_in_check(piece.color):
              #ОТКАТЫВАЕМ ХОД
            self.board[row_from][col_from] = saved_state['king_from']
            self.board[row_to][col_to] = saved_state['king_to_cell']
            #ЕСЛИ ВЗЯТИЕ НА ПРОХОДЕ
            if is_en_passant:
                self.board[captured_row][captured_col] = captured_piece
            #ЕСЛИ РОКИРОВКА   
            if is_castling:
                self.board[row_from][saved_state['rook_from_col']] = saved_state['rook']
                self.board[row_from][saved_state['rook_to_col']] = None
            print("Оставлять короля под боем нельзя!!")
            return False
        
        #ЕСЛИ ВСЕ УСЛОВИЯ ВЕРНЫ
        piece.has_moved = True
        
        #СОХРЯНЕМ ИНФОРМАЦИЮ О ПОСЛЕДНЕМ ХОДЕ ДЛЯ ВЗЯТИЯ НА ПРОХОДЕ
        self.last_move = {
        'from': (row_from, col_from),
        'to': (row_to, col_to),
        'piece': piece,
        'was_pawn_double': False
        }
        
        #ЕСЛИ РОКИРОВКА ТО ФИКСИРУЕМ has_moved ДЛЯ ЛАДЬИ
        if is_castling:
            rook_piece = self.board[row_from][saved_state['rook_to_col']]
            rook_piece.has_moved = True
            print(f"Рокировка {'короткая' if col_to > col_from else 'длинная'} успешна!")
            
        #ВЗЯТИЕ ФИГУРЫ
        if isinstance(piece, Pawn) and abs(row_to - row_from) == 2:
            self.last_move['was_pawn_double'] = True
            print(f"Последний ход (Откуда-куда) - {from_pos} {to_pos}")
        if is_en_passant:
            print(f"Взятие на проходе! Захвачена пешка на {index_to_notation(captured_row, captured_col)}!")
        elif original_target:
            print(f"Захвачена фигура {original_target.symbol} на {to_pos}!")    

        opponent_color = "black" if piece.color == "white" else "white"
        opponent_colors = {"black": "чёрных", "white": "белых",}
        winner_colors = {"black": "чёрные", "white": "белые",}
        
        #ОБЪЯВЛЕНИЕ ШАХА КОРОЛЮ
        if self.is_in_check(opponent_color):
            print(f"ШАХ королю {(opponent_colors.get(opponent_color))}!")
            
            #ОБЪЯВЛЕНИЕ МАТА
            if self.is_checkmate(opponent_color):
                winner_colors = {"black": "чёрные", "white": "белые"}
                print(f"МАТ королю {opponent_colors.get(opponent_color)}! Победитель - {winner_colors.get(piece.color)}!")
                self.game_over = True
            
        #ОБЪЯВЛЕНИЕ ПАТА
        elif self.is_stalemate(opponent_color):
            print(f"Пат! На доске возникла ничья!")
            self.game_over = True

        #НЕДОСТАТОЧНО МАТЕРИАЛА
        if self.not_enough_pieces():
            print(f"Недостаточно материала. На доске возникла ничья!")
            self.game_over = True
            
        #ПРАВИЛО 50 ХОДОВ
        if isinstance(piece, Pawn) or original_target is not None:
            self.half_moves = 0
            print(f"Количество полу-ходов: {self.half_moves}")
        else:
            self.half_moves += 1
            print(f"Количество полу-ходов: {self.half_moves}")
        if self.half_moves == 100:
            print(f"Правило 50 ходов. Ни одной взятой фигуры или хода пешкой. На доске возникла ничья!")
            self.game_over = True 
            
            #ПРЕВРАЩЕНИЕ ПЕШКИ
        # if isinstance(piece, Pawn):
        #     if (piece.color == "white" and row_to == 0) or (piece.color == "black" and row_to == 7):
        #         while True:
        #             choice = input("Пешка дошла до конца! Какой фигурой вы бы хотели заменить пешку? (queen, rook, knight, bishop)")
        #             if choice.lower() == "queen":
        #                 self.board[row_to][col_to] = Queen(piece.color)
        #                 print("ПЕШКА ПРЕВРАТИЛАСЬ В ФЕРЗЯ")
        #                 break
        #             elif choice.lower() == "rook":
        #                 self.board[row_to][col_to] = Rook(piece.color)
        #                 print("ПЕШКА ПРЕВРАТИЛАСЬ В ЛАДЬЮ")
        #                 break
        #             elif choice.lower() == "knight":
        #                 self.board[row_to][col_to] = Knight(piece.color)
        #                 print("ПЕШКА ПРЕВРАТИЛАСЬ В КОНЯ")
        #                 break
        #             elif choice.lower() == "bishop":
        #                 self.board[row_to][col_to] = Bishop(piece.color)
        #                 print("ПЕШКА ПРЕВРАТИЛАСЬ В СЛОНА")
        #                 break
        #             else:
        #                 print("Неверный выбор")
                        
            #СМЕНА ИГРОКОВ   
        self.current_player = "black" if self.current_player == "white" else "white"
        print(f"Ход: {piece.symbol} с {from_pos} на {to_pos}")
        return True
    
    '''ОТОБРАЖЕНИЕ ДОСКИ'''
    def display(self):
        print("\n   A  B  C  D  E  F  G  H")
        print("  +-------------------------")
        for row in range(8):
            print(f"{8-row} |", end="")
            for col in range(8):
                piece = self.board[row][col]
                symbol = piece.symbol if piece else '·'
                print(f" {symbol}", end=" ")
            print(f"| {8-row}")
        print("  +-------------------------")
        print("   A  B  C  D  E  F  G  H")
        