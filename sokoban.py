from aima3.search import Problem



# Déplacements relatifs
def move_pos(position, direction):
    y, x = position
    if direction == 'UP':
        return y - 1, x
    elif direction == 'DOWN':
        return y + 1, x
    elif direction == 'LEFT':
        return y, x - 1
    elif direction == 'RIGHT':
        return y, x + 1

# Trouver la position du joueur
def find_player_position(state):
    for y, row in enumerate(state):
        for x, cell in enumerate(row):
            if cell == '@':
                return (y, x)
    return None

# Trouver les positions des caisses
def find_boxes_positions(state):
    boxes = set()
    for y, row in enumerate(state):
        for x, cell in enumerate(row):
            if cell == '$':
                boxes.add((y, x))
    return boxes

# Trouver les positions des buts
def find_goal_positions(state):
    goals = set()
    for y, row in enumerate(state):
        for x, cell in enumerate(row):
            if cell == '.':
                goals.add((y, x))
    return goals

class SokobanProblem(Problem):
    def __init__(self, initial_state):
        super().__init__(initial_state)
        self.goal_positions = find_goal_positions(initial_state)
        self.node_count = 0

    def is_deadlock(self, state):
        for y, row in enumerate(state):
            for x, cell in enumerate(row):
                if cell != '$':
                    continue

                if (y, x) in self.goal_positions:
                    continue  # Caisse sur but, pas un deadlock

                # Coin simple (haut-gauche, haut-droit, bas-gauche, bas-droit)
                if ((state[y-1][x] == '#' and state[y][x-1] == '#') or
                    (state[y-1][x] == '#' and state[y][x+1] == '#') or
                    (state[y+1][x] == '#' and state[y][x-1] == '#') or
                    (state[y+1][x] == '#' and state[y][x+1] == '#')):
                    return True

                # Ligne bloquée horizontalement
                if ((state[y][x-1] == '#' or state[y][x+1] == '#') and
                    (state[y-1][x] == '#' and state[y+1][x] == '#')):
                    return True

                # Ligne bloquée verticalement
                if ((state[y-1][x] == '#' or state[y+1][x] == '#') and
                    (state[y][x-1] == '#' and state[y][x+1] == '#')):
                    return True

        return False

    def actions(self, state):
        if self.is_deadlock(state):
            return []  # Pas d’actions si on est dans un état mort

        actions = []
        py, px = find_player_position(state)

        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            dy, dx = move_pos((py, px), direction)
            if not self.in_bounds(dy, dx, state):
                continue

            cell = state[dy][dx]

            if cell == '#':
                continue  # mur

            elif cell in [' ', '.']:  # case vide ou but
                actions.append(direction)

            elif cell == '$':  # caisse
                ddy, ddx = move_pos((dy, dx), direction)
                if self.in_bounds(ddy, ddx, state) and state[ddy][ddx] in [' ', '.']:
                    actions.append(direction)

        return actions

    def in_bounds(self, y, x, state):
        return 0 <= y < len(state) and 0 <= x < len(state[0])

    def result(self, state, action):
        self.node_count += 1
        state = [list(row) for row in state]  # Copie modifiable
        py, px = find_player_position(state)
        dy, dx = move_pos((py, px), action)
        target_cell = state[dy][dx]

        if target_cell == '#':
            return tuple(tuple(row) for row in state)

        if target_cell == '$':
            ddy, ddx = move_pos((dy, dx), action)
            beyond_cell = state[ddy][ddx]

            if beyond_cell in [' ', '.']:
                state[ddy][ddx] = '$'
                state[dy][dx] = ' ' if (dy, dx) not in self.goal_positions else '.'
            else:
                return tuple(tuple(row) for row in state)

        state[py][px] = ' ' if (py, px) not in self.goal_positions else '.'
        state[dy][dx] = '@'

        return tuple(tuple(row) for row in state)

    def goal_test(self, state):
        for y, row in enumerate(state):
            for x, cell in enumerate(row):
                if (y, x) in self.goal_positions and cell != '$':
                    return False
        return True

    def h(self, node):
        boxes = find_boxes_positions(node.state)
        goals = self.goal_positions

        total = 0
        for box in boxes:
            distances = [abs(box[0]-g[0]) + abs(box[1]-g[1]) for g in goals]
            total += min(distances) if distances else 0

        return total
