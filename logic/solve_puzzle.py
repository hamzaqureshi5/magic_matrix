import copy
import random

from check_solvable import is_solve_able

def check_sum(row, ans):
    return sum(row) == ans

def is_valid_puzzle(square):
    # Check if it's a square (all rows have the same length)
    N = len(square)
    if all(len(row) == N for row in square):
        # Calculate the expected sum (sum of the first row)
        expected_sum = sum(square[0])

        # Check rows
        is_valid = all(sum(row) == expected_sum for row in square)

        # Check columns
        is_valid = is_valid and all(sum(square[i][j] for i in range(N)) == expected_sum for j in range(N))

        # Check the main diagonal (top-left to bottom-right)
        is_valid = is_valid and sum(square[i][i] for i in range(N)) == expected_sum

        # Check the other diagonal (top-right to bottom-left)
        is_valid = is_valid and sum(square[i][N - i - 1] for i in range(N)) == expected_sum

        if is_valid:
            return True
        else:
            return False
    else:
        return False

def check_puzzle(pzl, difficulty_level, numbers_to_hide):
                                  
    complete_show = 0
    for row in pzl:
        str_count = 0
        for str_item in row:
            if isinstance(str_item, str):
                str_count += 1
        if str_count == 0:
            complete_show += 1
                                
    for i in range(len(pzl)):
        col = []
        for row_ in pzl:
            col.append(row_[i])
        str_count = 0
        for str_item in col:
            if isinstance(str_item, str):
                str_count += 1
        if str_count == 0:
            complete_show += 1
    # main diagonal
    main_d = []
    for ii, row_ in enumerate(pzl):
        for iii, item in enumerate(row_):
            if ii == iii:
                main_d.append(item)
    str_count = 0
    for str_item in main_d:
        if isinstance(str_item, str):
            str_count += 1
    if str_count == 0:
        complete_show += 1

    # other diagonal
    other_d = []
    for ii, row_2 in enumerate(pzl):
        for iii, item2 in enumerate(row_2[::-1]):
            if ii == iii:
                other_d.append(item2)
    str_count = 0
    for str_item in other_d:
        if isinstance(str_item, str):
            str_count += 1
    if str_count == 0:
        complete_show += 1

    numbers = 0
    for ii in pzl:
        str_count = 0
        for str_item in ii:
            if isinstance(str_item, str):
                str_count += 1
        numbers += str_count
    if numbers == numbers_to_hide and complete_show == 1:
        return True
    return False
                                                                   
def generate_unsolved_puzzle(pzl, difficulty_level="easy"):
    n = len(pzl)

    if difficulty_level == "easy":
        numbers_to_hide = n + n - 1

        # Choose a row, column, or diagonal to keep intact
        show = random.choice(["row", "col", "diagonal"])
        show_row = False
        show_column = False
        show_diagonal = False
        if show == "row":
            row_to_show = random.randint(0, n - 1)
            show_row = True
        elif show == "col":
            col_to_show = random.randint(0, n - 1)
            show_column = True
        else:
            diagonal_to_show = random.randint(0, 1)  # 0 for main diagonal, 1 for other diagonal
            show_diagonal = True

        unsolved_pzl = copy.deepcopy(pzl)

        for i in range(n):
            for j in range(n):
                if (show_row and i == row_to_show) or \
                        (show_column and j == col_to_show) or \
                        (show_diagonal and (
                            (diagonal_to_show == 0 and i == j) or (diagonal_to_show == 1 and i == n - 1 - j))):
                    continue
                elif random.random() < 0.6:  # Hard-coded percentage
                    unsolved_pzl[i][j] = "hide"

    elif difficulty_level == "medium":
        numbers_to_hide = n + n + (n - 3)  # Grid 4×4 4+4+(4-3)=9 hidden numbers

        show = random.choice(["row", "col", "diagonal"])
        show_row = False
        show_column = False
        show_diagonal = False
        if show == "row":
            row_to_show = random.randint(0, n - 1)
            show_row = True
        elif show == "col":
            col_to_show = random.randint(0, n - 1)
            show_column = True
        else:
            diagonal_to_show = random.randint(0, 1)  # 0 for main diagonal, 1 for other diagonal
            show_diagonal = True

        unsolved_pzl = copy.deepcopy(pzl)

        for i in range(n):
            for j in range(n):
                if (show_row and i == row_to_show) or \
                        (show_column and j == col_to_show) or \
                        (show_diagonal and (
                            (diagonal_to_show == 0 and i == j) or (diagonal_to_show == 1 and i == n - 1 - j))):
                    continue
                elif random.random() < 0.6:  # Hard-coded percentage
                    unsolved_pzl[i][j] = str(unsolved_pzl[i][j])

    elif difficulty_level == "hard":
        numbers_to_hide = n + n + (n - 2)  # Grid 4×4 4+4+(4-2)=10 hidden numbers

        show = random.choice(["row", "col", "diagonal"])
        show_row = False
        show_column = False
        show_diagonal = False
        if show == "row":
            row_to_show = random.randint(0, n - 1)
            show_row = True
        elif show == "col":
            col_to_show = random.randint(0, n - 1)
            show_column = True
        else:
            diagonal_to_show = random.randint(0, 1)  # 0 for main diagonal, 1 for other diagonal
            show_diagonal = True

        unsolved_pzl = copy.deepcopy(pzl)

        for i in range(n):
            for j in range(n):
                if (show_row and i == row_to_show) or \
                        (show_column and j == col_to_show) or \
                        (show_diagonal and (
                            (diagonal_to_show == 0 and i == j) or (diagonal_to_show == 1 and i == n - 1 - j))):
                    continue
                elif random.random() < 0.6:  # Hard-coded percentage
                    unsolved_pzl[i][j] = str(unsolved_pzl[i][j])

    else:
        raise ValueError("Invalid difficulty level")

    # Create a copy of the puzzle to modify
    unsolved_pzl = copy.deepcopy(pzl)

    # Count the number of hidden numbers
    hidden_count = 0

    # Hide numbers based on the calculated numbers to hide
    while hidden_count < numbers_to_hide:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)

        # Check if this element is already hidden
        if unsolved_pzl[i][j] == "hide":
            continue

        # Hide the number and increment the count
        unsolved_pzl[i][j] = str(unsolved_pzl[i][j])
        hidden_count += 1

    return unsolved_pzl

def get_unsolved_puzzle(pzl, difficulty_level="easy"):
    n = len(pzl)  # Calculate the dimension based on the puzzle grid

    def numbers_to_hide_for_difficulty(difficulty_level):
        if difficulty_level == "easy":
            return n + n - 1  # Adjust this calculation as needed
        elif difficulty_level == "medium":
            return n + n + (n - 3)  # Adjust this calculation as needed
        elif difficulty_level == "hard":
            return n + n + (n - 2)  # Adjust this calculation as needed
        else:
            raise ValueError("Invalid difficulty level")

    numbers_to_hide = numbers_to_hide_for_difficulty(difficulty_level)
    
    puzzle = generate_unsolved_puzzle(pzl, difficulty_level)
    while not check_puzzle(puzzle, difficulty_level, numbers_to_hide):
        puzzle = generate_unsolved_puzzle(pzl, difficulty_level)
    while not is_solve_able(puzzle):
        return get_unsolved_puzzle(pzl, difficulty_level)
    return puzzle
