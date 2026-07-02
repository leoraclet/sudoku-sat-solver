import argparse
import os
import subprocess

N = range(9)


def var_index(i, j, k):
    return i * 81 + j * 9 + k + 1


def solve_sudoku(sudoku_line: str):
    """
    Résout le Sudoku avec le solveur cryptominisat
    Affiche une grille 9x9 solution, ou Erreur si insatisfaisable.
    """

    clauses = []

    ##################################################
    # LIT LA CHAINE ET MET SOUS FORME BOOLEENNE
    ##################################################
    for i in N:
        for j in N:
            cell = sudoku_line[i * 9 + j]
            if cell in "123456789":
                # Contrainte sur les valeurs déjà présentes dans la grille
                clauses.append([var_index(i, j, int(cell) - 1)])

    ##################################################
    # AJOUTE LES CONTRAINTES / REGLES DU SUDOKU
    ##################################################

    # 1. Contrainte : Chaque case contient EXACTEMENT un nombre (1-9)
    for i in range(9):
        for j in range(9):
            # Au moins un nombre dans la case (i,j)
            at_least_one = [var_index(i, j, k) for k in range(9)]
            clauses.append(at_least_one)

            # Au plus un nombre dans la case (i,j)
            for k in range(9):
                for e in range(k + 1, 9):
                    at_most_one = [
                        -var_index(i, j, k),
                        -var_index(i, j, e),
                    ]
                    clauses.append(at_most_one)

    # 2. Contrainte : Chaque nombre apparaît EXACTEMENT une fois par ligne
    for i in range(9):
        for k in range(9):
            # Au moins une fois le nombre k dans la ligne i
            at_least_one = [var_index(i, j, k) for j in range(9)]
            clauses.append(at_least_one)

            # Au plus une fois le nombre k dans la ligne i
            for j in range(9):
                for jp in range(j + 1, 9):
                    at_most_one = [-var_index(i, j, k), -var_index(i, jp, k)]
                    clauses.append(at_most_one)

    # 3. Contrainte : Chaque nombre apparaît EXACTEMENT une fois par colonne
    for j in range(9):
        for k in range(9):
            # Au moins une fois le nombre k dans la colonne j
            at_least_one = [var_index(i, j, k) for i in range(9)]
            clauses.append(at_least_one)

            # Au plus une fois le nombre k dans la colonne j
            for i in range(9):
                for ip in range(i + 1, 9):
                    at_most_one = [-var_index(i, j, k), -var_index(ip, j, k)]
                    clauses.append(at_most_one)

    # 4. Contrainte : Chaque nombre apparaît EXACTEMENT une fois par carré 3x3
    for box_i in range(0, 9, 3):  # Lignes des coins des carrés (0, 3, 6)
        for box_j in range(0, 9, 3):  # Colonnes des coins des carrés (0, 3, 6)
            for k in range(9):
                # Au moins une fois le nombre k dans le carré (box_i, box_j)
                at_least_one = []
                for di in range(3):
                    for dj in range(3):
                        at_least_one.append(var_index(box_i + di, box_j + dj, k))
                clauses.append(at_least_one)

                # Au plus une fois le nombre k dans le carré
                for di in range(3):
                    for dj in range(3):
                        for di2 in range(3):
                            for dj2 in range(3):
                                if (di, dj) != (di2, dj2):
                                    at_most_one = [
                                        -var_index(box_i + di, box_j + dj, k),
                                        -var_index(box_i + di2, box_j + dj2, k),
                                    ]
                                    clauses.append(at_most_one)

    ##################################################
    # RESOUD ET AFFICHE LA SOLUTION SI EXISTE
    ##################################################
    with open("pb.txt", "w") as f:
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")

    # Lit al sortie du sovleur
    sol = subprocess.run(
        ["cryptominisat5", "--verb", "0", "pb.txt"], capture_output=True, text=True
    ).stdout

    os.remove("pb.txt")

    # Si le problème n'admet AUCUNE solution
    if "UNSATISFIABLE" in sol:
        raise Exception("Sudoku is not solvable !!")

    # Nettoyage de la sortie su solveur SAT
    sol = sol.replace("\n", "")
    sol = sol.replace("v", "")
    sol = sol.replace("  ", " ")
    sol = sol.split(" ")[2:-1]
    sol = [int(e) + 1 if "-" in e else int(e) - 1 for e in sol]
    grid = [[0 for _ in range(9)] for _ in range(9)]

    # Re-création de la grille de Sudoku complète
    for var in sol:
        e = abs(int(var))
        if var > 0:
            grid[e // 81][(e % 81) // 9] = e % 9 + 1

    # Affichage de la grille
    print("-" * 23)
    for r in N:
        for c in N:
            if (c % 3) == 0:
                print("|" + str(grid[r][c]), end="|")
            else:
                print(grid[r][c], end="|")
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
