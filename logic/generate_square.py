import json
import random

from solve_puzzle import is_valid_puzzle

Types = {
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
}

Addition_Subtraction = {
    3: [-5, 80],
    4: [-10, 80],
    5: [-15, 80],
    6: [-20, 80],
    7: [-25, 80],
    8: [-30, 80],
    9: [-35, 80],
    10: [-40, 80],
    11: [-45, 50],
    12: [-50, 50],
}

Multiply = {
    3: [2, 9],
    4: [2, 7],
    5: [2, 7],
    6: [2, 7],
    7: [2, 4],
    8: [2, 4],
    9: [2, 4]
}


def choose_square(size, read_path):
    with open(read_path, 'r') as jsonfile:
        loaded_data = json.load(jsonfile)
    key = Types[size]
    all_squares = loaded_data[key]
    square = random.choice(all_squares)
    return square


def add_subtract_from_square(size, square, no_negative):
    add_subtract_range = Addition_Subtraction[size]
    if no_negative:
        num = random.randint(1, add_subtract_range[1])
    else:
        num = random.randint(add_subtract_range[0], -1)
    new_square = []
    for index1, row in enumerate(square):
        new_row = []
        for i in row:
            new_row.append(i + num)
        new_square.append(new_row)
    if not no_negative:
        for row in new_square:
            for i in row:
                if i < 0:
                    return new_square
        return add_subtract_from_square(size, square, no_negative)
    return new_square


def multiply_square(size, square):
    multiply_range = Multiply[size]
    multiply = random.randint(multiply_range[0], multiply_range[1])
    new_square = []
    for index1, row in enumerate(square):
        new_row = []
        for i in row:
            new_row.append(i * multiply)
        new_square.append(new_row)
    return new_square
