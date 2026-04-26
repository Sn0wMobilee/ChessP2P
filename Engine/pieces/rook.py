from .base import ChessPiece

class Rook(ChessPiece): #создание класса ладьи
    def __init__(self, color): #создание параметра цвета 
        symbol = "♖" if color == "white" else "♜" #присвоение символа в зависимости от цвета фигуры
        super().__init__(color,symbol) #наследование параметров род. класса
        self.piece_type = 'rook' #присвоение типа фигуры
        
    def get_attacking_squares(self, position, board):  #метод для нахождения всех клеток, на которые может походить фигура без учета шаха
        return self.get_possible_moves(position, board, None) #выбрасывание результата наружу
    
    """ХОДЫ ЛАДЬИ"""   
    def get_possible_moves(self, position, board_obj, last_move_info = None):  #метод для нахождения всех клеток, на которые может походить фигура с учетом щаха
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        rook_possible_moves = [] #список возможных ходов ладьи
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] #позиции на которые может сдвинуться ладья
        for dr, dc in directions: #dr - первый элемент позиции перемещения (влево-вправо), dc - второй элемент позиции перемещения (вверх-вниз)
            r, c = row + dr, col + dc #r, c - итоговые позиции перемещения
            while 0 <= r < 8 and 0 <= c < 8: #чтобы не вылазело за доску
                target = board_obj.board[r][c] if hasattr(board_obj, 'board') else board_obj[r][c] #проверка на наличие цели
                if target is None:
                    rook_possible_moves.append((r, c)) #просто свободная клетка
                elif target.color != self.color:
                    rook_possible_moves.append((r, c)) #если враг - срубить >:(
                    break #прервать цикл
                else:
                    break #прервать цикл
                r += dr
                c += dc
        return rook_possible_moves
