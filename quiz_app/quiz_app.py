"""Simple multiple-choice quiz application using Tkinter."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


class QuizApp:
    BG = "#f5f7fb"
    CARD = "#ffffff"
    ACCENT = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    TEXT = "#1e293b"
    MUTED = "#64748b"
    SUCCESS = "#16a34a"
    ERROR = "#dc2626"
    DIFFICULTIES = ("easy", "medium", "hard", "spanish")
    GRADIENTS = {
        "easy": ("#ecfdf5", "#6ee7b7"),
        "medium": ("#fffbeb", "#fcd34d"),
        "hard": ("#fef2f2", "#fca5a5"),
        "spanish": ("#fff7ed", "#fdba74"),
    }
    ACCENTS = {
        "easy": ("#16a34a", "#15803d"),
        "medium": ("#d97706", "#b45309"),
        "hard": ("#dc2626", "#b91c1c"),
        "spanish": ("#ea580c", "#c2410c"),
    }
    SELECT_COLORS = {
        "easy": "#bbf7d0",
        "medium": "#fde68a",
        "hard": "#fecaca",
        "spanish": "#fed7aa",
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Python Quiz")
        self.root.geometry("640x520")
        self.root.minsize(560, 480)
        self.root.configure(bg=self.BG)

        self.all_questions = self._load_questions()
        self.questions: list[dict] = []
        self.current_index = 0
        self.score = 0
        self.selected_var = tk.IntVar(value=-1)
        self.difficulty_var = tk.StringVar(value="easy")
        self.difficulty_var.trace_add("write", self._on_difficulty_change)

        self._build_ui()
        self.show_welcome()

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[index : index + 2], 16) for index in (0, 2, 4))

    def _draw_gradient(self, width: int, height: int) -> None:
        top, bottom = self.GRADIENTS[self.difficulty_var.get()]
        r1, g1, b1 = self._hex_to_rgb(top)
        r2, g2, b2 = self._hex_to_rgb(bottom)

        self.bg_canvas.delete("gradient")
        for row in range(max(height, 1)):
            ratio = row / max(height - 1, 1)
            red = int(r1 + (r2 - r1) * ratio)
            green = int(g1 + (g2 - g1) * ratio)
            blue = int(b1 + (b2 - b1) * ratio)
            color = f"#{red:02x}{green:02x}{blue:02x}"
            self.bg_canvas.create_rectangle(
                0,
                row,
                width,
                row + 1,
                fill=color,
                outline=color,
                tags="gradient",
            )

        self.bg_canvas.tag_lower("gradient")
        self.bg_canvas.tag_raise(self.card_window)

    def _apply_difficulty_theme(self) -> None:
        difficulty = self.difficulty_var.get()
        accent, accent_hover = self.ACCENTS[difficulty]
        self.action_button.config(bg=accent, activebackground=accent_hover)

        width = self.bg_canvas.winfo_width()
        height = self.bg_canvas.winfo_height()
        if width > 1 and height > 1:
            self._draw_gradient(width, height)

    def _on_difficulty_change(self, *_args: str) -> None:
        self._apply_difficulty_theme()

    def _load_questions(self) -> dict[str, list[dict]]:
        path = Path(__file__).with_name("questions.json")
        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def _build_ui(self) -> None:
        margin = 24
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.bg_canvas.pack(fill="both", expand=True)

        self.card = tk.Frame(
            self.bg_canvas,
            bg=self.CARD,
            highlightbackground="#e2e8f0",
            highlightthickness=1,
        )
        self.card_window = self.bg_canvas.create_window(
            margin,
            margin,
            window=self.card,
            anchor="nw",
        )

        def on_canvas_resize(event: tk.Event) -> None:
            card_width = max(event.width - 2 * margin, 400)
            card_height = max(event.height - 2 * margin, 400)
            self.bg_canvas.itemconfigure(
                self.card_window,
                width=card_width,
                height=card_height,
            )
            self._draw_gradient(event.width, event.height)

        self.bg_canvas.bind("<Configure>", on_canvas_resize)

        self.title_label = tk.Label(
            self.card,
            text="Python Quiz",
            font=("Segoe UI", 22, "bold"),
            bg=self.CARD,
            fg=self.TEXT,
        )
        self.title_label.pack(pady=(28, 8))

        self.subtitle_label = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 11),
            bg=self.CARD,
            fg=self.MUTED,
            wraplength=520,
            justify="center",
        )
        self.subtitle_label.pack(pady=(0, 12))

        self.progress_label = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 10),
            bg=self.CARD,
            fg=self.MUTED,
        )
        self.progress_label.pack(pady=(0, 8))

        self.progress_bar = ttk.Progressbar(
            self.card,
            mode="determinate",
            maximum=3,
        )
        self.progress_bar.pack(fill="x", padx=40, pady=(0, 16))

        self.question_label = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 14),
            bg=self.CARD,
            fg=self.TEXT,
            wraplength=520,
            justify="left",
        )
        self.question_label.pack(pady=(8, 16), padx=40, anchor="w")

        self.options_frame = tk.Frame(self.card, bg=self.CARD)
        self.options_frame.pack(fill="x", padx=40)

        self.feedback_label = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=self.CARD,
            fg=self.MUTED,
        )
        self.feedback_label.pack(pady=(16, 0))

        self.action_button = tk.Button(
            self.card,
            text="Start Quiz",
            font=("Segoe UI", 11, "bold"),
            bg=self.ACCENT,
            fg="white",
            activebackground=self.ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._on_action,
        )
        self.action_button.pack(pady=28)

    def _clear_options(self) -> None:
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def _show_difficulty_selector(self) -> None:
        labels = {
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard",
            "spanish": "Spanish",
        }
        for difficulty in self.DIFFICULTIES:
            tk.Radiobutton(
                self.options_frame,
                text=labels[difficulty],
                variable=self.difficulty_var,
                value=difficulty,
                font=("Segoe UI", 11),
                bg=self.CARD,
                fg=self.TEXT,
                activebackground=self.CARD,
                selectcolor=self.SELECT_COLORS[difficulty],
                anchor="w",
                padx=8,
                pady=6,
            ).pack(fill="x", pady=4)

    def show_welcome(self) -> None:
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.selected_var.set(-1)
        self.difficulty_var.set("easy")
        self.progress_bar["value"] = 0
        self.progress_label.config(text="")
        self.question_label.config(text="")
        self.feedback_label.config(text="")
        self._clear_options()

        self.title_label.config(text="Welcome!")
        self.subtitle_label.config(
            text="Choose a difficulty, then answer the multiple-choice questions."
        )
        self._show_difficulty_selector()
        self.action_button.config(text="Start Quiz")
        self._apply_difficulty_theme()

    def show_question(self) -> None:
        question = self.questions[self.current_index]
        total = len(self.questions)
        number = self.current_index + 1

        difficulty = self.difficulty_var.get().capitalize()
        self.title_label.config(text=f"Question — {difficulty}")
        self.subtitle_label.config(text="Select one answer, then click Next.")
        self.progress_label.config(text=f"Question {number} of {total}")
        self.progress_bar["value"] = self.current_index
        self.question_label.config(text=question["question"])
        self.feedback_label.config(text="")
        self.selected_var.set(-1)
        self._clear_options()

        select_color = self.SELECT_COLORS[self.difficulty_var.get()]
        for index, option in enumerate(question["options"]):
            tk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_var,
                value=index,
                font=("Segoe UI", 11),
                bg=self.CARD,
                fg=self.TEXT,
                activebackground=self.CARD,
                selectcolor=select_color,
                anchor="w",
                padx=8,
                pady=6,
            ).pack(fill="x", pady=4)

        is_last = self.current_index == total - 1
        self.action_button.config(text="Finish Quiz" if is_last else "Next")

    def show_results(self) -> None:
        total = len(self.questions)
        percent = round((self.score / total) * 100)

        if percent == 100:
            message = "Perfect score! Excellent work."
        elif percent >= 70:
            message = "Great job! You passed the quiz."
        else:
            message = "Keep practicing — you can do better next time."

        difficulty = self.difficulty_var.get().capitalize()
        self.title_label.config(text="Quiz Complete")
        self.subtitle_label.config(text=message)
        self.progress_label.config(
            text=f"{difficulty} — Final score: {self.score} / {total} ({percent}%)"
        )
        self.progress_bar["value"] = total
        self.question_label.config(text="")
        self.feedback_label.config(text="")
        self._clear_options()
        self.action_button.config(text="Play Again")

    def _on_action(self) -> None:
        if self.action_button["text"] == "Start Quiz":
            difficulty = self.difficulty_var.get()
            self.questions = self.all_questions[difficulty]
            self.progress_bar["maximum"] = len(self.questions)
            self.show_question()
            return

        if self.action_button["text"] == "Play Again":
            self.show_welcome()
            return

        selected = self.selected_var.get()
        if selected == -1:
            messagebox.showwarning("No answer selected", "Please choose an option before continuing.")
            return

        correct_index = self.questions[self.current_index]["answer"]
        if selected == correct_index:
            self.score += 1
            self.feedback_label.config(text="Correct!", fg=self.SUCCESS)
        else:
            correct_text = self.questions[self.current_index]["options"][correct_index]
            self.feedback_label.config(
                text=f"Incorrect. The right answer was: {correct_text}",
                fg=self.ERROR,
            )

        self.root.after(900, self._advance)

    def _advance(self) -> None:
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.show_question()
        else:
            self.show_results()


def main() -> None:
    root = tk.Tk()
    QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
