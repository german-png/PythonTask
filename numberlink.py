from collections import Counter
import os
import pygame
import math
import sys

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

    

BG_COLOR = (179, 179, 179)  # Фон окна
HEX_COLOR = (179, 179, 179) # Цвет заливки свободных гексагонов
LINE_COLOR = (0, 0, 0)  # Цвет сетки

# Цвета для пар
COLORS = {
    1: (219, 121, 121),   
    2: (46, 204, 113),  
    3: (92, 197, 229),  
    4: (241, 196, 15),  
}

radius = 50
width = math.sqrt(3) * radius
height = 2 * radius

def get_pixel_coordinates(x, y):
    pixel_x = x * width
    if y % 2 != 0:
        pixel_x += width / 2
    pixel_y = y * (height * 0.75)
    return pixel_x + 50, pixel_y + 60

def draw_hex(surface, color, center, width = 0):
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30 
        angle_rad = math.pi / 180 * angle_deg
        pt_x = center[0] + radius * math.cos(angle_rad)
        pt_y = center[1] + radius * math.sin(angle_rad)
        points.append((pt_x, pt_y))

    pygame.draw.polygon(surface, color, points, width)

def build_path_map(solution_path, numbers, pairs):
    path_map = {}
    current_tracking_num = numbers[0]
    num_idx = 0
    
    for coord in solution_path:
        path_map[coord] = current_tracking_num
        if coord == pairs[current_tracking_num][1]:
            num_idx += 1
            if num_idx < len(numbers):
                current_tracking_num = numbers[num_idx]
    return path_map

def run_gui(size, board_setup, found_solutions, numbers, pairs):
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 22, bold=True)

    max_x = size["max_x"]
    max_y = size["max_y"]
    
    # Разамер окна WIN
    win_width = int((max_x + 1.5) * width + 15)
    win_height = int((max_y * 0.75 + 1.5) * height + 100)
    screen = pygame.display.set_mode((win_width, win_height))
    
    current_idx = 0
    num_solutions = len(found_solutions)
    
    running = True
    while running:
        pygame.display.set_caption(f"Решение {current_idx + 1} из {num_solutions}")
        
        current_solution_path = found_solutions[current_idx]
        current_path_map = build_path_map(current_solution_path, numbers, pairs)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    current_idx = (current_idx + 1) % num_solutions
                elif event.key == pygame.K_LEFT:
                    current_idx = (current_idx - 1) % num_solutions
                    
        screen.fill(BG_COLOR)
        
        # Отрисовка сетки и пар
        for y in range(max_y + 1):
            for x in range(max_x + 1):
                coord = (x, y)
                center = get_pixel_coordinates(x, y)
                
                if coord in board_setup:
                    num = board_setup[coord]
                    cell_color = COLORS.get(num, HEX_COLOR)
                else:
                    cell_color = HEX_COLOR 
                    
                draw_hex(screen, cell_color, center, width=0) # Заливка шестиугольника
                draw_hex(screen, LINE_COLOR, center, width=4) # Отрисовка контура шестиугольника

        # Отрисовка пути, который соединяет пары
        for num in numbers:
            line_color = COLORS.get(num, (255, 255, 255))
            
            pixel_points = []
            for coord in current_solution_path:
                if current_path_map.get(coord) == num:
                    # Переводим виртуальную координату соты в пиксели (центр)
                    pixel_center = get_pixel_coordinates(coord[0], coord[1])
                    pixel_points.append(pixel_center)
            
            if len(pixel_points) >= 2:
                pygame.draw.lines(screen, line_color, False, pixel_points, width=7)

        # Текст подсказки
        help_text = font.render("Используй <- и -> для переключения", True, (0, 0, 0))
        help_rect = help_text.get_rect(center=(win_width // 2, win_height - 30))
        screen.blit(help_text, help_rect)
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    file_path = os.path.join(script_dir, 'input.txt') 
    
    size, my_board = parsing_coordinates(file_path)
    
    if size and my_board:
        solver = HexNumberlink(size, my_board)
        solutions = solver.solve(max_solutions=500)
        
        if solutions:
            print(f"Найдено решений: {len(solutions)}")
            run_gui(size, my_board, solutions, solver.numbers, solver.pairs)
        else:
            print("Решений не найдено")
    else:
        print("Не удалось прочесть или распарсить файл карты")


