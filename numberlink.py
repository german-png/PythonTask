from collections import Counter

def parsing_coordinates(file):
    field_size = {"max_x": 20, "max_y": 20}
    board = {}
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
        
            if not line or line.startswith('#'):
                continue

            if line.startswith('SIZE'):
                parts = line.split()
                field_size["max_x"] = int(parts[1])
                field_size["max_y"] = int(parts[2])
                continue
                
            try:
                x_str, y_str, value_str = line.split()
                x, y, value = int(x_str), int(y_str), int(value_str)
            except ValueError:
                print(f"Ошибка чтения строки: '{line}'. Неверный формат.")
                return None, None

            if not (0 <= x <= field_size["max_x"]) or not (0 <= y <= field_size["max_y"]):
                print(f"Ошибка: Точка ({x}, {y}) выходит за границы поля {field_size['max_x']}x{field_size['max_y']}!")
                return None, None
            
            if (x, y) in board:
                print(f"Ошибка: Координата ({x}, {y}) указана в файле дважды!")
                return None, None
            
            board[(x, y)] = value
    
    values = list(board.values())
    cnts = Counter(values)

    for num, count in cnts.items():
        if count != 2:
            print(f"Ошибка: Цифра {num} встречается {count} раз(а). Должно быть строго 2 (пара)!")
            return None, None
        
    return field_size, board

def get_neighbours(x, y, size):
    if y % 2 == 0:
        candidates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x-1, y-1), (x-1, y+1)]
    else:
        candidates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y-1), (x+1, y+1)]
    
    neighbours = []
    for xn, yn in candidates:
        if 0 <= xn <= size["max_x"] and 0 <= yn <= size["max_y"]:
            neighbours.append((xn, yn))

    return neighbours

class HexNumberlink:
    def __init__(self, size, board):
        self.size = size
        self.board = board 

        self.pairs = {}
        for coord, num in board.items():
            self.pairs.setdefault(num, []).append(coord)
        
        self.numbers = sorted(list(self.pairs.keys()))
        self.visited = set()
        self.sollutions = []
        self.count_sollutions = 1

    def solve(self, max_solutions = 1):
        self.max_solutions = max_solutions
        self.sollutions = []
        self.visited = set()
        self.path_history = []

        first_number = self.numbers[0]
        start = self.pairs[first_number][0]

        self.visited.add(start)
        self.path_history.append(start)

        self._backtrack(start, first_number, 0)
        return self.sollutions

    def _backtrack(self, cur_pos, cur_num, num_index):
        if len(self.sollutions) >= self.max_solutions:
            return
        
        cur_target = self.pairs[cur_num][1]

        if cur_pos == cur_target:
            if num_index == len(self.numbers) - 1:
                self.sollutions.append(list(self.path_history))                     
                return
            else:
                next_num = self.numbers[num_index + 1]
                next_start = self.pairs[next_num][0]

                if next_start in self.visited:
                    return
                
                self.visited.add(next_start)
                self.path_history.append(next_start)  
                self._backtrack(next_start, next_num, num_index + 1)
                self.path_history.pop()   
                self.visited.remove(next_start)
                return
            
        for neighbour in get_neighbours(cur_pos[0], cur_pos[1], self.size):
            if neighbour in self.visited:
                continue

            if neighbour in self.board and neighbour != cur_target:
                continue
            
            self.visited.add(neighbour)
            self.path_history.append(neighbour)  
            self._backtrack(neighbour, cur_num, num_index)
            self.path_history.pop()  
            self.visited.remove(neighbour)