import tkinter as tk
from tkinter import Frame, Label, Button
from stats_manager import update
import random
import winsound


class VisualMemoryGame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        self.main_container = Frame(self, bg="#0000FF")
        self.main_container.pack(expand=True, fill="both")

        top = Frame(self.main_container, bg="#0000FF")
        top.pack(fill="x", pady=(30, 10), padx=40)

        Button(top, text="⏸", font=("Arial", 18, "bold"),
               bg="white", width=3, command=self.pause).pack(side="left")

        self.title = Label(top, bg="#0000FF", fg="white",
                           font=("Arial", 36, "bold"))
        self.title.pack(side="left", expand=True)

        stats = Frame(self.main_container, bg="#0000FF")
        stats.pack(pady=20)

        self.level_label = Label(stats, bg="white", font=("Arial", 16, "bold"), width=12)
        self.level_label.pack(side="left", padx=20)

        self.points_label = Label(stats, bg="white", font=("Arial", 16, "bold"), width=12)
        self.points_label.pack(side="left", padx=20)

        self.timer_label = Label(self.main_container, bg="white",
                                 font=("Arial", 16, "bold"))
        self.timer_label.pack(pady=10)

        self.game_frame = Frame(self.main_container, bg="#0000FF")
        self.game_frame.pack(expand=True)

        self.overlay = Frame(self, bg="#0000FF")

        self.update_language()
        self.training_mode = False
        self.training_callback = None

        self.current_difficulty = None
        self.difficulty_multiplier = None
        self.show_time = None
        self.current_level = None
        self.correct_rounds = None
        self.values = None
        self.to_change = None
        self.time_left = None
        self.lock = None
        self.user = None

    def update_language(self):
        if self.controller.language == "Русский":
            self.title.config(text="Что изменилось?")
            self.level_text = "Уровень"
            self.points_text = "Очки"
            self.time_text = "Время"
            self.pause_text = "ПАУЗА"
            self.resume_text = "Продолжить"
            self.menu_text = "Главное меню"
        else:
            self.title.config(text="What Changed?")
            self.level_text = "Level"
            self.points_text = "Score"
            self.time_text = "Time"
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
        self.hide_overlay()
        self.lock = True

        self.controller.in_game = True
        winsound.PlaySound(None, winsound.SND_PURGE)

        self.current_difficulty = difficulty
        self.difficulty_multiplier = {"easy": 1, "medium": 2, "hard": 3}[difficulty]

        self.times = {"easy": 5000, "medium": 4000, "hard": 3000}
        self.show_time = self.times[difficulty]

        for w in self.game_frame.winfo_children():
            w.destroy()

        self.buttons = []
        for i in range(6):
            btn = Button(self.game_frame,
                         width=8, height=4,
                         font=("Arial", 24, "bold"),
                         command=lambda idx=i: self.press(idx))
            btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)
            self.buttons.append(btn)

        self.current_level = 1
        self.correct_rounds = 0

        self.update_stats()
        self.new_round()

    def new_round(self):
        self.lock = True
        self.user = []

        self.values = list(range(1, 7))
        random.shuffle(self.values)

        for i, b in enumerate(self.buttons):
            b.config(text=str(self.values[i]), bg="white")

        self.to_change = random.sample(range(6), 2)

        self.time_left = self.show_time // 1000
        self.update_timer()

        self.after(self.show_time, self.change_cards)

    def update_timer(self):
        self.timer_label.config(text=f"{self.time_text}: {self.time_left}")
        if self.time_left > 0:
            self.time_left -= 1
            self.after(1000, self.update_timer)

    def change_cards(self):
        self.fade_step(0)

    def fade_step(self, step):
        colors = ["#FFFFFF", "#DDDDDD", "#AAAAAA", "#777777"]

        if step < len(colors):
            for b in self.buttons:
                b.config(bg=colors[step])
            self.after(100, lambda: self.fade_step(step + 1))
        else:
            self.swap_cards()

    def swap_cards(self):
        i1, i2 = self.to_change
        self.values[i1], self.values[i2] = self.values[i2], self.values[i1]

        for i, b in enumerate(self.buttons):
            b.config(text=str(self.values[i]), bg="white")

        self.lock = False

    def press(self, idx):
        if self.lock:
            return

        if idx in self.to_change:
            if idx not in self.user:
                self.user.append(idx)
                self.buttons[idx].config(bg="green")

            if len(self.user) == 2:
                self.correct_rounds += 1
                self.current_level += 1
                self.update_stats()
                self.after(800, self.new_round)
        else:
            self.end_game()

    def calculate_score(self):
        return max(0, self.correct_rounds * 100 * self.difficulty_multiplier)

    def get_current_score(self):
        return max(0, self.correct_rounds * 100 * self.difficulty_multiplier)

    def end_game(self):
        self.final_score = self.calculate_score()

        update("changes", self.current_difficulty, False,
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

        Label(box, text=self.title.cget("text"),
              font=("Arial", 36, "bold"),
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

    def go_to_main_menu(self):
        self.hide_overlay()
        self.controller.in_game = False
        self.controller.play_music_loop()
        self.controller.show_frame("MainMenu")

    def hide_overlay(self):
        self.overlay.place_forget()

    def pause(self):
        self.show_overlay(True)