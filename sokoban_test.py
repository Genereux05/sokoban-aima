from sokoban import SokobanProblem
from aima3.search import astar_search, breadth_first_graph_search
import tkinter as tk
from tkinter import simpledialog, messagebox
import time

CELL_SIZE = 40

COLOR_MAP = {
    '#': 'black',     # Mur
    ' ': 'white',     # Sol
    '@': 'blue',      # Joueur
    '$': 'brown',     # Boîte
    '.': 'lightgreen',# Cible
    '*': 'orange',    # Boîte sur cible
    '+': 'lightblue'  # Joueur sur cible
}

def load_level_with_goals(init_path, goal_path):
    with open(init_path, 'r') as f:
        init = [list(line) for line in f.read().strip().split('\n')]

    with open(goal_path, 'r') as f:
        goals = [list(line) for line in f.read().strip().split('\n')]

    for i in range(len(init)):
        for j in range(len(init[i])):
            if goals[i][j] == '.':
                if init[i][j] == ' ':
                    init[i][j] = '.'
                elif init[i][j] == '$':
                    init[i][j] = '*'
                elif init[i][j] == '@':
                    init[i][j] = '+'

    return tuple(tuple(row) for row in init)

class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban - AIMA")

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.run_button = tk.Button(root, text="Résoudre le niveau", command=self.solve)
        self.run_button.pack(pady=10)

        self.state = None
        self.problem = None
        self.cell_size = CELL_SIZE

        self.load_level()

    def load_level(self):
        niveau = simpledialog.askinteger("Niveau", "Choisissez un niveau (1 à 15) :", minvalue=1, maxvalue=15)
        methode = simpledialog.askinteger("Méthode", "1 = BFS, 2 = A* :", minvalue=1, maxvalue=2)
        self.methode_num = methode

        init_path = f"levels/sokoInst{niveau}.init"
        goal_path = f"levels/sokoInst{niveau}.goal"

        self.state = load_level_with_goals(init_path, goal_path)
        self.problem = SokobanProblem(self.state)

        self.draw_state(self.state)

    def draw_state(self, state):
        self.canvas.delete("all")
        for y, row in enumerate(state):
            for x, cell in enumerate(row):
                color = COLOR_MAP.get(cell, 'grey')
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=color, outline='grey'
                )

    def solve(self):
        self.run_button.config(state='disabled')

        start_time = time.time()
        if self.methode_num == 1:
            result = breadth_first_graph_search(self.problem)
        else:
            result = astar_search(self.problem)
        end_time = time.time()

        if result is None:
            messagebox.showinfo("Résultat", "Aucune solution trouvée.")
            self.run_button.config(state='normal')
            return

        actions = result.solution()
        current = self.state

        self.animate_solution(current, actions, 0, end_time - start_time)

    def animate_solution(self, current, actions, index, duration):
        if index >= len(actions):
            messagebox.showinfo("Terminé", f"Résolu en {len(actions)} étapes.\nTemps : {duration:.2f}s\nNoeuds explorés : {self.problem.node_count}")
            self.run_button.config(state='normal')
            return

        current = self.problem.result(current, actions[index])
        self.draw_state(current)
        self.root.after(300, self.animate_solution, current, actions, index + 1, duration)

if __name__ == "__main__":
    root = tk.Tk()
    app = SokobanGUI(root)
    root.mainloop()
