from .base import ChessPiece

class Knight(ChessPiece): #создание класса коня
    def __init__(self, color): #параметр цвета
        symbol = "♘" if color == "white" else "♞" #присвоение символа в зависимости от цвета фигуры
        super().__init__(color,symbol) #наследование параметров род. класса
        self.piece_type = 'knight' #присвоение типа фигуры
          
        '''ХОДЫ КОНЯ'''
    def get_attacking_squares(self, position, board): #метод для нахождения всех клеток, на которые может походить фигура без учета шаха
        return self.get_possible_moves(position, board, None) #выбрасывание результата наружу
      
    def get_possible_moves(self, position, board_obj, last_move_info = None): #метод для нахождения всех клеток, на которые может походить фигура с учетом щаха
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        knight_possible_moves = [] #список возможных ходов коня
        possible_positions = [
        (row + 2, col + 1), (row + 2, col - 1),
        (row - 2, col + 1), (row - 2, col - 1),
        (row + 1, col + 2), (row + 1, col - 2),
        (row - 1, col + 2), (row - 1, col - 2)
        ] #позиции на которые может сдвинуться конь
        for r, c in possible_positions: #r - влево-вправо, с - вверх-вниз
            if 0 <= r < 8 and 0 <= c < 8: #проверка чтобы фигура не вылетела за доску
                target_piece = board_obj.board[r][c] #проверка на наличие цели
                if target_piece is None or target_piece.color != self.color: #если цель вражеская или ее нет то можна
                    knight_possible_moves.append((r, c))
        return knight_possible_moves