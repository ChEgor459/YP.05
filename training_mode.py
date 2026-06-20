import random
import json
import tkinter as tk
from tkinter import Frame, Label, Button


class TrainingMode:
    def __init__(self, controller):
        self.controller = controller
        self.results = []

        self.games_pool = [
            "VisualMemoryGame",
            "AudioMemoryGame",
            "MemoryPairsGame",
            "SequenceMemoryGame"
        ]
        self.difficulties = ["easy", "medium", "hard"]

        self.selected_games = []
        self.current_index = 0
        self.total_score = 0

        # ===== НАЗВАНИЯ =====
        self.names = {
            "ru": {
                "VisualMemoryGame": "Что изменилось",
                "AudioMemoryGame": "Аудио память",
                "MemoryPairsGame": "Найди пару",
                "SequenceMemoryGame": "Запомни последовательность"
            },
            "en": {
                "VisualMemoryGame": "What Changed",
                "AudioMemoryGame": "Audio Memory",
                "MemoryPairsGame": "Find the Pair",
                "SequenceMemoryGame": "Remember Sequence"
            }
        }

        self.diff_names = {
            "ru": {"easy": "Лёгкая", "medium": "Средняя", "hard": "Сложная"},
            "en": {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
        }

        # ===== ЭКРАН ПЕРЕХОДА =====
        self.transition_frame = Frame(controller.container, bg="#0000FF")

        box = Frame(self.transition_frame, bg="#0000FF", width=700, height=450)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        self.transition_label = Label(
            box, font=("Arial", 24, "bold"),
            bg="#0000FF", fg="white",
            justify="center", wraplength=600
        )
        self.transition_label.pack(pady=40)

        Button(
            box, text="Начать", font=("Arial", 18, "bold"),
            bg="white", width=18,
            command=self.launch_game
        ).pack(pady=20)

        # ===== ЭКРАН РЕЗУЛЬТАТОВ =====
        self.result_frame = Frame(controller.container, bg="#0000FF")

        self.result_box = Frame(self.result_frame, bg="#0000FF", width=900, height=600)
        self.result_box.place(relx=0.5, rely=0.5, anchor="center")
        self.result_box.pack_propagate(False)

    # ===== СТАРТ =====
    def start(self):
        self.results.clear()
        self.selected_games = [
            (random.choice(self.games_pool), random.choice(self.difficulties))
            for _ in range(3)
        ]
        self.current_index = self.total_score = 0
        self.show_transition()

    # ===== ПЕРЕХОД =====
    def show_transition(self):
        if self.current_index >= 3:
            return self.show_final_results()

        lang = "ru" if self.controller.language == "Русский" else "en"

        game, diff = self.selected_games[self.current_index]

        text = (
            f"{self.names[lang][game]}\n\n"
            f"{'Сложность' if lang == 'ru' else 'Difficulty'}: {self.diff_names[lang][diff]}\n\n"
            f"{self.current_index + 1} / 3"
        )

        self.transition_label.config(text=text)
        self.transition_frame.place(relwidth=1, relheight=1)
        self.transition_frame.lift()

    # ===== ЗАПУСК =====
    def launch_game(self):
        self.transition_frame.place_forget()

        game_name, difficulty = self.selected_games[self.current_index]
        game = self.controller.frames[game_name]

        game.training_mode = True
        game.training_callback = self.on_game_finished

        self.controller.show_frame(game_name)
        game.start_game(difficulty)

    # ===== КОНЕЦ ИГРЫ =====
    def on_game_finished(self, score, level):
        game, diff = self.selected_games[self.current_index]

        self.results.append((game, diff, score, level))
        self.total_score += score
        self.current_index += 1

        self.controller.root.after(700, self.show_transition)

    # ===== ФИНАЛ =====
    def show_final_results(self):
        with open("stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)

        if self.results:
            stats["training_runs"] = stats.get("training_runs", 0) + 1

            current_best = stats.get("best_training_score", 0)
            if self.total_score > current_best:
                stats["best_training_score"] = self.total_score

        with open("stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)

        for w in self.result_box.winfo_children():
            w.destroy()

        lang = "ru" if self.controller.language == "Русский" else "en"

        Label(
            self.result_box,
            text="Результаты" if lang == "ru" else "Results",
            font=("Arial", 40, "bold"),
            bg="#0000FF", fg="white"
        ).pack(pady=20)

        for i, (game, _, score, level) in enumerate(self.results, 1):
            name = self.names[lang][game]

            if game == "MemoryPairsGame":
                text = f"{i}. {name} — {'Очки' if lang == 'ru' else 'Score'}: {score}, {'Ходы' if lang == 'ru' else 'Moves'}: {level}"
            else:
                text = f"{i}. {name} — {'Уровень' if lang == 'ru' else 'Level'}: {level}, {'Очки' if lang == 'ru' else 'Score'}: {score}"

            Label(
                self.result_box, text=text,
                font=("Arial", 22, "bold"),
                bg="#0000FF", fg="white",
                wraplength=800, justify="center"
            ).pack(pady=5)

        Label(
            self.result_box,
            text=f"\n{'Итог' if lang == 'ru' else 'Total'}: {self.total_score}",
            font=("Arial", 28, "bold"),
            bg="#0000FF", fg="white"
        ).pack(pady=30)

        if stats.get("best_training_score", 0) == self.total_score and self.total_score > 0:
            Label(
                self.result_box,
                text="🎉 НОВЫЙ РЕКОРД! 🎉" if lang == "ru" else "🎉 NEW RECORD! 🎉",
                font=("Arial", 20, "bold"),
                bg="#0000FF", fg="yellow"
            ).pack(pady=(0, 20))

        Button(
            self.result_box,
            text="В главное меню" if lang == "ru" else "Main Menu",
            font=("Arial", 18, "bold"),
            bg="white", width=18,
            command=self.go_to_menu
        ).pack(pady=20)

        self.result_frame.place(relwidth=1, relheight=1)
        self.result_frame.lift()

    # ===== В МЕНЮ =====
    def go_to_menu(self):
        self.result_frame.place_forget()
        self.controller.in_game = False
        self.controller.play_music_loop()
        self.controller.show_frame("MainMenu")