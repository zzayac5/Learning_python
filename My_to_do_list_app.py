import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from datetime import date, datetime

# ───── data model ───────────────────────────────────────────────
@dataclass
class Task:
    text: str
    done: bool = False
    priority: int = 2              # 1=High,2=Med,3=Low
    due: date | None = None
    category: str = ""
    est_min: int = 0               # estimated minutes
    hard: bool = False              # New: hard vs soft deadline checkbox

    # for Treeview we expose a tuple representation
    def display(self) -> tuple[str, str, str, str, str]:
        status = "✅" if self.done else " "
        due_str = self.due.isoformat() if self.due else ""
        hard_flag= "H" if self.hard else ""   # flag for hard vs soft deadline
        return (
            status,
            self.text,
            str(self.priority),
            due_str,
            hard_flag,
            self.category or "",
        )

root = tk.Tk()

class TodoApp:
    def __init__(self, root: tk.Tk):
        # window
        self.root = root
        self.root.title("Advanced To‑Do")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # master list
        self.tasks: list[Task] = []

        # ── input pane ──────────────────────────────────────────
        input_frame = tk.LabelFrame(root, text="New Task")
        input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(input_frame, text="Task").grid(row=0, column=0, sticky="e", padx=1, pady=2)
        self.entry_text = tk.Entry(input_frame, width=30)
        self.entry_text.grid(row=0, column=1, sticky="w", padx=1, pady=2)

        tk.Label(input_frame, text="Priority").grid(row=0, column=2, sticky="e", padx=2)
        self.priority_var = tk.IntVar(value=2)
        tk.Spinbox(
            input_frame, from_=1, to=5, textvariable=self.priority_var, width=3
        ).grid(row=0, column=3, padx=2, pady=2)

        tk.Label(input_frame, text="Due‑date (YYYY‑MM‑DD)").grid(row=1, column=0, sticky="e", padx=2)
        self.entry_due = tk.Entry(input_frame, width=15)
        self.entry_due.grid(row=1, column=1, sticky="w", padx=1, pady=2)

        self.hard_var = tk.BooleanVar(value=False)          #Hard vs Soft deadline evaluation feature addition
        tk.Checkbutton(
            input_frame,
            text="Hard deadline",
            variable=self.hard_var
        ).grid(row=1, column=2, padx=1, sticky="w")

        tk.Label(input_frame, text="Category").grid(row=1, column=3, sticky="e", padx=2)
        self.entry_cat = tk.Entry(input_frame, width=12)
        self.entry_cat.grid(row=1, column=4, padx=2, pady=2)

        tk.Label(input_frame, text="Est. Min").grid(row=2, column=0, sticky="e", padx=2)
        self.entry_est = tk.Entry(input_frame, width=6)
        self.entry_est.grid(row=2, column=1, sticky="w", padx=2, pady=2)

        tk.Button(
            input_frame, text="Add Task", command=self.add_task
        ).grid(row=2, column=3, padx=2, pady=4, sticky="e")

        self.root.bind("<Return>", lambda e: self.add_task())

        # ── treeview display ───────────────────────────────────
        cols = ("Status", "Task", "Pr", "Due", "Hard", "Cat")
        self.tree = ttk.Treeview(root, columns=cols, show="headings", height=14)
        for c, w in zip(cols, (60, 260, 40, 100, 50, 100)):
            self.tree.heading(c, text=c, command=lambda col=c: self.sort_by(col))
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(padx=10, pady=5)
        self.tree.tag_configure("overdue", foreground="red")

        # add scrollbar
        ttk.Scrollbar(root, orient="vertical", command=self.tree.yview).place(x=690, y=170, height=255)
        self.tree.configure(yscrollcommand=lambda f, l: None)  # dummy; scrollbar handles it

        # ── action buttons ─────────────────────────────────────
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Toggle Complete", command=self.toggle_complete).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Show Today", command=self.filter_today).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Show All", command=self.show_all).grid(row=0, column=3, padx=5)

    # ── helpers ───────────────────────────────────────────────
    def parse_due(self, s: str) -> date | None:
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Date format", "Use YYYY‑MM‑DD")
            return None

    def refresh_tree(self, rows: list[Task] | None = None):
        self.tree.delete(*self.tree.get_children())
        now = datetime.now().date()
        for t in (rows if rows is not None else self.tasks):
            tags = []
            if t.due and t.due < now and not t.done:
                tags.append("overdue")
            self.tree.insert("", "end", values=t.display(), tags=tags)

    # ── CRUD ops ──────────────────────────────────────────────
    def add_task(self):
        text = self.entry_text.get().strip()
        if not text:
            return
        due = self.parse_due(self.entry_due.get().strip())
        if self.entry_due.get().strip() and due is None:
            return  # parse failed
        try:
            est = int(self.entry_est.get() or 0)
        except ValueError:
            messagebox.showwarning("Est. minutes", "Estimated minutes must be a number")
            return
        task = Task(
            text=text,
            priority=self.priority_var.get(),
            due=due,
            category=self.entry_cat.get().strip(),
            est_min=est,
            hard=self.hard_var.get()
        )
        self.tasks.append(task)
        self.refresh_tree()

        # clear inputs
        self.entry_text.delete(0, tk.END)
        self.entry_due.delete(0, tk.END)
        self.entry_cat.delete(0, tk.END)
        self.entry_est.delete(0, tk.END)
        self.priority_var.set(2)
        self.hard_var.set(False)

    def current_index(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.index(sel[0])

    def toggle_complete(self):
        idx = self.current_index()
        if idx is None:
            return
        self.tasks[idx].done = not self.tasks[idx].done
        self.refresh_tree()

    def delete_task(self):
        idx = self.current_index()
        if idx is None:
            return
        del self.tasks[idx]
        self.refresh_tree()

    # ── filtering & sorting ──────────────────────────────────
    def filter_today(self):
        today = date.today()
        self.refresh_tree([t for t in self.tasks if t.due == today])

    def show_all(self):
        self.refresh_tree()

    def sort_by(self, column_name: str):
        key_funcs = {
            "Status": lambda t: t.done,
            "Task": lambda t: t.text.lower(),
            "Pr": lambda t: t.priority,
            "Due": lambda t: t.due or date.max,
            "Hard": lambda t: not t.hard,
            "Cat": lambda t: t.category.lower(),
        }
        self.tasks.sort(key=key_funcs[column_name])
        self.refresh_tree()

# ───── start app ──────────────────────────────────────────────
app = TodoApp(root)
root.mainloop()
