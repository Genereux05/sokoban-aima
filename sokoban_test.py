from sokoban import SokobanProblem
from aima3.search import astar_search, breadth_first_graph_search
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import time
import os

CELL_SIZE = 40
SPRITE_PATH = "assets"

class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban - AIMA avec GUI")

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.run_button = tk.Button(root, text="Résoudre le niveau", command=self.solve)
        self.run_button.pack(pady=10)

        self.state = None
        self.problem = None
        self.cell_size = CELL_SIZE
        self.images = {}

        self.load_images()
        self.load_level()

    def load_images(self):
        def load(path):
            img = Image.open(os.path.join(SPRITE_PATH, path))
            return ImageTk.PhotoImage(img.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS))

        self.images = {
            '#': load("wall.png"),
            ' ': load("floor.png"),
            '@': load("player.png"),
            '$': load("box.png"),
            '.': load("goal.png"),
            '*': load("box_on_goal.png"),
            '+': load("player_on_goal.png")
        }

    def load_level(self):
        niveau = simpledialog.askinteger("Niveau", "Choisissez un niveau (1 à 15) :", minvalue=1, maxvalue=15)
        methode = simpledialog.askinteger("Méthode", "1 = BFS, 2 = A* :", minvalue=1, maxvalue=2)
        self.methode_num = methode

        init_path = f"levels/sokoInst{niveau}.init"
        goal_path = f"levels/sokoInst{niveau}.goal"

        self.state = self.load_level_with_goals(init_path, goal_path)
        self.problem = SokobanProblem(self.state)

        self.canvas.config(width=len(self.state[0]) * self.cell_size, height=len(self.state) * self.cell_size)
        self.draw_state(self.state)

    def load_level_with_goals(self, init_path, goal_path):
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

    def draw_state(self, state):
        self.canvas.delete("all")
        for y, row in enumerate(state):
            for x, cell in enumerate(row):
                image = self.images.get(cell, self.images[' '])
                self.canvas.create_image(
                    x * self.cell_size + self.cell_size // 2,
                    y * self.cell_size + self.cell_size // 2,
                    image=image
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
