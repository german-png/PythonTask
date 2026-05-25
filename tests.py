import unittest 
from numberlink import parsing_coordinates, get_neighbours, HexNumberlink

class TestParsingCoordinatesRealFiles(unittest.TestCase):
    def setUp(self):
        self.filename = "temp_file.txt"

    def writeTempFile(self, info):
        with open(self.filename, 'w', encoding="utf8-") as file:
            file.write(info)
    
    def test_valid_parse_file(self):
        self.writeTempFile("SIZE 4 4\n0 0 1\n3 3 1\n1 1 2\n2 2 2")
        size, board = parsing_coordinates(self.filename)

        self.assertEqual(size, {"max_x": 4, "max_y": 4})
        self.assertEqual(board[(0, 0)], 1)
        self.assertEqual(board[(3, 3)], 1)
        self.assertEqual(board[(1, 1)], 2)
        self.assertEqual(board[(2, 2)], 2)

    def test_invalid_count(self):
        self.writeTempFile("SIZE 4 4\n0 0 1\n3 3 1\n1 1 1")
        size, board = parsing_coordinates(self.filename)
        
        self.assertIsNone(size)
        self.assertIsNone(board)

    def test_duplicate_coordinates(self):
        self.writeTempFile("SIZE 4 4\n0 0 1\n3 3 1\n 1 1 2\n0 0 2")
        size, board = parsing_coordinates(self.filename)
        
        self.assertIsNone(size)
        self.assertIsNone(board)

    def test_out_of_bound(self):
        self.writeTempFile("SIZE 2 2\n3 1 1\n0 0 1")
        size, board = parsing_coordinates(self.filename)
        
        self.assertIsNone(size)
        self.assertIsNone(board)

    def test_comments(self):
        self.writeTempFile("SIZE 3 3\n#Рандомный коммент\n\n1 1 1\n0 0 1")
        size, board = parsing_coordinates(self.filename)

        self.assertEqual(size, {"max_x": 3, "max_y": 3})
        self.assertEqual(board[(1,1)], 1)
        self.assertEqual(board[(0,0)], 1)

    def test_invalid_string_format(self):
        self.writeTempFile("SIZE 3 3\n0 0 smth \n1 1 1")
        size, board = parsing_coordinates(self.filename)

        self.assertIsNone(size)
        self.assertIsNone(board)

class TestGetNeighbours(unittest.TestCase):
    def setUp(self):
        self.size = {"max_x": 5, "max_y": 5}

    def test_central_hex_neighbours(self):
        neighbours = get_neighbours(2, 2, self.size)
        expected = [(3, 2), (1, 2), (2, 3), (2, 1), (1, 1), (1, 3)]
        
        self.assertEqual(set(neighbours), set(expected))
        self.assertEqual(len(neighbours), 6)

    def test_corner_hex_neighnours(self):
        neighbours = get_neighbours(0, 0, self.size)
        expected = [(1, 0), (0, 1)]

        self.assertEqual(set(neighbours), set(expected))
        self.assertEqual(len(neighbours), 2)

    def test_boarder_even_hex_neighbours(self):
        neighbours = get_neighbours(0, 2, self.size)
        expected = [(1, 2), (0, 3), (0, 1)]
        
        self.assertEqual(set(neighbours), set(expected))
        self.assertEqual(len(neighbours), 3)

    def test_boarder_odd_hex_neighbours(self):
        neighbours = get_neighbours(0, 3, self.size)
        expected = [(1, 3), (0, 4), (0, 2), (1, 2), (1, 4)]
        
        self.assertEqual(set(neighbours), set(expected))
        self.assertEqual(len(neighbours), 5)

class TestGetCountSolutions(unittest.TestCase):
    def test_one_path(self):
        size = {"max_x": 1, "max_y": 1}

        board = {
            (0, 0): 1,
            (1, 1): 1
        } 

        solver = HexNumberlink(size, board)
        solutions = solver.solve(max_solutions=10)
        self.assertEqual(len(solutions), 4)

    def test_no_solutions(self):
        size = {"max_x": 2, "max_y": 2}
        board = {
            (0, 0): 1,  
            (2, 2): 1,  
            (1, 0): 2,  
            (0, 1): 2,  
        }
        
        solver = HexNumberlink(size, board)
        solutions = solver.solve(max_solutions=10)
        self.assertEqual(len(solutions), 0)
    
    def test_max_solutions_limit(self):
        size = {"max_x": 1, "max_y": 1}

        board = {
            (0, 0): 1,
            (1, 1): 1
        } 

        solver = HexNumberlink(size, board)
        solutions = solver.solve(max_solutions=2)
        self.assertEqual(len(solutions), 2)

if __name__ == "__main__":
    unittest.main()