import copy


def replace_single_missing(pzl):
    for r_index, row in enumerate(pzl):
        if row.count("hide") == 1:
            index = row.index("hide")
            row[index] = 1

    for i in range(len(pzl)):
        col = []
        for row in pzl:
            col.append(row[i])
        if col.count("hide") == 1:
            index = col.index("hide")
            pzl[index][i] = 1

    # main diagonal
    main_diagonal = []
    for index_, row_ in enumerate(pzl):
        for i, item in enumerate(row_):
            if i == index_:
                main_diagonal.append(item)

    if main_diagonal.count("hide") == 1:
        index = main_diagonal.index("hide")
        pzl[index][index] = 1

    # other diagonal
    other_diagonal = []
    for index_, row_ in enumerate(pzl):
        for i, item in enumerate(row_[::-1]):
            if i == index_:
                other_diagonal.append(item)

    if other_diagonal.count("hide") == 1:
        index = other_diagonal.index("hide")
        pzl[index][-index] = 1

    return pzl


def is_solve_able(pzl):
    new_pzl = copy.deepcopy(pzl)
    for i in range(len(new_pzl) + 5):
        new_pzl = replace_single_missing(new_pzl)

    for ii in new_pzl:
        if "hide" in ii:
            return False
    return True

