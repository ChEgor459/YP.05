import tkinter as tk
from tkinter import Frame, Label, Button

class MainMenu(Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        self.frame = Frame(self, bg="#0000FF")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.brain_label = Label(self.frame, text="🧠", bg="#0000FF", font=("Arial", 80))
        self.brain_label.pack(pady=(0, 20))

        self.title_label = Label(self.frame, bg="#0000FF", fg="white", font=("Arial", 67, "bold"))
        self.title_label.pack()

        self.subtitle_label = Label(self.frame, bg="#0000FF", fg="#AAAAFF", font=("Arial", 24))
        self.subtitle_label.pack(pady=(0, 50))

        button_style = {
            "font": ("Arial", 24, "bold"),
            "width": 15,
            "height": 1,
            "bg": "white",
            "fg": "black",
            "bd": 1,
            "relief": "solid",
            "cursor": "hand2"
        }

        exit_style = button_style.copy()
        exit_style.update({"bg": "#ff6b6b", "fg": "white"})

        self.btn_train = Button(
            self.frame,
            command=lambda: self.controller.training.start(),
            **button_style
        )
        self.btn_train.pack(pady=10)

        self.btn_games = Button(self.frame, command=lambda: controller.show_frame("GamesMenu"), **button_style)
        self.btn_games.pack(pady=10)

        self.btn_stats = Button(
            self.frame,
            command=lambda: controller.show_frame("StatsMenu"),
            **button_style
        )
        self.btn_stats.pack(pady=10)

        self.btn_settings = Button(self.frame, command=lambda: controller.show_frame("SettingsMenu"), **button_style)
        self.btn_settings.pack(pady=10)

        self.btn_exit = Button(self.frame, command=self.controller.root.destroy, **exit_style)
        self.btn_exit.pack(pady=10)

        self.update_language()

    def update_language(self):
        if self.controller.language == "Русский":
            self.title_label.config(text="Memory training")
            self.subtitle_label.config(text="Тренируй память каждый день")
            self.btn_train.config(text="📝 Тренировка")
            self.btn_games.config(text="🎮 Мини-игры")
            self.btn_stats.config(text="📊 Статистика")
            self.btn_settings.config(text="⚙️ Настройки")
            self.btn_exit.config(text="❌ Выход")
        else:
            self.title_label.config(text="Memory training")
            self.subtitle_label.config(text="Train your memory every day")
            self.btn_train.config(text="📝 Training")
            self.btn_games.config(text="🎮 Mini-games")
            self.btn_stats.config(text="📊 Statistics")
            self.btn_settings.config(text="⚙️ Settings")
            self.btn_exit.config(text="❌ Exit")