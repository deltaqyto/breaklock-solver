import math
import random
import matplotlib.pyplot as plt
from time import time
import contextlib


def draw_sol(sol, grid_size):
    max_len = len(str(grid_size[0] * grid_size[1])) + 1
    print(("-" * max_len * grid_size[0])[:-1])
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            if grid_size[1] * y + x in sol:
                print(f"{sol.index(grid_size[1] * y + x) + 1}" + " " * (max_len - len(str(sol.index(grid_size[1] * y + x) + 1))), end="")
            else:
                print("." + " " * (max_len - 1), end="")
        print()
    print(("-" * max_len * grid_size[0])[:-1])


def get_all_sols(grid_size: (int, int), max_len: int) -> list:
    """
    Return all solutions to the android problem as a list
    :param grid_size: (x, y) size of the grid
    :param max_len: maximum number of nodes in the solution
    """
    sols = []

    def r_sols(current_sol):
        current_y = current_sol[-1] // grid_size[1]        # The solution values are stored as ids ->>   0, 1, 2     for an example 3x3 grid
        current_x = current_sol[-1] - current_y * grid_size[1]  # Cache x and y of last visited node     3, 4, 5
        grid = {}  # Prepping a dict to store options for travelling                                     6, 7, 8
        grid_id = -1

        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                grid_id += 1
                if grid_id in current_sol:  # Avoid using the same node twice
                    continue
                dist = (x - current_x) ** 2 + (y - current_y) ** 2   # Find some kind of distance, no need to root since all values will be like this
                slope = math.atan2((y - current_y), (x - current_x))  # Likely very slow, but need to hold some kind of slope value,
                # so that jumping over a point can be detected

                # If the option table doesnt have the slope add a new entry with distance and id
                # if it does, check distances and pick the closer one
                grid[slope] = (dist, grid_id) if grid.get(slope) is None or grid[slope][0] > dist else grid[slope]

        # The code matches the android login criteria, since:
        # - Each node is visited either 0 or 1 time(s)
        # - The path can travel to any other node within line of sight
        # - The path cannot jump over unvisited nodes, but can over visited ones
        # - The path is not a cycle
        # - The path abides the max length cap

        r_sol = [current_sol]
        if len(current_sol) == max_len:  # Stop if hit the max length and return
            return r_sol

        for _, opt in grid.values():  # Else recurse for each possible choice
            r_sol += r_sols(current_sol + [opt])
        return r_sol

    for start in range(grid_size[0] * grid_size[1]):
        sols += r_sols([start])
    return sols


def evaluate(trial, target):
    assert len(trial) == len(target)
    whites = 0
    for a, b in zip(trial, target):
        whites += a == b
    blacks = 0
    for a in trial:
        if a in target:
            blacks += 1

    return blacks - whites, whites


def narrow_sols(sol_list, target, blacks, whites):
    new_sols = [sol for sol in sol_list if (blacks, whites) == evaluate(sol, target)]
    return new_sols


def main(mode="solve", auxmode="normal"):
    grid_dims = 3, 3
    sol_len = 6
    sol_dict = {}
    if mode != "test":
        print(f"Loading for a {grid_dims[0]} x {grid_dims[1]} game")
        sols = get_all_sols(grid_dims, sol_len)
        sol_dict = {i: [] for i in range(1, 10)}
        for sol in sols:
            sol_dict[len(sol)].append(sol)

    if mode == "solve":
        working_sols = sol_dict[sol_len]

        while True:
            print(f"There {'are' if len(working_sols) != 1 else 'is only'} {len(working_sols)} solution{'s' if len(working_sols) != 1 else ''}. "
                  f"Draw the following:")
            guess = random.choice(working_sols)
            print(draw_sol(guess, grid_dims))

            inval = input("Result (b, w): ")
            if not inval:
                break
            inval = inval.split(",")
            print(inval)
            try:
                blacks = int(inval[0])
                whites = int(inval[1])
                assert 0 <= blacks <= sol_len and 0 <= whites <= sol_len and 0 <= blacks + whites <= sol_len
            except AssertionError:
                print("Input not in accepted range")
                continue
            except ValueError:
                print("Couldn't process input: Bad values")
                continue
            except IndexError:
                print("Couldn't process input: Not enough values")
                continue

            working_sols = narrow_sols(working_sols, guess, blacks, whites)

    elif mode == "play":
        tries = 0
        working_sols = sol_dict[sol_len]
        solution = random.choice(working_sols)
        print(f"Try to find the length {sol_len} solution")
        print("Type help to get a possible solution given your past answers (this will cost an extra point)\n"
              "Type stats to see how close you are to a solution")

        while True:
            tries += 1
            draw_sol(list(range(grid_dims[0] * grid_dims[1])), grid_dims)
            inval = input("Guess: ") if auxmode != "walkthrough" else ', '.join([str(h + 1) for h in random.choice(working_sols)])
            if auxmode == "walkthrough":
                print(f"Guess: {inval}")
            if not inval:
                break
            if inval == "stats":
                prob = math.ceil(len(working_sols) / len(sol_dict[sol_len]) * 100)
                print(f"{len(working_sols)} out of {len(sol_dict[sol_len])} "
                      f"possible solutions are valid, based on your past guesses. "
                      f"That's {'only ' if prob <= 10 else ''}{prob}% of the possibilities remaining")
                tries -= 1
                continue
            if inval == "help":
                help_val = random.choice(working_sols)
                print(f"Drawn below is a possible solution: {[h + 1 for h in help_val]}")
                draw_sol(help_val, grid_dims)

                continue
            inval = inval.split(",")
            if len(inval) != sol_len:
                print(f"That guess is not the right size, enter one of size {sol_len}")
                tries -= 1
                continue
            try:
                inval = [int(i) - 1 for i in inval]
            except ValueError:
                print("The input could not be processed: Bad values")
                tries -= 1
                continue
            if inval not in sol_dict[sol_len]:
                print("That is not a valid combination of points.")
                tries -= 1
                continue
            blacks, whites = evaluate(inval, solution)
            working_sols = narrow_sols(working_sols, inval, blacks, whites)
            if whites == sol_len:
                print(f"Solution {', '.join([str(i + 1) for i in inval])} is correct")
                draw_sol(solution, grid_dims)
                break
            if auxmode == "walkthrough":
                prob = math.ceil(len(working_sols) / len(sol_dict[sol_len]) * 100)
                print(f"{len(working_sols)} out of {len(sol_dict[sol_len])} "
                      f"possible solutions are valid, based on past guesses. "
                      f"That's {'only ' if prob <= 10 else ''}{prob}% of the possibilities remaining")
                print()
            print(f"{'Your s' if auxmode != 'walkthrough' else 'S'}olution {', '.join([str(i + 1) for i in inval])} "
                  f"{f'matches partially' if blacks != 0 or whites != 0 and whites != sol_len else 'does not match'}\n"
                  f"Blacks: {blacks}, Whites: {whites}")
        print(f"You finished in {tries} turns")
        return tries

    elif mode == "test":
        print("Running generation test")
        for i in range(1, sol_len + 1):
            t = time()
            sols = get_all_sols(grid_dims, i)
            t = time() - t
            sol_dict = {i: [] for i in range(1, 10)}
            for sol in sols:
                sol_dict[len(sol)].append(sol)
            print(f"  Paths of {i} nodes took {round(t, 4)} seconds, with {len(sol_dict[i])} paths")
        print("Running game skill test")
        tries_count = {}
        for i in range(200):
            if not i % 10:
                print(f"  Starting game #{i}")

            with contextlib.redirect_stdout(None):
                tries = main("play", "walkthrough")

            if tries not in tries_count:
                tries_count[tries] = 0
            tries_count[tries] += 1
        print(tries_count)
        print(f"Expected turns:{sum([k * v for k, v in tries_count.items()])/sum(tries_count.values())}")

        fig, axs = plt.subplots()
        axs.bar(tries_count.keys(), tries_count.values())
        plt.show()

    elif mode == "cheat":
        tries = 0
        working_sols = sol_dict[sol_len]
        solution = random.choice(working_sols)
        print(solution)
        print(f"Try to find the length {sol_len} solution")
        print("Type help to get a possible solution given your past answers (this will cost an extra point)\n"
              "Type stats to see how close you are to a solution")

        while True:
            tries += 1
            draw_sol(list(range(grid_dims[0] * grid_dims[1])), grid_dims)
            inval = input("Guess: ") if auxmode != "walkthrough" else ', '.join([str(h + 1) for h in random.choice(working_sols)])
            if auxmode == "walkthrough":
                print(f"Guess: {inval}")
            if not inval:
                break
            if inval == "stats":
                prob = math.ceil(len(working_sols) / len(sol_dict[sol_len]) * 100)
                print(f"{len(working_sols)} out of {len(sol_dict[sol_len])} "
                      f"possible solutions are valid, based on your past guesses. "
                      f"That's {'only ' if prob <= 10 else ''}{prob}% of the possibilities remaining")
                tries -= 1
                continue
            if inval == "help":
                help_val = random.choice(working_sols)
                print(f"Drawn below is a possible solution: {[h + 1 for h in help_val]}")
                draw_sol(help_val, grid_dims)

                continue
            inval = inval.split(",")
            if len(inval) != sol_len:
                print(f"That guess is not the right size, enter one of size {sol_len}")
                tries -= 1
                continue
            try:
                inval = [int(i) - 1 for i in inval]
            except ValueError:
                print("The input could not be processed: Bad values")
                tries -= 1
                continue
            if inval not in sol_dict[sol_len]:
                print("That is not a valid combination of points.")
                tries -= 1
                continue
            blacks, whites = evaluate(inval, solution)
            if whites == sol_len and len(working_sols) == 1:
                print(f"Solution {', '.join([str(i + 1) for i in inval])} is correct")
                draw_sol(solution, grid_dims)
                break
            else:
                working_sols.remove(inval)
                solution = random.choice(working_sols)
                blacks, whites = evaluate(inval, solution)
                print(solution)
            working_sols = narrow_sols(working_sols, inval, blacks, whites)
                
            if auxmode == "walkthrough":
                prob = math.ceil(len(working_sols) / len(sol_dict[sol_len]) * 100)
                print(f"{len(working_sols)} out of {len(sol_dict[sol_len])} "
                      f"possible solutions are valid, based on past guesses. "
                      f"That's {'only ' if prob <= 10 else ''}{prob}% of the possibilities remaining")
                print()
            print(f"{'Your s' if auxmode != 'walkthrough' else 'S'}olution {', '.join([str(i + 1) for i in inval])} "
                  f"{f'matches partially' if blacks != 0 or whites != 0 and whites != sol_len else 'does not match'}\n"
                  f"Blacks: {blacks}, Whites: {whites}")
        print(f"You finished in {tries} turns")
        return tries


if __name__ == "__main__":
    main("solve", "normal")
