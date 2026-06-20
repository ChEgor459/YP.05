import tkinter as tk
from tkinter import Frame, Label, Button

class DifficultyMenu(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller
        self.current_game = None

        frame = Frame(self, bg="#0000FF")
        frame.place(relwidth=1, relheight=1)

        # Кнопка назад
        self.back_btn = Button(frame, text="←", font=("Arial", 24, "bold"),
                               bg="white", fg="black", relief="solid", bd=1,
                               cursor="hand2", command=lambda: controller.show_frame("GamesMenu"))
        self.back_btn.place(x=20, y=20, width=60, height=60)

        # Заголовок
        self.title = Label(frame, bg="#0000FF", fg="white", font=("Arial", 50, "bold"))
        self.title.pack(pady=(80, 40))

        # Кнопки сложности
        button_style = {"font": ("Arial", 24, "bold"), "width": 20, "height": 2,
                        "bg": "white", "cursor": "hand2"}

        self.btn_easy = Button(frame, command=lambda: self.start_game("easy"), **button_style)
        self.btn_easy.pack(pady=15)

        self.btn_medium = Button(frame, command=lambda: self.start_game("medium"), **button_style)
        self.btn_medium.pack(pady=15)

        self.btn_hard = Button(frame, command=lambda: self.start_game("hard"), **button_style)
        self.btn_hard.pack(pady=15)

        self.update_language()

    def set_game(self, game_name):
        self.current_game = game_name
        self.update_language()

    def start_game(self, difficulty):
        if self.current_game == "pairs":
            game = self.controller.frames["MemoryPairsGame"]
            game.start_game(difficulty)
            self.controller.show_frame("MemoryPairsGame")
        elif self.current_game == "audio":
            game = self.controller.frames["AudioMemoryGame"]
            game.start_game(difficulty)
            self.controller.show_frame("AudioMemoryGame")
        elif self.current_game == "sequence":
            game = self.controller.frames["SequenceMemoryGame"]
            game.start_game(difficulty)
            self.controller.show_frame("SequenceMemoryGame")
        elif self.current_game == 'visual':
            game = self.controller.frames['VisualMemoryGame']
            game.start_game(difficulty)
            self.controller.show_frame('VisualMemoryGame')

    def update_language(self):
        if self.controller.language == "Русский":
            self.title.config(text="Выберите сложность")
            self.btn_easy.config(text="Легкий")
            self.btn_medium.config(text="Средний")
            self.btn_hard.config(text="Сложный")
        else:
            self.title.config(text="Select Difficulty")
            self.btn_easy.config(text="Easy")
            self.btn_medium.config(text="Medium")
            self.btn_hard.config(text="Hard")