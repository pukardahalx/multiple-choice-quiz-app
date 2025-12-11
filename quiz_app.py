import tkinter as tk
from tkinter import messagebox
import json
import random
from datetime import datetime
import os
import sys

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Computer Science Quiz")
        self.root.geometry("700x750")
        self.root.configure(bg="#f0f8ff")
        self.root.resizable(False, False)

        # Find the folder
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.questions_file = os.path.join(self.base_path, "questions.json")

        self.all_questions = []
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.timer = 30
        self.timer_id = None

        if not self.load_questions():
            return

        self.show_selection_screen()

    def load_questions(self):
        try:
            with open(self.questions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not data:
                    messagebox.showerror("Error", "questions.json is empty!")
                    return False
                self.all_questions = data
                return True
        except FileNotFoundError:
            messagebox.showerror("Error", "questions.json not found!\n\nPut it in the same folder.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read file:\n{e}")
            return False

    def show_selection_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root,
                 text="COMPUTER HISTORY\n& FUNDAMENTALS QUIZ",
                 font=("Arial", 32, "bold"),
                 bg="#f0f8ff",
                 fg="#1a237e",
                 justify="center").pack(pady=(100, 60))

        tk.Label(self.root,
                 text="Click any option to start the quiz:",
                 font=("Arial", 22),
                 bg="#f0f8ff").pack(pady=30)

        # Each radio button starts the quiz when clicked
        self.choice = tk.StringVar()

        options = [
            ("10 Questions", 10),
            ("20 Questions", 20),
            ("30 Questions", 30),
            ("40 Questions", 40),
            ("50 Questions", 50),
            ("All 60 Questions", 60)
        ]

        for text, num in options:
            tk.Radiobutton(self.root,
                           text=text,
                           variable=self.choice,
                           value=str(num),
                           font=("Arial", 24, "bold"),
                           bg="#f0f8ff",
                           selectcolor="#81c784",
                           command=lambda n=num: self.start_quiz_now(n)  # Starts immediately
                           ).pack(pady=20)

    def start_quiz_now(self, num_questions):
        if num_questions == 60:
            self.questions = self.all_questions.copy()
        else:
            self.questions = random.sample(self.all_questions, num_questions)
        random.shuffle(self.questions)

        # Clear and start
        for widget in self.root.winfo_children():
            widget.destroy()

        self.build_quiz_gui()
        self.next_question()

    def build_quiz_gui(self):
        self.progress = tk.Label(self.root, text="", font=("Arial", 16, "bold"), bg="#f0f8ff", fg="#ad1457")
        self.progress.pack(pady=15)

        self.question_label = tk.Label(self.root, text="", font=("Arial", 18), bg="#f0f8ff", wraplength=640, justify="center")
        self.question_label.pack(pady=30)

        self.var = tk.StringVar()
        self.radios = []

        self.submit = tk.Button(self.root, text="Submit Answer", font=("Arial", 18), bg="#1976d2", fg="white", command=self.check_answer)
        self.submit.pack(pady=25)

        self.timer_label = tk.Label(self.root, text="Time left: 30s", font=("Arial", 20, "bold"), fg="red", bg="#f0f8ff")
        self.timer_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text="Score: 0", font=("Arial", 22, "bold"), fg="#2e7d32", bg="#f0f8ff")
        self.score_label.pack(pady=15)

        self.feedback = tk.Label(self.root, text="", font=("Arial", 20), bg="#f0f8ff")
        self.feedback.pack(pady=20)

    def next_question(self):
        if self.current_question >= len(self.questions):
            self.end_quiz()
            return

        self.submit.config(state="normal")  

        self.progress.config(text=f"Question {self.current_question+1} / {len(self.questions)}")
        q = self.questions[self.current_question]
        self.question_label.config(text=q["question"])

        for r in self.radios:
            r.destroy()
        self.radios = []
        self.var.set("")

        for opt in q["options"]:
            r = tk.Radiobutton(self.root, text=opt, variable=self.var, value=opt, font=("Arial", 16), bg="#f0f8ff")
            r.pack(anchor="w", padx=100, pady=10)
            self.radios.append(r)

        self.feedback.config(text="")
        self.start_timer()

    def start_timer(self):
        self.timer = 30
        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"Time left: {self.timer}s")
        if self.timer > 0:
            self.timer -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.feedback.config(text="Time's up!", fg="red")
            self.submit.config(state="disabled")
            self.root.after(2000, self.go_next)

    def check_answer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        ans = self.var.get()
        if not ans:
            self.feedback.config(text="Choose an answer!", fg="orange")
            return

        correct = self.questions[self.current_question]["answer"]
        if ans == correct:
            self.feedback.config(text="Correct!", fg="green")
            self.score += 1
        else:
            self.feedback.config(text=f"Wrong! → {correct}", fg="red")

        self.score_label.config(text=f"Score: {self.score}")
        self.submit.config(state="disabled")
        self.root.after(2500, self.go_next)

    def go_next(self):
        self.current_question += 1
        self.next_question()

    def end_quiz(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        total = len(self.questions)
        perc = (self.score / total * 100) if total else 0

        messagebox.showinfo("Quiz Complete!",
                            f"You scored {self.score} / {total}\n"
                            f"Accuracy: {perc:.1f}%\n\n"
                            "Thanks for playing!")

        try:
            with open(os.path.join(self.base_path, "high_scores.txt"), "a", encoding="utf-8") as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                f.write(f"{now} | {self.score}/{total} ({perc:.1f}%)\n")
        except:
            pass

        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()