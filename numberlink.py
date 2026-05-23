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