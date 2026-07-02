import argparse
import itertools

import z3

N = range(9)


def solve_sudoku(sudoku_line: str):
    """
    Résout le Sudoku avec le solveur z3
    Affiche une grille 9x9 solution, ou Erreur si insatisfaisable.
    """

    s = z3.Solver()

    ##################################################
    # LIT LA CHAINE ET INITIALISE LE SOLVEUR SAT
    ##################################################

    grid = []
    for r in N:
        row = []
        for c in N:
            cell = sudoku_line[r * 9 + c]
            v = z3.Int("c_%d_%d" % (r, c))
            row.append(v)
            if cell != "#":
                s.add(v == int(cell))
        grid.append(row)

    ##################################################
    # AJOUTE LES CONTRAINTES / REGLES DU SUDOKU
    ##################################################

    # 1. Contrainte : Chaque case contient EXACTEMENT un nombre (1-9)
    for r in N:
        for c in N:
            v = grid[r][c]
            s.add(v >= 1)
            s.add(v <= 9)

    # 2. Contrainte : Chaque nombre apparaît EXACTEMENT une fois par ligne
    for r in N:
        s.add(z3.Distinct(grid[r]))

    # 3. Contrainte : Chaque nombre apparaît EXACTEMENT une fois par colonne
    for c in N:
        col = [grid[r][c] for r in N]
        s.add(z3.Distinct(col))

    # 4. Contrainte : Chaque nombre apparaît EXACTEMENT une fois par carré 3x3
    offsets = list(itertools.product(range(0, 3), range(0, 3)))
    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            group_cells = []
            for dy, dx in offsets:
                group_cells.append(grid[r + dy][c + dx])
            s.add(z3.Distinct(group_cells))

    ##################################################
    # RESOUD ET AFFICHE LA SOLUTION SI EXISTE
    ##################################################

    # Si le problème n'admet AUCUNE solution
    if s.check() != z3.sat:
        raise Exception("Sudoku is not solvable !!")

    m = s.model()

    # Affichage de la grille
    print("-" * 23)
    for r in N:
        for c in N:
            if (c % 3) == 0:
                print("|" + str(m.evaluate(grid[r][c])), end="|")
            else:
                print(m.evaluate(grid[r][c]), end="|")
            if (c + 1) % 3 == 0:
                print(" ", end="")
        print()
        if (r + 1) % 3 == 0:
            print("-" * 23)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", nargs="?", default=None, help="Chaîne représentant le Sudoku"
    )
    args = parser.parse_args()

    if args.input:
        print("Résolution du problème ...\n")
        solve_sudoku(args.input)
    else:
        # Sample test
        print("Test de résolution sur la grille de l'énnoncé ...\n")
        sample_sudoku_grid = "#26###81#3##7#8##64###5###7#5#1#7#9###39#51###4#3#2#5#1###3###25##2#4##9#38###46#"
        solve_sudoku(sample_sudoku_grid)
