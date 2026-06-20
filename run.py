import tkinter as tk
import winsound
import threading

from menus.main_menu import MainMenu
from menus.games_menu import GamesMenu
from menus.settings_menu import SettingsMenu
from menus.difficulty_menu import DifficultyMenu
from games.memory_pairs_game import MemoryPairsGame
from games.audio_memory_game import AudioMemoryGame
from games.remember_sequence_game import SequenceMemoryGame
from games.visual_memory_games import VisualMemoryGame
from training_mode import TrainingMode
from menus.stats_menu import StatsMenu


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("MemoryTrainer")

        self.normal_width = 1024
        self.normal_height = 768

        self.root.geometry(f"{self.normal_width}x{self.normal_height}")

        self.center_window()

        self.root.attributes('-fullscreen', True)

        self.root.bind('<Escape>', self.toggle_fullscreen)

        self.root.configure(bg="#0000FF")

        from stats_manager import load_settings

        settings = load_settings()

        self.language = settings.get("language", "Русский")
        self.sound_on = settings.get("sound_on", True)

        self.container = tk.Frame(root, bg="#0000FF")
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        self.training = TrainingMode(self)

        for F in (MainMenu, GamesMenu, SettingsMenu, StatsMenu, DifficultyMenu, MemoryPairsGame, AudioMemoryGame,
                  SequenceMemoryGame, VisualMemoryGame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MainMenu")

        self.in_game = False

        self.play_music_loop()

    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.root.attributes('-fullscreen')

        if is_fullscreen:
            self.root.attributes('-fullscreen', False)
            self.root.geometry(f"{self.normal_width}x{self.normal_height}")
            self.center_window()
        else:
            self.normal_width = self.root.winfo_width()
            self.normal_height = self.root.winfo_height()
            self.root.attributes('-fullscreen', True)

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.normal_width) // 2
        y = (screen_height - self.normal_height) // 2
        self.root.geometry(f"{self.normal_width}x{self.normal_height}+{x}+{y}")

    def play_music_loop(self):
        if self.sound_on and not self.in_game:
            import winsound
            winsound.PlaySound(
                "sounds/music.wav",
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
            )

    def show_frame(self, name):
        frame = self.frames[name]

        if hasattr(frame, "update_language"):
            frame.update_language()

        frame.tkraise()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()