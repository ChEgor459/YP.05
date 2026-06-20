import tkinter as tk
from tkinter import Frame, Label, Button, IntVar
from stats_manager import save_settings


class SettingsMenu(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0000FF")
        self.controller = controller

        # ===== STATE =====
        self.lang_var = IntVar(value=0 if controller.language == "Русский" else 1)

        # ===== BACK =====
        Button(
            self, text="←", font=("Arial", 24, "bold"),
            bg="white", fg="black", width=3,
            relief="solid", bd=1, cursor="hand2",
            command=lambda: controller.show_frame("MainMenu")
        ).place(x=20, y=20)

        # ===== TITLE =====
        self.title = Label(self, bg="#0000FF", fg="white",
                           font=("Arial", 40, "bold"))
        self.title.pack(pady=(100, 40))

        # ===== LANGUAGE =====
        lang_frame = Frame(self, bg="#0000FF")
        lang_frame.pack(pady=20)

        self.lang_label = Label(lang_frame, bg="#0000FF",
                                fg="white", font=("Arial", 24, "bold"))
        self.lang_label.pack(side="left", padx=(0, 20))

        self.rb_ru = tk.Radiobutton(
            lang_frame, text="Русский",
            variable=self.lang_var, value=0,
            font=("Arial", 22, "bold"),
            bg="#0000FF", fg="white",
            selectcolor="#66CCFF",
            activebackground="#0000FF",
            command=self.change_language
        )
        self.rb_en = tk.Radiobutton(
            lang_frame, text="English",
            variable=self.lang_var, value=1,
            font=("Arial", 22, "bold"),
            bg="#0000FF", fg="white",
            selectcolor="#66CCFF",
            activebackground="#0000FF",
            command=self.change_language
        )

        self.rb_ru.pack(side="left", padx=15)
        self.rb_en.pack(side="left", padx=15)

        # ===== SOUND =====
        self.btn_sound = Button(
            self, font=("Arial", 22, "bold"),
            width=20, height=2,
            bg="white", fg="black",
            command=self.toggle_sound
        )
        self.btn_sound.pack(pady=40)

        self.update_language()

    # ===== LANGUAGE UPDATE =====
    def update_language(self):
        lang = "Русский" if self.lang_var.get() == 0 else "English"
        self.controller.language = lang

        is_ru = lang == "Русский"

        self.title.config(text="Настройки" if is_ru else "Settings")
        self.lang_label.config(text="Язык:" if is_ru else "Language:")

        self.btn_sound.config(
            text=("🔊 Звук: Вкл" if self.controller.sound_on else "🔇 Звук: Выкл")
            if is_ru else
            ("🔊 Sound: On" if self.controller.sound_on else "🔇 Sound: Off")
        )

    # ===== CHANGE LANGUAGE =====
    def change_language(self):
        self.update_language()

        save_settings(self.controller.language, self.controller.sound_on)

        for frame in self.controller.frames.values():
            if hasattr(frame, "update_language"):
                frame.update_language()

    # ===== SOUND =====
    def toggle_sound(self):
        self.controller.sound_on = not self.controller.sound_on

        import winsound
        if self.controller.sound_on:
            self.controller.play_music_loop()
        else:
            winsound.PlaySound(None, winsound.SND_PURGE)

        save_settings(self.controller.language, self.controller.sound_on)
        self.update_language()