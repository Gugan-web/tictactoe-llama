import tkinter as tk
from tkinter import messagebox
import threading
import random
import warnings

warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module=r"autogen\.oai\.gemini",
)
warnings.filterwarnings(
    "ignore",
    message=r"flaml\.automl is not available\..*",
    category=UserWarning,
)

from autogen import ConversableAgent

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Classic")
        self.root.geometry("400x600")
        self.root.configure(bg="#ffffff")
        self.root.resizable(False, False)

        # Style colors (based on user image)
        self.c_green = "#1a5b20"
        self.c_orange = "#c27a0e"
        self.c_btn = "#b37617"

        # Game state
        self.board = [""] * 9
        self.game_over = False
        self.turn = 1 # 1 = human, 2 = AI
        self.human_symbol = "X"
        self.ai_symbol = "O"

        # Ollama Agent Configuration
        ollama_config = {
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "price": [0, 0],
        }
        self.ai_agent = ConversableAgent(
            name="Classic_TTT_AI",
            system_message=(
                "You are playing Tic Tac Toe. Identify the board state and reply ONLY with a single digit (0-8).\n"
                "0|1|2\n3|4|5\n6|7|8\n"
                "Choose the best available square to win or block."
            ),
            llm_config={"config_list": [ollama_config], "cache_seed": None},
        )

        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        # Title
        self.lbl_title = tk.Label(self.root, text="TIC TAC TOE", font=("Comic Sans MS", 32, "bold"), fg=self.c_green, bg="#ffffff")
        self.lbl_title.pack(pady=(20, 10))

        # Name Input Frame
        frame_name = tk.Frame(self.root, bg="#ffffff")
        frame_name.pack(pady=5)
        
        tk.Label(frame_name, text="Name:", font=("Arial", 12), fg=self.c_green, bg="#ffffff").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value="Player")
        self.entry_name = tk.Entry(frame_name, textvariable=self.name_var, font=("Arial", 12), width=15)
        self.entry_name.pack(side=tk.LEFT, padx=5)

        # Canvas for Board
        self.canvas_size = 240
        self.cell_size = self.canvas_size // 3
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Status Label
        self.lbl_status = tk.Label(self.root, text="", font=("Comic Sans MS", 18, "bold"), fg=self.c_green, bg="#ffffff")
        self.lbl_status.pack(pady=(5, 10))

        # Restart Button
        self.btn_restart = tk.Button(
            self.root, text="Restart", font=("Arial", 14), bg=self.c_btn, fg="black",
            activebackground="#8a5b11", relief=tk.FLAT, width=10, command=self.reset_game
        )
        self.btn_restart.pack(pady=10)

    def draw_grid(self):
        self.canvas.delete("all")
        # Draw vertical lines
        self.canvas.create_line(self.cell_size, 0, self.cell_size, self.canvas_size, fill=self.c_orange, width=4)
        self.canvas.create_line(self.cell_size*2, 0, self.cell_size*2, self.canvas_size, fill=self.c_orange, width=4)
        # Draw horizontal lines
        self.canvas.create_line(0, self.cell_size, self.canvas_size, self.cell_size, fill=self.c_orange, width=4)
        self.canvas.create_line(0, self.cell_size*2, self.canvas_size, self.cell_size*2, fill=self.c_orange, width=4)

        # Draw pieces
        for idx, val in enumerate(self.board):
            if val == "X":
                self.draw_x(idx)
            elif val == "O":
                self.draw_o(idx)

    def draw_x(self, idx):
        row = idx // 3
        col = idx % 3
        pad = 20
        x0 = col * self.cell_size + pad
        y0 = row * self.cell_size + pad
        x1 = (col + 1) * self.cell_size - pad
        y1 = (row + 1) * self.cell_size - pad
        self.canvas.create_line(x0, y0, x1, y1, fill=self.c_orange, width=3)
        self.canvas.create_line(x0, y1, x1, y0, fill=self.c_orange, width=3)

    def draw_o(self, idx):
        row = idx // 3
        col = idx % 3
        pad = 20
        x0 = col * self.cell_size + pad
        y0 = row * self.cell_size + pad
        x1 = (col + 1) * self.cell_size - pad
        y1 = (row + 1) * self.cell_size - pad
        self.canvas.create_oval(x0, y0, x1, y1, outline=self.c_orange, width=3)

    def on_canvas_click(self, event):
        if self.game_over or self.turn == 2:
            return

        col = event.x // self.cell_size
        row = event.y // self.cell_size
        idx = row * 3 + col

        if idx >= 0 and idx < 9 and self.board[idx] == "":
            self.board[idx] = self.human_symbol
            self.draw_grid()
            if self.check_win_state(self.human_symbol):
                return
            self.turn = 2
            self.lbl_status.config(text="AI is thinking...")
            # Run AI in background
            threading.Thread(target=self.ai_move_worker, daemon=True).start()

    def ai_move_worker(self):
        b = [x if x else str(i) for i, x in enumerate(self.board)]
        board_str = f"{b[0]}|{b[1]}|{b[2]}\n{b[3]}|{b[4]}|{b[5]}\n{b[6]}|{b[7]}|{b[8]}"
        prompt = f"You are {self.ai_symbol}. The board is:\n{board_str}\nProvide exactly ONE digit (0-8) corresponding to an available square."
        
        try:
            response = self.ai_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
            
            # Parse digit safely
            ai_move = None
            empty_cells = [i for i, x in enumerate(self.board) if x == ""]
            
            for char in str(response):
                if char.isdigit():
                    digit = int(char)
                    if digit in empty_cells:
                        ai_move = digit
                        break
                        
            if ai_move is None and empty_cells:
                ai_move = random.choice(empty_cells)

            if ai_move is not None:
                # Schedule GUI update on main thread
                self.root.after(0, self.apply_ai_move, ai_move)
        except Exception as e:
            self.root.after(0, self.lbl_status.config, {"text": "AI Error. Restart."})

    def apply_ai_move(self, idx):
        self.board[idx] = self.ai_symbol
        self.draw_grid()
        if self.check_win_state(self.ai_symbol):
            return
        self.turn = 1
        self.lbl_status.config(text=f"Your turn, {self.name_var.get()}")

    def check_win_state(self, last_played_symbol):
        win_lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        
        for a, b, c in win_lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.game_over = True
                winner = self.name_var.get() if last_played_symbol == self.human_symbol else "AI"
                self.lbl_status.config(text=f"{winner} wins!")
                return True
                
        if "" not in self.board:
            self.game_over = True
            self.lbl_status.config(text="Draw!")
            return True
            
        return False

    def reset_game(self):
        self.board = [""] * 9
        self.game_over = False
        self.draw_grid()
        
        # Randomise colors/symbols
        self.human_symbol = random.choice(["X", "O"])
        self.ai_symbol = "O" if self.human_symbol == "X" else "X"
        self.turn = random.choice([1, 2])
        
        if self.turn == 1:
            self.lbl_status.config(text=f"Your turn, {self.name_var.get()} ({self.human_symbol})")
        else:
            self.lbl_status.config(text="AI goes first...")
            threading.Thread(target=self.ai_move_worker, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
