from .base import ChessPiece #импортируем базовый класс

class Bishop(ChessPiece): #создание класса слона
    def __init__(self, color): #параметр цвета
        symbol = "♗" if color == "white" else "♝" #присвоение символа в зависимости от цвета фигуры
        super().__init__(color, symbol) #наследование параметров род. класса
        self.piece_type = 'bishop' #присвоение типа фигуры
        
    def get_attacking_squares(self, position, board): #метод для нахождения всех клеток, на которые может походить фигура без учета шаха
        return self.get_possible_moves(position, board, None) #выбрасывание результата наружу
    
    """ХОДЫ СЛОНА"""
    def get_possible_moves(self, position, board_obj,  last_move_info = None): #метод для нахождения всех клеток, на которые может походить фигура с учетом щаха
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        bishop_possible_moves = [] #список возможных ходов слона
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)] #позиции на которые может сдвинуться слон
        for dr, dc in diagonals: #dr - первый элемент позиции перемещения (влево-вправо), dc - второй элемент позиции перемещения (вверх-вниз)
            r, c = row + dr, col + dc #r, c - итоговые позиции перемещения
            while 0 <= r < 8 and 0 <= c < 8: #чтобы не вылазело за доску
                target = board_obj.board[r][c] if hasattr(board_obj, 'board') else board_obj[r][c] #проверка на наличие цели
                if target is None:
                    bishop_possible_moves.append((r, c)) #просто свободная клетка
                elif target.color != self.color:
                    bishop_possible_moves.append((r, c)) #если враг - срубить >:(
                    break #конец цикла
                else:
                    break #конец цикла
                r += dr
                c += dc
        return bishop_possible_moves #выбрасывание списка наружу