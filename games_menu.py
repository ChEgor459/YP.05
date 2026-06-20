import tkinter as tk
from tkinter import Frame, Label, Button


class GamesMenu(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        # Кнопка назад
        Button(
            self, text="←", font=("Arial", 24, "bold"),
            bg="white", fg="black", relief="solid", bd=1,
            cursor="hand2",
            command=lambda: controller.show_frame("MainMenu")
        ).place(x=20, y=20, width=60, height=60)

        self.title = Label(self, bg="#0000FF", fg="white", font=("Arial", 50, "bold"))
        self.title.pack(pady=(80, 40))

        # Игры: (ключ, кнопка)
        self.buttons = {
            "pairs": Button(self, font=("Arial", 20, "bold"), width=28, height=2,
                            command=lambda: self.open_difficulty("pairs")),
            "audio": Button(self, font=("Arial", 20, "bold"), width=28, height=2,
                            command=lambda: self.open_difficulty("audio")),
            "sequence": Button(self, font=("Arial", 20, "bold"), width=28, height=2,
                               command=lambda: self.open_difficulty("sequence")),
            "visual": Button(self, font=("Arial", 20, "bold"), width=28, height=2,
                             command=lambda: self.open_difficulty("visual")),
        }

        for btn in self.buttons.values():
            btn.pack(pady=10)

        self.update_language()

    def open_difficulty(self, game_name):
        menu = self.controller.frames["DifficultyMenu"]
        menu.set_game(game_name)
        self.controller.show_frame("DifficultyMenu")

    def update_language(self):
        ru = self.controller.language == "Русский"

        self.title.config(text="Мини-игры" if ru else "Mini Games")

        texts = {
            "pairs": ("Найди пару 🃏", "Find the Pair 🃏"),
            "audio": ("Аудио-память 🎵", "Audio Memory 🎵"),
            "sequence": ("Запомни последовательность 🔢", "Remember the Sequence 🔢"),
            "visual": ("Что изменилось? 🔎", "What Changed? 🔎"),
        }

        for key, btn in self.buttons.items():
            btn.config(text=texts[key][0 if ru else 1])