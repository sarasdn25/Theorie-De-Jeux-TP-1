#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import random
import sys
from itertools import product


class Game:
    # names[i] : noms des stratégies du joueur i ; pay : {profil: vecteur de gains}
    def __init__(self, names, pay):
        self.names = names
        self.pay = pay
        self.n = len(names)

    def full_remaining(self):
        # au départ, toutes les stratégies sont présentes
        return [list(range(len(nm))) for nm in self.names]


def from_nested(names, nested):
    # construit un Game à partir d'une liste imbriquée de gains
    n = len(names)
    pay = {}

    def rec(level, node, prefix):
        if level == n:
            if len(node) != n:
                raise ValueError(f"Vecteur de gains de taille {len(node)} au "
                                 f"profil {prefix}, {n} attendus.")
            pay[tuple(prefix)] = tuple(node)
            return
        if len(node) != len(names[level]):
            raise ValueError(f"Le joueur {level + 1} a {len(names[level])} "
                             f"stratégies mais {len(node)} lignes sont données.")
        for idx, child in enumerate(node):
            rec(level + 1, child, prefix + [idx])

    rec(0, nested, [])
    return Game(names, pay)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return from_nested(data["strategies"], data["payoffs"])


def fmt_num(x):
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return f"{x:g}" if isinstance(x, float) else str(x)


def fmt_vec(v):
    return "(" + ", ".join(fmt_num(x) for x in v) + ")"


def print_table(title, row_labels, col_labels, cells):
    # affiche un tableau texte aligné
    if title:
        print(title)
    w0 = max([len(r) for r in row_labels] + [1])
    widths = [max(len(col_labels[c]), *(len(cells[r][c]) for r in range(len(row_labels))))
              for c in range(len(col_labels))]
    header = " " * w0 + " | " + " | ".join(col_labels[c].center(widths[c])
                                           for c in range(len(col_labels)))
    sep = "-" * len(header)
    print(header)
    print(sep)
    for r, rl in enumerate(row_labels):
        print(rl.ljust(w0) + " | " + " | ".join(cells[r][c].center(widths[c])
                                                for c in range(len(col_labels))))


def display_game(game, rem):
    # 2 joueurs : une matrice ; 3 ou plus : une matrice par combinaison des joueurs 3..n
    rows, cols = rem[0], rem[1]
    row_labels = [game.names[0][r] for r in rows]
    col_labels = [game.names[1][c] for c in cols]

    if game.n == 2:
        cells = [[fmt_vec(game.pay[(r, c)]) for c in cols] for r in rows]
        print_table(f"  Joueur 1 (lignes) \\ Joueur 2 (colonnes)",
                    row_labels, col_labels, cells)
        return

    for combo in product(*rem[2:]):
        label = ", ".join(f"Joueur {j + 3} = {game.names[j + 2][s]}"
                          for j, s in enumerate(combo))
        cells = [[fmt_vec(game.pay[(r, c) + combo]) for c in cols] for r in rows]
        print_table(f"  [{label}]  (Joueur 1 en lignes, Joueur 2 en colonnes)",
                    row_labels, col_labels, cells)
        print()


def display_remaining(game, rem):
    for i in range(game.n):
        print(f"  Joueur {i + 1} : " + ", ".join(game.names[i][s] for s in rem[i]))


def dominates(game, rem, i, b, a, mode):
    # True si b domine a pour le joueur i, contre toutes les combinaisons des autres
    others = [rem[j] if j != i else [None] for j in range(game.n)]
    all_strict = True
    any_strict = False
    for combo in product(*others):
        pa = list(combo)
        pb = list(combo)
        pa[i] = a
        pb[i] = b
        ua = game.pay[tuple(pa)][i]
        ub = game.pay[tuple(pb)][i]
        if ub < ua:
            return False
        if ub <= ua:
            all_strict = False
        if ub > ua:
            any_strict = True
    if mode == "strict":
        return all_strict
    return any_strict


def find_dominated(game, rem, mode, player_order):
    # retourne (joueur, stratégie dominée, dominants) ou None
    for i in player_order:
        if len(rem[i]) < 2:
            continue
        for a in rem[i]:
            doms = [b for b in rem[i] if b != a and dominates(game, rem, i, b, a, mode)]
            if doms:
                return i, a, doms
    return None


def iterated_elimination(game, mode, player_order=None, verbose=True):
    # boucle d'élimination avec trace ; retourne (stratégies restantes, éliminations)
    if player_order is None:
        player_order = list(range(game.n))
    rem = game.full_remaining()
    steps = []
    nom_mode = "strictement" if mode == "strict" else "faiblement"

    if verbose:
        print("\n=== Jeu initial ===")
        display_game(game, rem)
        print(f"\nMode : dominance {'stricte' if mode == 'strict' else 'faible'}")
        print("Ordre d'examen des joueurs : "
              + " puis ".join(f"Joueur {i + 1}" for i in player_order))

    while True:
        found = find_dominated(game, rem, mode, player_order)
        if found is None:
            break
        i, a, doms = found
        b = doms[0]
        steps.append((i, a, b))
        rem[i].remove(a)
        if verbose:
            autres = ""
            if len(doms) > 1:
                autres = " (aussi dominée par " + ", ".join(
                    game.names[i][d] for d in doms[1:]) + ")"
            print(f"\n--- Étape {len(steps)} ---")
            print(f"Joueur {i + 1} : la stratégie {game.names[i][a]} est supprimée, "
                  f"{nom_mode} dominée par {game.names[i][b]}{autres}.")
            print("Jeu après suppression :")
            display_game(game, rem)

    if verbose:
        print("\n=== Résultat final ===")
        if not steps:
            print("Aucune élimination n'est possible : le jeu reste inchangé.")
        else:
            print("Ordre des éliminations : " + " ; ".join(
                f"J{i + 1}:{game.names[i][a]} (par {game.names[i][b]})"
                for i, a, b in steps))
        print("Jeu réduit :")
        display_game(game, rem)
        if all(len(r) == 1 for r in rem):
            prof = tuple(rem[i][0] for i in range(game.n))
            noms = ", ".join(game.names[i][prof[i]] for i in range(game.n))
            print(f"\nIl reste un SEUL profil de stratégies : ({noms}) "
                  f"avec les gains {fmt_vec(game.pay[prof])}.")
        else:
            print("\nIl reste PLUSIEURS profils : le jeu ne se réduit pas à un seul profil.")
            display_remaining(game, rem)
            if mode == "faible":
                print("(En dominance faible, le résultat peut dépendre de l'ordre "
                      "d'élimination suivi.)")
    return rem, steps


def parse_num(tok):
    try:
        return int(tok)
    except ValueError:
        return float(tok.replace(",", "."))


def ask_int(prompt, minimum=1):
    while True:
        try:
            v = int(input(prompt).strip())
            if v >= minimum:
                return v
        except ValueError:
            pass
        print(f"  Entrez un entier >= {minimum}.")


def default_names(n, ks):
    return [[f"{chr(65 + i)}{j + 1}" for j in range(ks[i])] for i in range(n)]


def ask_sizes():
    n = ask_int("Nombre de joueurs (>= 2) : ", 2)
    ks = [ask_int(f"Nombre de stratégies du joueur {i + 1} : ", 1) for i in range(n)]
    return n, ks


def input_keyboard():
    n, ks = ask_sizes()
    names = default_names(n, ks)
    for i in range(n):
        s = input(f"Noms des {ks[i]} stratégies du joueur {i + 1} "
                  f"(séparés par des espaces, Entrée = {' '.join(names[i])}) : ").split()
        if len(s) == ks[i]:
            names[i] = s
        elif s:
            print("  Nombre de noms incorrect, noms par défaut conservés.")
    pay = {}
    print("\nSaisissez les gains de chaque profil (n nombres séparés par des espaces).")
    for prof in product(*[range(k) for k in ks]):
        label = ", ".join(names[i][prof[i]] for i in range(n))
        while True:
            try:
                vals = tuple(parse_num(t) for t in input(f"  Gains pour ({label}) : ").split())
                if len(vals) == n:
                    break
            except ValueError:
                pass
            print(f"  Entrez exactement {n} nombres.")
        pay[prof] = vals
    return Game(names, pay)


def input_random():
    n, ks = ask_sizes()
    lo = ask_int("Gain minimum : ", -10**9)
    hi = ask_int(f"Gain maximum (>= {lo}) : ", lo)
    pay = {prof: tuple(random.randint(lo, hi) for _ in range(n))
           for prof in product(*[range(k) for k in ks])}
    return Game(default_names(n, ks), pay)


def input_file():
    while True:
        path = input("Chemin du fichier JSON : ").strip()
        try:
            return load_json(path)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
            print(f"  Erreur de lecture : {e}")


def ex1():
    return from_nested([["H", "M", "B"], ["G", "C", "D"]], [
        [[3, 1], [2, 3], [0, 0]],
        [[1, 2], [1, 2], [5, 1]],
        [[2, 2], [0, 1], [1, 0]]])


def ex2():
    return from_nested([["Pierre", "Feuille", "Ciseaux"], ["Pierre", "Feuille", "Ciseaux"]], [
        [[0, 0], [-1, 1], [1, -1]],
        [[1, -1], [0, 0], [-1, 1]],
        [[-1, 1], [1, -1], [0, 0]]])


def ex3():
    return from_nested([["H", "B"], ["G", "M", "D"]], [
        [[2, 1], [2, 1], [2, 0]],
        [[2, 1], [1, 0], [2, 0]]])


def ex4():
    # 0 = C (contribuer), 1 = N (ne pas contribuer)
    pay = {}
    for prof in product(range(2), repeat=3):
        c = prof.count(0)
        pay[prof] = tuple(2 * c - 3 if prof[i] == 0 else 2 * c for i in range(3))
    return Game([["C", "N"]] * 3, pay)


def ex5():
    return from_nested([["A1", "A2", "A3"], ["B1", "B2", "B3"]], [
        [[10, 10], [4, 9], [4, 11]],
        [[5, 6], [8, 3], [3, 4]],
        [[4, 0], [8, 1], [5, 3]]])


EXAMPLES = {1: ex1, 2: ex2, 3: ex3, 4: ex4, 5: ex5}

EXAMPLE_INFO = {
    1: "2 joueurs, 3x3 : elimination jusqu'a 1x1 (dominance stricte)",
    2: "2 joueurs, 3x3 : Pierre-Feuille-Ciseaux (aucune elimination)",
    3: "2 joueurs, 2x3 : dominance faible et ordre d'elimination",
    4: "3 joueurs, 2 strategies chacun : contribuer ou non (C/N)",
    5: "2 joueurs, 3x3 : Exercice 4 de la Serie 1",
}


# modes imposés par le TP : (mode, ordre des joueurs)
EXAMPLE_RUNS = {
    1: [("strict", None)],
    2: [("strict", None), ("faible", None)],
    3: [("strict", None), ("faible", [0, 1]), ("faible", [1, 0])],
    4: [("strict", None)],
    5: [("strict", None), ("faible", None)],
}


def run_example(k, mode_filter=None, order_override=None):
    # lance l'exemple k dans le(s) mode(s) prévu(s) par le TP
    runs = [r for r in EXAMPLE_RUNS[k] if mode_filter in (None, r[0])]
    if not runs:
        runs = [(mode_filter, None)]
    for mode, order in runs:
        if order_override:
            order = order_override
        titre = f"EXEMPLE {k} - dominance {'stricte' if mode == 'strict' else 'faible'}"
        if order is not None:
            titre += " (joueurs examinés dans l'ordre " + " puis ".join(f"J{i + 1}" for i in order) + ")"
        print("\n" + "#" * 70 + f"\n# {titre}\n" + "#" * 70)
        iterated_elimination(EXAMPLES[k](), mode, order)


def choose_example():
    # affiche la liste des exemples et demande lequel lancer
    print("\nExemples disponibles :")
    for k in sorted(EXAMPLES):
        print(f"  {k}) Exemple {k} - {EXAMPLE_INFO[k]}")
    k = ask_int("Numero de l'exemple : ", 1)
    while k not in EXAMPLES:
        k = ask_int(f"Choisissez un numero entre 1 et {len(EXAMPLES)} : ", 1)
    return k


def run_tests():
    # vérifie les résultats attendus du TP
    def final(game, mode, order=None):
        rem, _ = iterated_elimination(game, mode, order, verbose=False)
        return [[game.names[i][s] for s in rem[i]] for i in range(game.n)]

    tests = [
        ("Exemple 1, strict", final(ex1(), "strict"), [["H"], ["C"]]),
        ("Exemple 2, strict", final(ex2(), "strict"), [["Pierre", "Feuille", "Ciseaux"]] * 2),
        ("Exemple 2, faible", final(ex2(), "faible"), [["Pierre", "Feuille", "Ciseaux"]] * 2),
        ("Exemple 3, strict", final(ex3(), "strict"), [["H", "B"], ["G", "M"]]),
        ("Exemple 3, faible (J1 d'abord)", final(ex3(), "faible", [0, 1]), [["H"], ["G", "M"]]),
        ("Exemple 3, faible (J2 d'abord)", final(ex3(), "faible", [1, 0]), [["H", "B"], ["G"]]),
        ("Exemple 4, strict", final(ex4(), "strict"), [["N"], ["N"], ["N"]]),
        ("Exemple 5, strict", final(ex5(), "strict"), [["A3"], ["B3"]]),
        ("Exemple 5, faible", final(ex5(), "faible"), [["A3"], ["B3"]]),
    ]
    ok = True
    for nom, got, exp in tests:
        good = got == exp
        ok &= good
        print(f"[{'OK' if good else 'ECHEC'}] {nom} : {got}")
    print("\nTous les tests passent." if ok else "\nCertains tests échouent.")
    return ok


def choose_mode():
    while True:
        c = input("Mode de dominance : 1) stricte  2) faible : ").strip()
        if c == "1":
            return "strict"
        if c == "2":
            return "faible"


def choose_order(n):
    s = input(f"Ordre d'examen des joueurs (ex. {' '.join(str(i + 1) for i in range(n))}, "
              f"Entrée = ordre naturel) : ").split()
    try:
        order = [int(t) - 1 for t in s]
        if sorted(order) == list(range(n)):
            return order
    except ValueError:
        pass
    if s:
        print("  Ordre invalide, ordre naturel utilisé.")
    return list(range(n))


def main():
    import argparse
    ap = argparse.ArgumentParser(description="TP Théorie des jeux : dominance stricte et faible")
    ap.add_argument("file", nargs="?", help="fichier JSON décrivant le jeu")
    ap.add_argument("--test", action="store_true", help="lance les tests du TP")
    ap.add_argument("--example", type=int, choices=sorted(EXAMPLES),
                    help="lance l'exemple choisi (1 à 5) dans le(s) mode(s) prévu(s) par le TP")
    ap.add_argument("--mode", choices=["strict", "faible", "weak"],
                    help="mode de dominance (pour un exemple : ne lance que ce mode)")
    ap.add_argument("--order", type=int, nargs="+",
                    help="ordre d'examen des joueurs en mode faible, ex. --order 2 1")
    args = ap.parse_args()

    if args.test:
        sys.exit(0 if run_tests() else 1)

    mode_arg = None
    if args.mode:
        mode_arg = "faible" if args.mode == "weak" else args.mode
    order_arg = [o - 1 for o in args.order] if args.order else None

    # exemple du TP : mode imposé, pas de question
    if args.example:
        run_example(args.example, mode_arg, order_arg)
        return

    if args.file:
        game = load_json(args.file)
    else:
        print("=== TP Théorie des jeux : élimination itérée des stratégies dominées ===")
        print("Source du jeu :\n  1) Saisie au clavier\n  2) Fichier JSON\n"
              "  3) Génération aléatoire\n  4) Exemples du TP (1 à 5)")
        choice = ""
        while choice not in ("1", "2", "3", "4"):
            choice = input("Votre choix : ").strip()
        if choice == "4":
            run_example(choose_example(), mode_arg, order_arg)
            return
        game = {"1": input_keyboard, "2": input_file, "3": input_random}[choice]()

    # jeu personnalisé : l'utilisateur choisit le mode
    mode = mode_arg or choose_mode()
    if mode == "faible":
        if order_arg and sorted(order_arg) == list(range(game.n)):
            order = order_arg
        else:
            if order_arg:
                print("Ordre invalide, il faut citer chaque joueur une fois.")
            order = choose_order(game.n)
    else:
        order = None
    iterated_elimination(game, mode, order)


if __name__ == "__main__":
    main()