# TP Théorie des jeux : Élimination itérée des stratégies dominées


## 1. Objectif

Écrire un programme qui prend en entrée un jeu fini sous forme normale avec un **nombre quelconque de joueurs** et un **nombre quelconque de stratégies par joueur**, l'affiche, puis le simplifie par **élimination itérée des stratégies dominées**, étape par étape, jusqu'au jeu réduit le plus petit possible. Seules les stratégies pures sont considérées.

## 2. Principe

Une stratégie **a** du joueur i est dominée par **b** si, contre toute combinaison s₋ᵢ des stratégies restantes des autres joueurs :

- **dominance stricte :** uᵢ(b, s₋ᵢ) > uᵢ(a, s₋ᵢ) pour tout s₋ᵢ ;
- **dominance faible :** uᵢ(b, s₋ᵢ) ≥ uᵢ(a, s₋ᵢ) pour tout s₋ᵢ, avec une inégalité stricte au moins une fois.

Deux stratégies ayant exactement les mêmes gains ne se dominent pas. Supprimer une stratégie change le jeu : une stratégie qui n'était pas dominée peut le devenir ensuite. Le processus est donc **itéré** jusqu'à ce que plus rien ne puisse être supprimé.

## 3. Représentation des données

| Élément | Signification |
|---|---|
| `Game.names[i]` | noms des stratégies du joueur i |
| `Game.pay` | dictionnaire `{(s1,...,sn): (u1,...,un)}`, stratégies repérées par leur indice d'origine |
| `Game.n` | nombre de joueurs |
| `rem[i]` | indices encore présents pour le joueur i (l'état de l'élimination) |

Supprimer une stratégie retire seulement son indice de `rem[i]` ; la table des gains n'est jamais modifiée. Le code ne dépend donc ni du nombre de joueurs ni du nombre de stratégies.

## 4. Fonctions principales

| Fonction | Rôle |
|---|---|
| `from_nested`, `load_json` | construisent un `Game` à partir de listes imbriquées / d'un fichier JSON, avec vérification des tailles |
| `input_keyboard`, `input_file`, `input_random` | les trois modes de saisie (R1) |
| `display_game`, `print_table` | affichage du jeu (R2) |
| `dominates(game, rem, i, b, a, mode)` | test de dominance (R3, R4) |
| `find_dominated` | trouve une stratégie dominée dans le jeu courant |
| `iterated_elimination` | boucle principale avec trace et résultat final (R5, R6) |
| `run_example` | lance un exemple du TP dans le(s) mode(s) imposé(s) par le TP |
| `run_tests` | vérification automatique des jeux de test du TP |

## 5. Test de dominance

Pour le joueur i et les stratégies a, b :

1. `itertools.product` génère toutes les combinaisons des stratégies restantes des **autres** joueurs.
2. Pour chaque combinaison, on compare le gain du joueur i avec a et avec b.
3. Si b < a pour une combinaison, le test s'arrête immédiatement : pas de dominance.
4. **Mode strict :** b doit être strictement supérieur à a pour toutes les combinaisons.
5. **Mode faible :** b doit être supérieur ou égal à a partout, et strictement supérieur au moins une fois.

Comme l'étape 1 couvre « toutes les combinaisons des autres », le même code fonctionne pour 2, 3, 4 joueurs ou plus. Deux stratégies identiques ne se dominent jamais (l'égalité échoue au test strict, et le mode faible exige une inégalité stricte).

## 6. Élimination itérée

```
rem = toutes les stratégies de tous les joueurs
répéter :
    chercher UNE stratégie dominée (joueurs dans l'ordre choisi)
    si aucune : arrêter
    noter (joueur, stratégie supprimée, stratégie dominante)
    la retirer de rem, afficher l'étape et le nouveau jeu
afficher le résultat final
```

Choix de conception :

- **Une seule élimination par itération**, suivie d'un nouveau balayage, car le jeu a changé. Cela donne la trace pas à pas exigée par R5.
- **La terminaison est garantie :** chaque itération supprime une stratégie, et une stratégie ne peut être dominée que par une stratégie qui reste ; la dernière stratégie d'un joueur n'est donc jamais supprimée.
- Si plusieurs stratégies dominent la stratégie supprimée, la trace nomme la première et ajoute « (aussi dominée par ...) ».

## 7. Affichage (R2)

- **2 joueurs :** un tableau aligné, joueur 1 en lignes, joueur 2 en colonnes, chaque case contenant `(u1, u2)`.
- **3 joueurs ou plus :** joueurs 1 et 2 en lignes/colonnes, et **une matrice étiquetée pour chaque combinaison des stratégies des joueurs 3 à n**, par exemple `[Joueur 3 = C, Joueur 4 = D]`.

## 8. Trace et résultat final (R5, R6)

À chaque étape, le programme affiche le joueur, la stratégie supprimée, la stratégie qui la domine et le jeu après suppression. À la fin, il affiche l'**ordre des éliminations**, le jeu réduit, et indique s'il reste **un seul profil** (avec ses gains) ou plusieurs. Si aucune élimination n'est possible, il le dit explicitement.

## 9. Dominance stricte et dominance faible

En mode **strict**, le jeu réduit ne dépend pas de l'ordre d'élimination. En mode **faible**, il peut en dépendre (Exemple 3) : l'utilisateur choisit quel joueur est examiné en premier, et le programme **affiche l'ordre des éliminations suivi**.

## 10. Choix du mode pour les exemples du TP

Pour les exemples du TP, le mode est imposé par l'énoncé, le programme ne le demande donc pas : Exemple 1 strict ; Exemple 2 strict puis faible ; Exemple 3 strict, puis faible avec les deux ordres ; Exemple 4 strict ; Exemple 5 strict puis faible. Pour un jeu saisi par l'utilisateur (clavier, fichier, aléatoire), c'est l'utilisateur qui choisit le mode (R4).

## 11. Couverture des exigences

| Exig. | Exigence | État | Où |
|---|---|---|---|
| R1 | n joueurs, kᵢ stratégies, clavier / fichier / aléatoire | Fait | `input_keyboard`, `input_file`, `input_random` |
| R2 | Matrice pour 2 joueurs, une matrice par combinaison pour 3 et plus | Fait | `display_game` |
| R3 | Dominance stricte | Fait | `dominates` (strict) |
| R4 | Dominance faible, mode choisi par l'utilisateur | Fait | `dominates` (faible), `choose_mode` |
| R5 | Élimination itérée avec trace | Fait | `iterated_elimination` |
| R6 | Jeu final + « un seul profil ou non » | Fait | fin de `iterated_elimination` |

## 12. Résultats sur les jeux de test

Produits par `python code.py --test` (9 cas, tous réussis).

| Jeu | Mode | Attendu | Obtenu |
|---|---|---|---|
| Exemple 1 | strict | (H, C), gains (2, 3) | OK : D (par G), M (par H), B (par H), G (par C) |
| Exemple 2 | strict | aucune élimination, 3×3 | OK, message clair |
| Exemple 2 | faible | aucune élimination, 3×3 | OK |
| Exemple 3 | strict | D supprimée, 2×2 (G, M) | OK |
| Exemple 3 | faible, joueur 1 d'abord | H × {G, M} | OK : B (par H), puis D (par G) |
| Exemple 3 | faible, joueur 2 d'abord | {H, B} × G | OK : M (par G), puis D (par G) |
| Exemple 4 (3 joueurs) | strict | (N, N, N), gains (0, 0, 0) | OK |
| Exemple 5 | strict | (A3, B3), gains (5, 3) | OK : B2 (par B3), A2 (par A1), B1 (par B3), A1 (par A3) |
| Exemple 5 | faible | (A3, B3), gains (5, 3) | OK |

Vérifications supplémentaires : le jeu « contribuer ou non » avec 4 et 5 joueurs donne (N, N, N, N) et (N, N, N, N, N) ; un jeu aléatoire à 4 joueurs avec 2, 3, 2, 2 stratégies est affiché correctement sous forme de matrices étiquetées avec des vecteurs de 4 gains.

## 13. Limites

- Stratégies pures uniquement, comme indiqué dans le TP.
- Le nombre de profils croît en kⁿ : la saisie manuelle au clavier devient impraticable pour les grands jeux (préférer la génération aléatoire ou un fichier JSON).
- En mode faible, le programme suit un seul ordre d'élimination (choix de l'utilisateur) et n'énumère pas tous les ordres possibles.

## 14. Conclusion

Le programme répond aux exigences R1 à R6, fonctionne pour un nombre quelconque de joueurs et de stratégies, montre chaque étape d'élimination et reproduit tous les résultats attendus du TP, y compris la dépendance à l'ordre de la dominance faible (Exemple 3).