import tkinter as tk
from tkinter import Frame, Label, Button
from stats_manager import update
import random


class SequenceMemoryGame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        self.main_container = Frame(self, bg="#0000FF")
        self.main_container.pack(expand=True, fill="both")

        top_frame = Frame(self.main_container, bg="#0000FF")
        top_frame.pack(fill="x", pady=(30, 10), padx=40)

        Button(top_frame, text="⏸", font=("Arial", 18, "bold"),
               bg="white", width=3, command=self.pause).pack(side="left")

        self.game_title = Label(top_frame, bg="#0000FF", fg="white",
                                font=("Arial", 36, "bold"))
        self.game_title.pack(side="left", expand=True)

        stats = Frame(self.main_container, bg="#0000FF")
        stats.pack(pady=20)

        self.level_label = Label(stats, bg="white", font=("Arial", 16, "bold"), width=12)
        self.level_label.pack(side="left", padx=20)

        self.points_label = Label(stats, bg="white", font=("Arial", 16, "bold"), width=12)
        self.points_label.pack(side="left", padx=20)

        self.game_frame = Frame(self.main_container, bg="#0000FF")
        self.game_frame.pack(expand=True)

        self.overlay = Frame(self.main_container, bg="#0000FF")

        self.update_language()
        self.training_mode = False
        self.training_callback = None

    def update_language(self):
        if self.controller.language == "Русский":
            self.game_title.config(text="Запомни последовательность")
            self.level_text = "Уровень"
            self.points_text = "Очки"
            self.pause_text = "ПАУЗА"
            self.resume_text = "Продолжить"
            self.menu_text = "Главное меню"
        else:
            self.game_title.config(text="Remember Sequence")
            self.level_text = "Level"
            self.points_text = "Score"
            self.pause_text = "PAUSE"
            self.resume_text = "Resume"
            self.menu_text = "Main Menu"

    def get_difficulty_text(self):
        return {
            "easy": {"ru": "Легкий", "en": "Easy"},
            "medium": {"ru": "Средний", "en": "Medium"},
            "hard": {"ru": "Сложный", "en": "Hard"}
        }[self.current_difficulty]["ru" if self.controller.language == "Русский" else "en"]

    def start_game(self, difficulty):
        self.controller.in_game = True
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.hide_overlay()

        self.current_difficulty = difficulty
        self.difficulty_multiplier = {"easy": 1, "medium": 2, "hard": 3}[difficulty]

        sizes = {"easy": (2, 2), "medium": (2, 3), "hard": (3, 3)}
        rows, cols = sizes[difficulty]

        for w in self.game_frame.winfo_children():
            w.destroy()

        self.buttons = []
        index = 0

        for r in range(rows):
            for c in range(cols):
                btn = Button(self.game_frame, text=str(index + 1),
                             width=6, height=3, font=("Arial", 24, "bold"),
                             command=lambda i=index: self.press(i))
                btn.grid(row=r, column=c, padx=10, pady=10)
                self.buttons.append(btn)
                index += 1

        self.sequence = []
        self.user_sequence = []
        self.correct_sequences = 0
        self.current_level = 1

        self.update_stats()
        self.lock = True
        self.after(500, self.add)

    def add(self):
        self.sequence.append(random.randint(0, len(self.buttons) - 1))
        self.user_sequence = []
        self.play()

    def play(self):
        self.lock = True
        for i, idx in enumerate(self.sequence):
            self.after(600 * (i + 1), lambda b=idx: self.flash(b))
        self.after(600 * (len(self.sequence) + 1),
                   lambda: setattr(self, "lock", False))

    def flash(self, idx):
        b = self.buttons[idx]
        b.config(bg="yellow")
        self.after(300, lambda: b.config(bg="white"))

    def press(self, idx):
        if self.lock or not self.sequence:
            return

        btn = self.buttons[idx]
        btn.config(bg="#7CFC00")
        self.after(200, lambda: btn.config(bg="white"))

        self.user_sequence.append(idx)
        pos = len(self.user_sequence) - 1

        if pos >= len(self.sequence) or self.user_sequence[-1] != self.sequence[pos]:
            btn.config(bg="#ff9999")
            self.after(200, lambda: btn.config(bg="white"))
            self.end_game()
            return

        if len(self.user_sequence) == len(self.sequence):
            self.correct_sequences += 1
            self.current_level += 1
            self.update_stats()
            self.after(600, self.add)

    def calculate_score(self):
        return max(0, self.correct_sequences * 100 * self.difficulty_multiplier)

    def get_current_score(self):
        return max(0, self.correct_sequences * 100 * self.difficulty_multiplier)

    def end_game(self):
        self.final_score = self.calculate_score()

        update("sequence", self.current_difficulty, False,
               self.final_score, self.current_level, 0,
               self.controller.language)

        if getattr(self, "training_mode", False) and self.training_callback:
            cb = self.training_callback
            self.training_callback = None
            self.after(300, lambda: cb(self.final_score, self.current_level))
            return

        self.show_overlay()

    def update_stats(self):
        self.level_label.config(text=f"{self.level_text}: {self.current_level}")
        self.points_label.config(text=f"{self.points_text}: {self.get_current_score()}")

    def show_overlay(self, resume=False):
        for w in self.overlay.winfo_children():
            w.destroy()

        self.overlay.place(relwidth=1, relheight=1)
        self.overlay.lift()

        box = Frame(self.overlay, bg="#0000FF", width=700, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        Label(box, text=self.game_title.cget("text"),
              font=("Arial", 34, "bold"),
              bg="#0000FF", fg="white").pack(pady=(20, 5))

        Label(box, text=self.get_difficulty_text(),
              font=("Arial", 24, "bold"),
              bg="#0000FF", fg="white").pack(pady=(0, 20))

        if not resume:
            Label(box, text=f"{self.points_text}: {self.final_score}",
                  font=("Arial", 20, "bold"),
                  bg="#0000FF", fg="white").pack(pady=10)

            Label(box, text=f"{self.level_text}: {self.current_level}",
                  font=("Arial", 20, "bold"),
                  bg="#0000FF", fg="white").pack(pady=10)

        if resume:
            Button(box, text=self.resume_text,
                   font=("Arial", 18, "bold"),
                   bg="white", width=18,
                   command=self.hide_overlay).pack(pady=15)

        Button(box, text=self.menu_text,
               font=("Arial", 18, "bold"),
               bg="white", width=18,
               command=self.go_to_main_menu).pack(pady=15)

    def pause(self):
        self.show_overlay(True)

    def hide_overlay(self):
        self.overlay.place_forget()

    def go_to_main_menu(self):
        self.hide_overlay()
        self.controller.in_game = False
        self.controller.play_music_loop()
        self.controller.show_frame("MainMenu")