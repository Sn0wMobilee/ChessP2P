'''ПРЕОБРАЗОВАНИЕ ШАХМАТНОЙ НОТАЦИИ В ИНДЕКСЫ ДОСКИ'''
def notation_to_index(position):
    cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7,}
    if len(position) != 2:
        return None
    col_char, row_char = position[0].lower(), position[1]
    if col_char not in cols or not row_char.isdigit():
        return None
    col = cols[col_char]
    row = 8 - int(row_char)
    return (row, col)

'''ОБРАТНОЕ ПРЕОБРАЗОВАНИЕ'''
def index_to_notation(row,col):
    col_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    return f"{col_map[col]}{8 - row}"