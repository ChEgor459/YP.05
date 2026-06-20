import tkinter as tk
from tkinter import Frame, Label, Button
import json
import os


class StatsMenu(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        # ===== BACK =====
        Button(
            self, text="←", font=("Arial", 24, "bold"),
            bg="white", fg="black", width=3,
            relief="solid", bd=1, cursor="hand2",
            command=lambda: controller.show_frame("MainMenu")
        ).place(x=20, y=20)

        # ===== CENTER =====
        self.center = Frame(self, bg="#0000FF")
        self.center.place(relx=0.5, rely=0.5, anchor="center")

        self.title = Label(self.center, font=("Arial", 36, "bold"),
                           bg="#0000FF", fg="white")
        self.title.pack(pady=(0, 30))

        self.total_games_label = Label(self.center, font=("Arial", 18, "bold"),
                                       bg="#0000FF", fg="white")
        self.total_games_label.pack()

        self.training_label = Label(self.center, font=("Arial", 18, "bold"),
                                    bg="#0000FF", fg="white")
        self.training_label.pack()

        self.best_training_label = Label(self.center, font=("Arial", 18, "bold"),
                                         bg="#0000FF", fg="white")
        self.best_training_label.pack(pady=(10, 0))

        Frame(self.center, bg="white", height=2).pack(fill="x", padx=250, pady=25)

        self.best_title = Label(self.center, font=("Arial", 28, "bold"),
                                bg="#0000FF", fg="white")
        self.best_title.pack(pady=(0, 25))

        self.games_container = Frame(self.center, bg="#0000FF")
        self.games_container.pack()

        # ===== CONFIG =====
        self.games = {
            "pairs": ("pairs_total", True),
            "sequence": ("sequence_total", False),
            "audio": ("audio_total", False),
            "changes": ("changes_total", False)
        }

        self.names = {
            "ru": {
                "pairs": "Найди пару",
                "sequence": "Последовательность",
                "audio": "Аудио память",
                "changes": "Что изменилось"
            },
            "en": {
                "pairs": "Find the Pair",
                "sequence": "Sequence",
                "audio": "Audio",
                "changes": "Changes"
            }
        }

        self.update_language()

    # ===== LOAD =====
    def load_stats(self):
        if not os.path.exists("stats.json"):
            return {}
        return json.load(open("stats.json", encoding="utf-8"))

    # ===== TEXT =====
    def diff_text(self, d, ru):
        return {
            "easy": "Легкий" if ru else "Easy",
            "medium": "Средний" if ru else "Medium",
            "hard": "Сложный" if ru else "Hard"
        }[d]

    # ===== UPDATE =====
    def update_language(self):
        ru = self.controller.language == "Русский"
        lang = "ru" if ru else "en"

        self.title.config(text="Статистика" if ru else "Statistics")
        self.best_title.config(text="Лучшие результаты" if ru else "Best Scores")

        stats = self.load_stats()

        self.total_games_label.config(
            text=f"{'Всего игр сыграно' if ru else 'Total Games Played'}: {stats.get('total_games', 0)}"
        )
        self.training_label.config(
            text=f"{'Всего тренировок' if ru else 'Total Training Sessions'}: {stats.get('training_runs', 0)}"
        )

        best_training_score = stats.get('best_training_score', 0)
        self.best_training_label.config(
            text=f"{'Лучший результат в тренировке' if ru else 'Best Training Score'}: {best_training_score}"
        )

        for w in self.games_container.winfo_children():
            w.destroy()

        self.games_container.grid_columnconfigure((0, 1), weight=1)

        # ===== ГЕНЕРАЦИЯ КАРТОЧЕК =====
        for i, (key, (total_key, is_pairs)) in enumerate(self.games.items()):
            row, col = divmod(i, 2)

            played = stats.get(total_key, 0)
            name = self.names[lang][key]

            card = Frame(self.games_container, bg="white", bd=2,
                         relief="solid", width=450, height=280)
            card.grid(row=row, column=col, padx=25, pady=15)
            card.grid_propagate(False)

            Label(card, text=f"{name} ({played})",
                  font=("Arial", 18, "bold"),
                  bg="white", fg="#0000FF").pack(pady=(15, 12))

            for diff in ("easy", "medium", "hard"):
                data = stats.get(key, {}).get(diff, {})

                if not data:
                    value = "Нет результатов" if ru else "No score yet"
                else:
                    if is_pairs:
                        score = data.get("best_score", 0)
                        moves = data.get("best_moves", 0)
                        value = (
                            f"{'Очки' if ru else 'Score'}: {score} | "
                            f"{'Ходы' if ru else 'Moves'}: {moves}"
                        ) if (score or moves) else ("Нет результатов" if ru else "No score yet")
                    else:
                        lvl = data.get("best_level", 0)
                        score = data.get("best_score", 0)
                        value = (
                            f"{'Уровень' if ru else 'Level'}: {lvl} | "
                            f"{'Очки' if ru else 'Score'}: {score}"
                        ) if (lvl or score) else ("Нет результатов" if ru else "No score yet")

                row_frame = Frame(card, bg="white")
                row_frame.pack(fill="x", padx=25, pady=6)

                Label(row_frame, text=self.diff_text(diff, ru),
                      font=("Arial", 13, "bold"),
                      bg="white", width=10, anchor="w").pack(side="left")

                Label(row_frame, text=value,
                      font=("Arial", 12),
                      bg="white", fg="gray",
                      anchor="w").pack(side="left", padx=10)