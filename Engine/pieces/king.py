from .base import ChessPiece
from .rook import Rook

class King(ChessPiece): #создание класса короля
    def __init__(self, color,): #параметр цвета
        symbol = "♔" if color == "white" else "♚" #присвоение символа в зависимости от цвета фигуры
        super().__init__(color, symbol) #наследование параметров род. класса
        self.piece_type = 'king' #присвоение типа фигуры
        
    """ПРОВЕРКА НА ВОЗМОЖНОСТЬ КОРОТКОЙ РОКИРОВКИ"""
    def _can_castle_kingside(self, position, board_obj, last_move_info=None): #параметры: текущая позиция, объект доски, информация о последнем ходе
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        rook = board_obj.board[row][7] # обязательно ладья должна быть в правом нижнем углу
        if self.has_moved: 
            return False #если король подвинулся - незя
        if not rook or not isinstance(rook,Rook) or rook.has_moved:
            return False #если нет ладьи или это не ладья или ладья подвинулась - незя
        if board_obj.board[row][5] is not None or board_obj.board[row][6] is not None: #если клетки между ладьей и королем заняты - незя
                return False
        if board_obj.is_in_check(self.color):
                return False #если шах - незя
        opponent_color = 'black' if self.color == 'white' else 'white' #если собственный цвет - белый то цвет противника черный, и наоборот
        squares_to_check = [(row, col), (row, col + 1), (row, col + 2)] #проверка клеток между ладьей и королем
        for square in squares_to_check: #перебор каждой клетки
            if board_obj.square_is_under_attack(square, opponent_color): #если клетки под атакой противника:
                return False #НЕЗЯ
        return True #если все подходит то можно
    
    """ПРОВЕРКА НА ВОЗМОЖНОСТЬ ДЛИННОЙ РОКИРОВКИ"""
    def _can_castle_queenside(self,position, board_obj, last_move_info=None):
        row, col = position 
        rook = board_obj.board[row][0] # обязательно ладья должна быть в правом верхнем углу
        if self.has_moved:
            return False  
        if not rook or not isinstance(rook,Rook) or rook.has_moved:
            return False 
        if board_obj.board[row][1] is not None or board_obj.board[row][2] is not None or board_obj.board[row][3] is not None:
                return False
        if board_obj.is_in_check(self.color):
                return False
        opponent_color = 'black' if self.color == 'white' else 'white'
        squares_to_check = [(row, col), (row, col - 1), (row, col - 2),]
        for square in squares_to_check:
            if board_obj.square_is_under_attack(square, opponent_color):
                return False
        return True
        
        '''ХОДЫ КОРОЛЯ'''
    def get_attacking_squares(self, position, board): #куда же может просто в теории пойти король без учета шаха?
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        king_attacking_squares = [] #список возможных ходов короля
        possible_positions = [
        (row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1),
        (row - 1, col + 1), (row + 1, col - 1), (row - 1, col - 1), (row + 1, col + 1),
        ] #позиции на которые может сдвинуться король
        for r, c in possible_positions: #r - влево-вправо, с - вверх-вниз
            if 0 <= r < 8 and 0 <= c < 8: #проверка чтобы фигура не вылетела за доску
                king_attacking_squares.append((r, c)) #если все подходит то добавляем возможные ходы в список
        return king_attacking_squares #выбрасываем наружу
    
    def get_possible_moves(self, position, board_obj, last_move_info=None): #куда же может просто в теории пойти король с учетом шаха и др правил?
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        king_filtered_moves = [] #список возможных ОТФИЛЬТРОВАННЫХ ходов короля
        possible_positions = [
        (row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1),
        (row - 1, col + 1), (row + 1, col - 1), (row - 1, col - 1), (row + 1, col + 1),
        ] #позиции на которые может сдвинуться король
        for r, c in possible_positions: #r - влево-вправо, с - вверх-вниз
            if 0 <= r < 8 and 0 <= c < 8: #проверка чтобы фигура не вылетела за доску
                target_piece = board_obj.board[r][c] #проверка на наличие цели
                if target_piece is None or target_piece.color != self.color: #если противник есть или нету фигуры то можно походить
                    king_filtered_moves.append((r, c))
        if not self.has_moved:
            if board_obj.can_castle_kingside(position, self.color):
                king_filtered_moves.append((position[0], position[1] + 2)) #если не походил то открыта возможность для короткой рокировочки
            if board_obj.can_castle_queenside(position, self.color):
                king_filtered_moves.append((position[0], position[1] - 2)) #тоже самое для длинной
        return king_filtered_moves 