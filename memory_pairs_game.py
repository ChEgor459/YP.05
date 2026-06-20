import tkinter as tk
from tkinter import Frame, Label, Button
from stats_manager import update
import random


class MemoryPairsGame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        self.main_container = Frame(self, bg="#0000FF")
        self.main_container.pack(expand=True, fill="both")

        # ===== TOP =====
        top_frame = Frame(self.main_container, bg="#0000FF")
        top_frame.pack(fill="x", pady=(30, 10), padx=40)

        Button(top_frame, text="⏸",
               font=("Arial", 18, "bold"),
               bg="white", width=3,
               command=self.show_pause_menu).pack(side="left")

        self.game_title = Label(top_frame,
                                bg="#0000FF",
                                fg="white",
                                font=("Arial", 36, "bold"))
        self.game_title.pack(side="left", expand=True)

        # ===== STATS =====
        stats_frame = Frame(self.main_container, bg="#0000FF")
        stats_frame.pack(pady=(10, 30))

        self.moves_label = Label(stats_frame, bg="white",
                                 font=("Arial", 16, "bold"))
        self.moves_label.pack(side="left", padx=20)

        self.points_label = Label(stats_frame, bg="white",
                                  font=("Arial", 16, "bold"))
        self.points_label.pack(side="left", padx=20)

        # ===== GAME =====
        self.center_frame = Frame(self.main_container, bg="#0000FF")
        self.center_frame.pack(expand=True, fill="both")

        self.game_frame = Frame(self.center_frame, bg="#0000FF")
        self.game_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.overlay = Frame(self.main_container, bg="#0000FF")

        self.update_language()

        self.training_mode = False
        self.training_callback = None

    # ===== LANGUAGE =====
    def update_language(self):
        if self.controller.language == "Русский":
            self.game_title.config(text="Найди пару")
            self.moves_text = "Ходы"
            self.score_text = "Очки"
            self.pause_text = "ПАУЗА"
            self.resume_text = "Продолжить"
            self.menu_text = "Главное меню"
            self.win_text = "ПОБЕДА!"
        else:
            self.game_title.config(text="Find the Pair")
            self.moves_text = "Moves"
            self.score_text = "Score"
            self.pause_text = "PAUSE"
            self.resume_text = "Resume"
            self.menu_text = "Main Menu"
            self.win_text = "YOU WON!"

    def get_difficulty_text(self):
        if self.controller.language == "Русский":
            return {"easy": "Легкий", "medium": "Средний", "hard": "Сложный"}[self.current_difficulty]
        else:
            return {"easy": "Easy", "medium": "Medium", "hard": "Hard"}[self.current_difficulty]

    # ===== START =====
    def start_game(self, difficulty):
        self.controller.in_game = True

        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.hide_overlay()

        self.current_difficulty = difficulty

        self.difficulty_multiplier = {"easy": 1, "medium": 2, "hard": 3}[difficulty]

        rows, cols = {"easy": (3, 2), "medium": (4, 4), "hard": (5, 6)}[difficulty]

        total = rows * cols
        self.total_pairs = total // 2
        self.min_moves = self.total_pairs * 2

        self.found_pairs = 0
        self.moves = 0

        self.update_moves()
        self.update_points()

        for w in self.game_frame.winfo_children():
            w.destroy()

        numbers = list(range(self.total_pairs)) * 2
        random.shuffle(numbers)

        self.cards = numbers
        self.buttons = []
        self.first = None
        self.second = None
        self.lock = False

        index = 0
        for r in range(rows):
            for c in range(cols):
                btn = Button(
                    self.game_frame,
                    text="?",
                    width=6,
                    height=3,
                    font=("Arial", 20, "bold"),
                    bg="white",
                    command=lambda i=index: self.flip(i)
                )
                btn.grid(row=r, column=c, padx=10, pady=10)
                self.buttons.append(btn)
                index += 1

    # ===== GAME =====
    def flip(self, index):
        if self.lock:
            return

        btn = self.buttons[index]
        if btn["text"] != "?":
            return

        btn.config(text=str(self.cards[index]), bg="#ADD8E6")

        if self.first is None:
            self.first = index
            return

        self.second = index
        self.lock = True
        self.moves += 1

        self.update_moves()
        self.update_points()

        self.after(500, self.check)

    def check(self):
        if self.cards[self.first] == self.cards[self.second]:
            for i in [self.first, self.second]:
                self.buttons[i].config(bg="#7CFC00", state="disabled")

            self.found_pairs += 1
            self.update_points()

            if self.found_pairs == self.total_pairs:
                self.end_game()
        else:
            for i in [self.first, self.second]:
                self.buttons[i].config(bg="#ff9999")

            def reset():
                self.buttons[self.first].config(text="?", bg="white")
                self.buttons[self.second].config(text="?", bg="white")
                self.first = self.second = None
                self.lock = False

            self.after(400, reset)
            return

        self.first = None
        self.second = None
        self.lock = False

    # ===== SCORE =====
    def calculate_score(self):
        pairs_bonus = self.found_pairs * 100
        extra_moves = max(0, self.moves - self.min_moves)
        penalty = extra_moves * 10
        return max(0, (pairs_bonus * self.difficulty_multiplier) - penalty)

    def get_current_score(self):
        pairs_bonus = self.found_pairs * 100
        extra_moves = max(0, self.moves - self.min_moves)
        penalty = extra_moves * 10
        return max(0, (pairs_bonus * self.difficulty_multiplier) - penalty)

    def end_game(self):
        self.final_score = self.calculate_score()

        update("pairs", self.current_difficulty, True,
               self.final_score, 0, self.moves,
               self.controller.language)

        # ✅ ИСПРАВЛЕНО ЗДЕСЬ
        if self.training_mode and self.training_callback:
            callback = self.training_callback
            self.training_callback = None
            self.after(300, lambda: callback(self.final_score, self.moves))
            return

        self.show_end()

    # ===== UI =====
    def update_moves(self):
        self.moves_label.config(text=f"{self.moves_text}: {self.moves}")

    def update_points(self):
        self.points_label.config(text=f"{self.score_text}: {self.get_current_score()}")

    # ===== OVERLAY =====
    def show_end(self):
        self.overlay.place(relwidth=1, relheight=1)
        self.overlay.lift()

        for w in self.overlay.winfo_children():
            w.destroy()

        box = Frame(self.overlay, bg="#0000FF", width=700, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        Label(box, text=self.game_title.cget("text"),
              font=("Arial", 36, "bold"),
              bg="#0000FF", fg="white").pack(pady=(20, 5))

        Label(box, text=self.get_difficulty_text(),
              font=("Arial", 24, "bold"),
              bg="#0000FF", fg="white").pack(pady=(0, 20))

        Label(box, text=f"{self.score_text}: {self.final_score}",
              font=("Arial", 20, "bold"),
              bg="#0000FF", fg="white").pack(pady=10)

        Label(box, text=f"{self.moves_text}: {self.moves}",
              font=("Arial", 20, "bold"),
              bg="#0000FF", fg="white").pack(pady=10)

        Button(box, text=self.menu_text,
               font=("Arial", 18, "bold"),
               bg="white", width=18,
               command=self.go_to_main_menu).pack(pady=20)

    def show_pause_menu(self):
        self.show_overlay(self.pause_text, True)

    def show_overlay(self, title, resume=False):
        for w in self.overlay.winfo_children():
            w.destroy()

        self.overlay.place(relwidth=1, relheight=1)
        self.overlay.lift()

        box = Frame(self.overlay, bg="#0000FF", width=700, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        Label(box, text=title,
              font=("Arial", 42, "bold"),
              bg="#0000FF", fg="white").pack(pady=40)

        if resume:
            Button(box, text=self.resume_text,
                   font=("Arial", 18, "bold"),
                   bg="white", width=18,
                   command=self.hide_overlay).pack(pady=15)

        Button(box, text=self.menu_text,
               font=("Arial", 18, "bold"),
               bg="white", width=18,
               command=self.go_to_main_menu).pack(pady=15)

    def hide_overlay(self):
        self.overlay.place_forget()

    def go_to_main_menu(self):
        self.hide_overlay()
        self.controller.in_game = False
        self.controller.play_music_loop()
        self.controller.show_frame("MainMenu")