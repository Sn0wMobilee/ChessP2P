from .base import ChessPiece

class Pawn(ChessPiece): #создание класса пешки
    def __init__(self, color): #присвоение параметра - цвет
        symbol = "♙" if color == "white" else "♟" #присвоение символа в зависимости от цвета фигуры
        super().__init__(color, symbol) #наследование параметров род. класса
        self.piece_type = 'pawn'  #присвоение типа фигуры
        
    def get_attacking_squares(self, position, board):  #метод для нахождения всех клеток, на которые может походить фигура без учета шаха
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        squares = [] #список возможных ходов коня
        direction = -1 if self.color == 'white' else 1 #определение куда походит пешка в зависимости от цвета (вверх или вниз)
        for diogonal in [-1, 1]: #по диогонали если есть кого сожрать
            new_col = col + diogonal #итоговая позиция
            if 0 <= new_col < 8 and 0 <= row + direction < 8: #проверка чтобы не вылетело за доску
                squares.append((row + direction, new_col)) #добавление позиции если все сходится
        return squares
                    
    def get_possible_moves(self, position, board_obj, last_move_info = None): #метод для нахождения всех клеток, на которые может походить фигура с учетом щаха
        """Логика ходов пешки"""  
        row, col = position #row - строка, col - столбец. В итоге [row][col] - позиция клетки
        pawn_possible_moves = [] #список возможных ходов коня
        
        '''ПРОСТОЕ ПЕРЕМЕЩЕНИЕ'''   
        direction = -1 if self.color == 'white' else 1 #определение куда походит пешка в зависимости от цвета (вверх или вниз)
        if 0 <= row + direction < 8 and board_obj.board[row + direction][col] is None: #чтоб не вылетело за доску и не могла срубить вперед
            pawn_possible_moves.append((row + direction, col))
            if not self.has_moved and 0 <= row + 2*direction < 8 and board_obj.board[row + 2*direction][col] is None: #если не переместилась то можно пойти на 2 клетки вперед
                pawn_possible_moves.append((row + 2*direction, col))
                
        '''ОБЫЧНОЕ ВЗЯТИЕ'''          
        for diogonal in [-1, 1]: #диогональ
            new_col = col + diogonal #итоговая позиция
            if 0 <= new_col < 8 and 0 <= row + direction < 8: #чтоб не вылетело за доску
                target_piece = board_obj.board[row + direction][new_col] #проверка на наличие враж. фигуры
                if target_piece is not None and target_piece.color != self.color: #если она есть...
                    pawn_possible_moves.append((row + direction, new_col)) #срубить
                    
        '''ВЗЯТИЕ НА ПРОХОДЕ'''            
        if last_move_info and last_move_info.get('was_pawn_double', False): #пешка не должна походить на две клетки вперед
            last_piece = last_move_info.get('piece') #получить последнюю походившую фигуру
            last_to = last_move_info.get('to') #проверить куда она походила
            last_from = last_move_info.get('from') #проверить откуда она походила
            if last_to and last_piece and isinstance(last_piece, Pawn): #если фигура походила и это пешка
                target_row, target_col = last_to #то куда походила последняя фигура и будет позиция на которую встанет пешка
                if target_row == row and abs(target_col - col) == 1: #если расстояние между столбцами 2 фигур = 1 и они на одном ряду
                    if self.color == 'white': #если твоя пешка белая
                        if row == 3 and last_from[0] == 1 and last_to[0] == 3: #если это ряд 5
                            pawn_possible_moves.append((row - 1, target_col)) #добавить
                    elif self.color == 'black': #если твоя пешка черная
                        if row == 4 and last_from[0] == 6 and last_to[0] == 4: #если это ряд 4
                            pawn_possible_moves.append((row + 1, target_col)) #добавить

        return pawn_possible_moves