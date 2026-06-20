import tkinter as tk
from tkinter import Frame, Label, Button
import random
from functools import partial
from stats_manager import update
import winsound
import os


class AudioMemoryGame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller
        self.current_difficulty = "easy"

        self.sequence = []
        self.user_sequence = []
        self.lock = True

        self.main_container = Frame(self, bg="#0000FF")
        self.main_container.pack(expand=True, fill="both")

        self.overlay = Frame(self.main_container, bg="#0000FF")

        # ===== TOP =====
        top_frame = Frame(self.main_container, bg="#0000FF")
        top_frame.pack(fill="x", pady=(30, 10), padx=40)

        self.pause_btn = Button(
            top_frame, text="⏸",
            font=("Arial", 18, "bold"),
            bg="white", width=3,
            command=self.show_pause
        )
        self.pause_btn.pack(side="left")

        self.title = Label(
            top_frame, bg="#0000FF", fg="white",
            font=("Arial", 36, "bold")
        )
        self.title.pack(side="left", expand=True)

        # ===== STATS =====
        stats_frame = Frame(self.main_container, bg="#0000FF")
        stats_frame.pack(pady=(10, 30))

        self.level_label = Label(stats_frame, bg="white", font=("Arial", 16, "bold"), width=12)
        self.level_label.pack(side="left", padx=20)

        self.points_label = Label(stats_frame, bg="white", font=("Arial", 16, "bold"), width=12)
        self.points_label.pack(side="left", padx=20)

        # ===== GAME =====
        self.center_frame = Frame(self.main_container, bg="#0000FF")
        self.center_frame.pack(expand=True, fill="both")

        self.game_frame = Frame(self.center_frame, bg="#0000FF")
        self.game_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.update_language()

        self.training_mode = False
        self.training_callback = None

    # ===== LANGUAGE =====
    def update_language(self):
        if getattr(self.controller, "language", "EN") == "Русский":
            self.title.config(text="Аудио память")
            self.level_text = "Уровень"
            self.score_text = "Очки"
            self.pause_text = "ПАУЗА"
            self.resume_text = "Продолжить"
            self.menu_text = "Главное меню"
            self.lose_text = "Вы ошиблись!"
            self.lang_code = "ru"
        else:
            self.title.config(text="Audio Memory")
            self.level_text = "Level"
            self.score_text = "Score"
            self.pause_text = "PAUSE"
            self.resume_text = "Resume"
            self.menu_text = "Main Menu"
            self.lose_text = "Wrong!"
            self.lang_code = "en"

    # ===== DIFFICULTY =====
    def get_difficulty_text(self):
        return {
            "ru": {"easy": "Легкий", "medium": "Средний", "hard": "Сложный"},
            "en": {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
        }[self.lang_code][self.current_difficulty]

    # ===== SOUND =====
    def play_sound(self, idx):
        path = os.path.join("sounds", self.lang_code, f"{idx + 1}.wav")
        if os.path.isfile(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    # ===== START =====
    def start_game(self, difficulty):
        self.controller.in_game = True
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.hide_overlay()

        self.current_difficulty = difficulty
        self.difficulty_multiplier = {"easy": 1, "medium": 2, "hard": 3}[difficulty]

        rows, cols = {"easy": (2, 2), "medium": (3, 2), "hard": (3, 3)}[difficulty]

        self.current_level = 1
        self.correct_sequences = 0

        self.sequence = []
        self.user_sequence = []
        self.lock = True

        self.update_level()
        self.update_points()

        for w in self.game_frame.winfo_children():
            w.destroy()

        self.buttons = []
        for i in range(rows * cols):
            btn = Button(
                self.game_frame,
                text=str(i + 1),
                width=6, height=3,
                font=("Arial", 24, "bold"),
                command=partial(self.button_pressed, i)
            )
            btn.grid(row=i // cols, column=i % cols, padx=10, pady=10)
            self.buttons.append(btn)

        self.after(500, self.add_to_sequence)

    # ===== GAME =====
    def add_to_sequence(self):
        self.sequence.append(random.randint(0, len(self.buttons) - 1))
        self.user_sequence = []
        self.play_sequence()

    def play_sequence(self):
        self.lock = True
        for i, idx in enumerate(self.sequence):
            self.after(800 * (i + 1), lambda x=idx: self.play_sound(x))
        self.after(800 * (len(self.sequence) + 1), self.unlock)

    def unlock(self):
        self.lock = False

    def button_pressed(self, idx):
        if self.lock or not self.sequence:
            return

        self.user_sequence.append(idx)

        btn = self.buttons[idx]
        btn.config(bg="#7CFC00")
        self.after(200, lambda: btn.config(bg="white"))

        pos = len(self.user_sequence) - 1

        if self.user_sequence[-1] != self.sequence[pos]:
            btn.config(bg="#ff9999")
            self.after(200, lambda: btn.config(bg="white"))
            return self.end_game()

        if len(self.user_sequence) == len(self.sequence):
            self.correct_sequences += 1
            self.current_level += 1

            self.update_level()
            self.update_points()

            self.after(600, self.add_to_sequence)

    # ===== SCORE =====
    def calculate_score(self):
        return max(0, self.correct_sequences * 100 * self.difficulty_multiplier)

    def get_current_score(self):
        return self.correct_sequences * 100 * self.difficulty_multiplier

    def end_game(self):
        self.final_score = self.calculate_score()

        update(
            "audio",
            self.current_difficulty,
            False,
            self.final_score,
            self.current_level,
            0,
            self.controller.language
        )

        if getattr(self, "training_mode", False) and self.training_callback:
            cb = self.training_callback
            self.training_callback = None
            self.after(300, lambda: cb(self.final_score, self.current_level))
            return

        self.show_fail_screen()

    # ===== UI =====
    def update_level(self):
        self.level_label.config(text=f"{self.level_text}: {self.current_level}")

    def update_points(self):
        self.points_label.config(text=f"{self.score_text}: {self.get_current_score()}")

    # ===== PAUSE =====
    def show_pause(self):
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()

        for w in self.overlay.winfo_children():
            w.destroy()

        box = Frame(self.overlay, bg="#0000FF", width=700, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        Label(box, text=self.pause_text,
              font=("Arial", 42, "bold"),
              bg="#0000FF", fg="white").pack(pady=40)

        Button(box, text=self.resume_text,
               font=("Arial", 18, "bold"),
               bg="white", width=18,
               command=self.hide_overlay).pack(pady=15)

        Button(box, text=self.menu_text,
               font=("Arial", 18, "bold"),
               bg="white", width=18,
               command=self.go_to_main_menu).pack(pady=15)

    # ===== FAIL =====
    def show_fail_screen(self):
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()

        for w in self.overlay.winfo_children():
            w.destroy()

        box = Frame(self.overlay, bg="#0000FF", width=700, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        Label(box, text=self.title.cget("text"),
              font=("Arial", 36, "bold"),
              bg="#0000FF", fg="white").pack(pady=(20, 5))

        Label(box, text=self.get_difficulty_text(),
              font=("Arial", 24, "bold"),
              bg="#0000FF", fg="white").pack(pady=(0, 20))

        Label(box, text=f"{self.score_text}: {self.final_score}",
              font=("Arial", 20, "bold"),
              bg="#0000FF", fg="white").pack(pady=10)

        Label(box, text=f"{self.level_text}: {self.current_level}",
              font=("Arial", 20, "bold"),
              bg="#0000FF", fg="white").pack(pady=10)

        Button(box, text=self.menu_text,
               font=("Arial", 18, "bold"),
               bg="white", width=18,
               command=self.go_to_main_menu).pack(pady=20)

    def hide_overlay(self):
        self.overlay.place_forget()

    def go_to_main_menu(self):
        self.hide_overlay()
        self.controller.in_game = False
        self.controller.play_music_loop()
        self.controller.show_frame("MainMenu")