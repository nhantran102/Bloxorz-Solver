import tkinter as tk
import time
from .engine import GameState
from .search import bfs, dfs, ucs, astar
import os
from .ai_logger import AILogger
import tracemalloc

# Define color palette for the game grid and elements
COLORS = {
    " ": "#151515", "O": "#d0d0d0", "F": "#ff9933", "G": "#33cc66",
}

class BloxorzApp:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Bloxorz - AI Solver (JSON)")
        self.root.configure(bg="#111111")
        self.root.geometry("1100x760")
        self.logger = AILogger()

        # List of JSON files representing levels
        self.levels = [
            "levels/level0.json", "levels/level1.json", "levels/level2.json", "levels/level3.json",
            "levels/level4.json", "levels/level5.json", "levels/level6.json", "levels/level7.json",
            "levels/level8.json", "levels/level9.json", "levels/level10.json", "levels/level11.json", "levels/level12.json",
            "levels/level13.json"
        ]
        self.level_index = 0
        self.game = None
        self.moves = 0
        self.solving = False
        self.solution_path = []
        self.failed = False
        
        self._build_ui()
        self._bind_keys()
        self._load_level(self.level_index)

    def _build_ui(self):
        # Create main layout containers
        self.main = tk.Frame(self.root, bg="#111111")
        self.main.pack(fill="both", expand=True)

        # Game display area
        self.canvas = tk.Canvas(self.main, bg="#111111", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True, padx=16, pady=16)

        # Sidebar control panel
        self.sidebar = tk.Frame(self.main, bg="#1a1a1a", width=250)
        self.sidebar.pack(side="right", fill="y", padx=16, pady=16)

        # Sidebar labels
        tk.Label(self.sidebar, text="Bloxorz", bg="#1a1a1a", fg="#f5f5f5", font=("Segoe UI", 22, "bold")).pack(pady=(18, 8))
        self.level_label = tk.Label(self.sidebar, bg="#1a1a1a", fg="#dcdcdc", font=("Segoe UI", 14))
        self.level_label.pack(pady=5)
        self.moves_label = tk.Label(self.sidebar, bg="#1a1a1a", fg="#f5f5f5", font=("Segoe UI", 12))
        self.moves_label.pack(pady=5)
        self.status_label = tk.Label(self.sidebar, bg="#1a1a1a", fg="#f1c40f", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(pady=10)

        # Basic game controls
        tk.Button(self.sidebar, text="Reset (R)", command=self.reset_level, bg="#2c2c2c", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Button(self.sidebar, text="Prev Level (back) ", command=self.prev_level, bg="#2c2c2c", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Button(self.sidebar, text="Next Level (Enter)", command=self.next_level, bg="#2c2c2c", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)

        # --- TÁCH KHỐI ---
        tk.Label(self.sidebar, text="Tách khối", bg="#1a1a1a", fg="#a0a0a0", font=("Segoe UI", 10)).pack(pady=(20, 5))
        tk.Button(self.sidebar, text="Tách / Hợp nhất (Space)", command=self.on_split_key, bg="#c0392b", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Button(self.sidebar, text="Đổi khối (Tab)", command=self.on_toggle_key, bg="#7f8c8d", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Label(self.sidebar, text="Nằm ngang/dọc rồi Space để tách.\nTab đổi khối, Space để hợp nhất\nkhi 2 khối kề nhau.",
                 bg="#1a1a1a", fg="#7a7a7a", font=("Segoe UI", 8), justify="left").pack(pady=(2, 5), padx=15)

        tk.Label(self.sidebar, text="AI Solvers", bg="#1a1a1a", fg="#a0a0a0", font=("Segoe UI", 10)).pack(pady=(20, 5))

        # AI Algorithm selection buttons
        tk.Button(self.sidebar, text="Solve with BFS", command=lambda: self.run_solver("BFS"), bg="#2980b9", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Button(self.sidebar, text="Solve with DFS", command=lambda: self.run_solver("DFS"), bg="#27ae60", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Button(self.sidebar, text="Solve with UCS", command=lambda: self.run_solver("UCS"), bg="#8e44ad", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)
        tk.Button(self.sidebar, text="Solve with A*", command=lambda: self.run_solver("A*"), bg="#d35400", fg="white", relief="flat").pack(fill="x", padx=15, pady=3)

    def _bind_keys(self):
        # Keyboard shortcuts for player movement
        self.root.bind("<Up>", lambda e: self.move("UP"))
        self.root.bind("<Down>", lambda e: self.move("DOWN"))
        self.root.bind("<Left>", lambda e: self.move("LEFT"))
        self.root.bind("<Right>", lambda e: self.move("RIGHT"))
        self.root.bind("<r>", lambda e: self.reset_level())
        self.root.bind("<Return>", lambda e: self.next_level())
        self.root.bind("<BackSpace>", lambda e: self.prev_level())
        # Tách khối: Space = tách / hợp nhất, Tab = đổi khối con đang điều khiển
        self.root.bind("<space>", lambda e: self.on_split_key())
        self.root.bind("<Tab>", lambda e: self.on_toggle_key())

    def _load_level(self, index):
        # Clear canvas
        self.canvas.delete("all")

        # Reset state variables
        self.solving = False
        self.solution_path = []
        self.failed = False
        self.moves = 0
        self.level_index = index % len(self.levels)
        
        # Load the level from the engine
        self.game = GameState(self.levels[self.level_index])
        
        # UI updates
        self.status_label.config(text="Ready", fg="#f1c40f")
        self._update_labels()
        self._redraw()

    def run_solver(self, algo_name):
        # Do not run if there is no game loaded, the game is already won, or the AI is currently solving
        if not self.game or self.game.check_win() or self.solving: return
        
        # Update UI to show that the computation has started
        self.status_label.config(text=f"Computing {algo_name}...", fg="#9b59b6")
        self.root.update() 
        
        # Map the selected algorithm name to its corresponding function
        algorithm = {"BFS": bfs, "DFS": dfs, "UCS": ucs, "A*": astar}.get(algo_name)
        
        # --- START METRICS COLLECTION ---
        tracemalloc.start() # Start tracking memory allocation
        start_time = time.time() # Record the start time
        
        # Execute the chosen search algorithm
        path = algorithm(self.game)
        
        # --- END METRICS COLLECTION ---
        elapsed = time.time() - start_time # Calculate total execution time
        current_mem, peak_memory = tracemalloc.get_traced_memory() # Get memory usage stats
        tracemalloc.stop() # Stop tracking memory
        
        if path:
            self.solving = True
            self.solution_path = path
            
            # Log the performance data to the JSON file
            # Temporarily set nodes_expanded to 0 if you haven't counted nodes in search.py yet
            nodes_expanded = 0 
            self.logger.log_result(self.level_index, algo_name, elapsed, peak_memory, nodes_expanded, len(path))
            
            # Update UI with the success status and start auto-playing the solution
            self.status_label.config(text=f"Found: {len(path)} moves ({elapsed:.2f}s)", fg="#2ecc71")
            self.play_solution()
        else:
            # Update UI if the algorithm fails to find a solution
            self.status_label.config(text="No solution found!", fg="#e74c3c")

    def play_solution(self):
        # Automate the moves found by the AI
        if not self.solution_path or not self.solving:
            self.solving = False
            if self.game.check_win():
                self.status_label.config(text="AI SUCCESS!", fg="#2ecc71")
            return
            
        move = self.solution_path.pop(0)
        self.move(move, is_ai=True)
        self.root.after(200, self.play_solution) # Delay between auto-moves

    def reset_level(self): self._load_level(self.level_index)
    def next_level(self): self._load_level(self.level_index + 1)
    def prev_level(self): self._load_level(self.level_index - 1)

    def on_split_key(self):
        # Space: tách khối (khi đang là 1 khối nằm) hoặc hợp nhất (khi 2 khối con kề nhau)
        if not self.game or self.failed or self.game.check_win(): return
        if self.game.is_split():
            if self.game.try_rejoin():
                self.moves += 1
                self.status_label.config(text="Đã hợp nhất khối", fg="#f1c40f")
                if self.game.check_win():
                    self.status_label.config(text="YOU WIN!", fg="#2ecc71")
            else:
                self.status_label.config(text="2 khối chưa kề nhau!", fg="#e67e22")
        else:
            if self.game.do_split():
                self.status_label.config(text="Đã tách khối — Tab để đổi khối", fg="#3498db")
            else:
                self.status_label.config(text="Chỉ tách khi khối đang NẰM", fg="#e67e22")
        self._update_labels()
        self._redraw()

    def on_toggle_key(self):
        # Tab: đổi khối con đang điều khiển (khi đã tách)
        if self.game and self.game.is_split() and not self.failed and not self.game.check_win():
            self.game.toggle_active()
            self._redraw()
        return "break"  # chặn Tab chuyển focus giữa các widget

    def move(self, direction, is_ai=False):
        # Ignore moves if game is already won or lost
        if not self.game or self.game.check_win() or self.failed: return

        # Chế độ đã tách: điều khiển khối con đang active
        if self.game.is_split():
            result = self.game.move_split(direction)
            if result == "fell":
                self.failed = True
                self._redraw()
                return
            if result == "blocked":
                return  # bị chặn, không tính là một nước đi, không thua
            self.moves += 1
            self._update_labels()
            self._redraw()
            return

        # Attempt to update game state; if return is False, the player failed/fell
        if not self.game.update_move(direction):
            self.failed = True
            self._redraw()
            return

        self.moves += 1
        if self.game.check_win():
            self.status_label.config(text="YOU WIN!", fg="#2ecc71")

        self._update_labels()
        self._redraw()

    def _update_labels(self):
        self.level_label.config(text=f"Level {self.level_index + 1} / {len(self.levels)}")
        self.moves_label.config(text=f"Moves: {self.moves}")

    def _redraw(self):
        # 1. First-time render: Calculate cell dimensions and draw fixed elements
        if not self.canvas.find_withtag("tile"):
            self.root.update_idletasks()
            canvas_width = max(self.canvas.winfo_width(), 600)
            canvas_height = max(self.canvas.winfo_height(), 600)
            self.cell_size = max(min(canvas_width // max(self.game.cols, 1), canvas_height // max(self.game.rows, 1)), 35)
            self.offset_x = (canvas_width - self.game.cols * self.cell_size) // 2
            self.offset_y = (canvas_height - self.game.rows * self.cell_size) // 2

            for r in range(self.game.rows):
                for c in range(self.game.cols):
                    cell = self.game.grid[r][c]
                    x1, y1 = self.offset_x + c * self.cell_size, self.offset_y + r * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    
                    fill_color = COLORS.get(cell, "#151515")
                    if fill_color != "#151515":
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="#3d3d3d", tags="tile")
                        
                        # Draw Goal (G) or Finish (F) labels
                        if cell == "G": self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="T", font=("Segoe UI", 16, "bold"), fill="#0b3d1f", tags="tile")
                        elif cell == "F": self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="O", font=("Segoe UI", 14, "bold"), fill="#6b3e00", tags="tile")

        # 2. Dynamic content: Clear only movable/changable objects (switches, block, bridges)
        self.canvas.delete("dynamic")

        # Draw switches
        for switch in self.game.switches:
            sr, sc = switch["pos"]
            x1, y1 = self.offset_x + sc * self.cell_size, self.offset_y + sr * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            color = "#6bb7ff" if switch["type"] == "soft" else "#365a9c"
            self.canvas.create_oval(x1+8, y1+8, x2-8, y2-8, fill=color, outline="", tags="dynamic")

        # Draw the block (đã tách -> vẽ 2 khối con, khối đang điều khiển được tô sáng + viền vàng)
        if self.game.is_split():
            for i, (r, c) in enumerate(self.game.split_cells):
                x1, y1 = self.offset_x + c * self.cell_size, self.offset_y + r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                fill = "#ff6b6b" if i == self.game.active else "#8e2b2b"
                self.canvas.create_rectangle(x1+6, y1+6, x2-6, y2-6, fill=fill, outline="#000000", width=2, tags="dynamic")
                if i == self.game.active:
                    self.canvas.create_rectangle(x1+3, y1+3, x2-3, y2-3, outline="#f1c40f", width=3, tags="dynamic")
        else:
            for r, c in self.game.block.get_occupied_cells():
                x1, y1 = self.offset_x + c * self.cell_size, self.offset_y + r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1+3, y1+3, x2-3, y2-3, fill="#d63031", outline="#000000", width=2, tags="dynamic")

        # Draw bridges based on their current state
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                if self.game.grid[r][c].startswith("B_"):
                    x1, y1 = self.offset_x + c * self.cell_size, self.offset_y + r * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    fill = "#d0d0d0" if self.game.bridges_state.get(self.game.grid[r][c], False) else "#151515"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#3d3d3d", tags="dynamic")

        # 3. Check for Win or Game Over states and draw overlay if necessary
        if self.game and self.game.check_win():
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()

            self.canvas.create_rectangle(0, 0, w, h, fill="#000000", stipple="gray50", tags="dynamic")
            self.canvas.create_text(w//2, h//2 - 40, text="YOU WIN!", fill="#2ecc71", font=("Segoe UI", 42, "bold"), tags="dynamic")
            self.canvas.create_text(w//2, h//2 + 30, text="Press Enter for next level", fill="white", font=("Segoe UI", 22), tags="dynamic")

        elif self.failed:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()

            self.canvas.create_rectangle(0, 0, w, h, fill="#000000", stipple="gray50", tags="dynamic")
            self.canvas.create_text(w//2, h//2 - 40, text="GAME OVER", fill="#e74c3c", font=("Segoe UI", 42, "bold"), tags="dynamic")
            self.canvas.create_text(w//2, h//2 + 30, text="Press R to reset", fill="white", font=("Segoe UI", 22), tags="dynamic")

    def run(self):
        # Start the main event loop
        self.root.mainloop()