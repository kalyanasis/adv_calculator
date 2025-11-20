#!/usr/bin/env python3
import math
import time
import ast
import tkinter as tk
from tkinter import ttk

# -------------------------------
# Safe expression evaluator (AST)
# -------------------------------
ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
}

ALLOWED_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log10,  # log base 10
    "ln": math.log,     # natural log
    "sqrt": math.sqrt,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
}

ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)
ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)


def _raise(msg="Invalid expression"):
    raise ValueError(msg)


def safe_eval(expr: str, trig_in_degrees=False) -> float:
    """
    Safely evaluate a math expression with allowed names and functions.
    Supports +, -, *, /, %, **, parentheses, and whitelisted functions.

    trig_in_degrees: if True, converts numeric arguments of sin/cos/tan from degrees to radians.
    """
    # Preprocess for power operator caret ^ -> **
    expr = expr.replace("^", "**")

    # Parse to AST
    try:
        node = ast.parse(expr, mode="eval")
    except Exception:
        _raise()

    def visit(n):
        if isinstance(n, ast.Expression):
            return visit(n.body)

        elif isinstance(n, ast.Num):  # Python <3.8
            return n.n

        elif isinstance(n, ast.Constant):  # Python 3.8+
            if isinstance(n.value, (int, float)):
                return n.value
            _raise()

        elif isinstance(n, ast.BinOp) and isinstance(n.op, ALLOWED_BINOPS):
            left = visit(n.left)
            right = visit(n.right)
            if isinstance(n.op, ast.Add):   return left + right
            if isinstance(n.op, ast.Sub):   return left - right
            if isinstance(n.op, ast.Mult):  return left * right
            if isinstance(n.op, ast.Div):   return left / right
            if isinstance(n.op, ast.Mod):   return left % right
            if isinstance(n.op, ast.Pow):   return left ** right
            _raise()

        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ALLOWED_UNARYOPS):
            operand = visit(n.operand)
            if isinstance(n.op, ast.UAdd):  return +operand
            if isinstance(n.op, ast.USub):  return -operand
            _raise()

        elif isinstance(n, ast.Name):
            if n.id in ALLOWED_NAMES:
                return ALLOWED_NAMES[n.id]
            _raise(f"Unknown name: {n.id}")

        elif isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name):
                _raise()
            func_name = n.func.id
            if func_name not in ALLOWED_FUNCS:
                _raise(f"Unknown function: {func_name}")
            args = [visit(a) for a in n.args]
            # Convert degrees to radians for trig
            if func_name in ("sin", "cos", "tan") and trig_in_degrees:
                args = [math.radians(arg) for arg in args]
            try:
                return ALLOWED_FUNCS[func_name](*args)
            except Exception:
                _raise("Bad function arguments")

        elif isinstance(n, ast.Expr):
            return visit(n.value)

        elif isinstance(n, ast.Tuple):
            _raise()  # disallow tuples

        else:
            _raise()

    result = visit(node)
    return result


# -------------------------------
# UI: Modern Tkinter (ttk themed)
# -------------------------------
class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Calculator")
        self.root.geometry("520x520")
        self.root.minsize(500, 480)
        self.root.bind("<Control-h>", self.toggle_history_event)
        self.root.bind("<Control-t>", self.toggle_theme_event)
        self.root.bind("<Control-d>", self.set_degrees_event)
        self.root.bind("<Control-r>", self.set_radians_event)

        # State
        self.memory = 0.0
        self.trig_in_degrees = True
        self.history_visible = True
        self.theme = "dark"

        self._configure_style()
        self._build_layout()
        self._bind_keys()
        self.just_evaluated = False

    def _configure_style(self):
        self.style = ttk.Style()
        # Prefer system theme fallback
        try:
            self.style.theme_use("clam")
        except:
            pass

        if self.theme == "dark":
            bg = "#23262E"
            surface = "#2A2E38"
            text = "#E6E6E6"
            accent = "#4C89FF"
            danger = "#D9534F"
            self.root.configure(bg=bg)

            self.style.configure("TFrame", background=bg)
            self.style.configure("Surface.TFrame", background=surface)
            self.style.configure("TLabel", background=bg, foreground=text)
            self.style.configure("Heading.TLabel", background=bg, foreground=text, font=("Segoe UI", 10, "bold"))

            self.style.configure("Display.TEntry",
                                 fieldbackground=surface,
                                 foreground=text,
                                 background=surface,
                                 padding=8,
                                 font=("Consolas", 16))

            self.style.configure("Calc.TButton",
                                 background=surface,
                                 foreground=text,
                                 padding=8,
                                 font=("Segoe UI", 11))
            self.style.map("Calc.TButton",
                           background=[("active", "#343A46")],
                           foreground=[("disabled", "#888")])

            self.style.configure("Accent.Calc.TButton",
                                 background=accent,
                                 foreground="#FFFFFF")
            self.style.map("Accent.Calc.TButton",
                           background=[("active", "#3D73D6")])

            self.style.configure("Danger.Calc.TButton",
                                 background=danger,
                                 foreground="#FFFFFF")
            self.style.map("Danger.Calc.TButton",
                           background=[("active", "#C64541")])

            self.style.configure("History.TFrame", background=surface)
            self.style.configure("History.TLabel", background=surface, foreground=text)
            self.style.configure("History.TButton", background=surface, foreground=text, padding=6)
        else:
            bg = "#F7F7F7"
            surface = "#FFFFFF"
            text = "#222"
            accent = "#2F6FED"
            danger = "#D9534F"
            self.root.configure(bg=bg)

            self.style.configure("TFrame", background=bg)
            self.style.configure("Surface.TFrame", background=surface)
            self.style.configure("TLabel", background=bg, foreground=text)
            self.style.configure("Heading.TLabel", background=bg, foreground=text, font=("Segoe UI", 10, "bold"))

            self.style.configure("Display.TEntry",
                                 fieldbackground=surface,
                                 foreground=text,
                                 background=surface,
                                 padding=8,
                                 font=("Consolas", 16))

            self.style.configure("Calc.TButton",
                                 background=surface,
                                 foreground=text,
                                 padding=8,
                                 font=("Segoe UI", 11))
            self.style.map("Calc.TButton",
                           background=[("active", "#EDEDED")])

            self.style.configure("Accent.Calc.TButton",
                                 background=accent,
                                 foreground="#FFFFFF")
            self.style.map("Accent.Calc.TButton",
                           background=[("active", "#2256C0")])

            self.style.configure("Danger.Calc.TButton",
                                 background=danger,
                                 foreground="#FFFFFF")
            self.style.map("Danger.Calc.TButton",
                           background=[("active", "#C64541")])

            self.style.configure("History.TFrame", background=surface)
            self.style.configure("History.TLabel", background=surface, foreground=text)
            self.style.configure("History.TButton", background=surface, foreground=text, padding=6)

    def _build_layout(self):
        # Top bar
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=12, pady=(12, 6))

        # Mode toggle
        self.mode_var = tk.StringVar(value="Degrees")
        mode_label = ttk.Label(top, text="Mode:", style="Heading.TLabel")
        mode_label.pack(side="left")
        self.mode_btn = ttk.Button(top, textvariable=self.mode_var, style="Calc.TButton", command=self.toggle_mode)
        self.mode_btn.pack(side="left", padx=(6, 12))

        # Theme toggle
        self.theme_btn = ttk.Button(top, text="Toggle theme", style="Calc.TButton", command=self.toggle_theme)
        self.theme_btn.pack(side="left")

        # History toggle
        self.history_btn = ttk.Button(top, text="Toggle history", style="Calc.TButton", command=self.toggle_history)
        self.history_btn.pack(side="left", padx=(6, 0))

        # Display
        display_frame = ttk.Frame(self.root, style="Surface.TFrame")
        display_frame.pack(fill="x", padx=12, pady=(6, 12))
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(display_frame, textvariable=self.entry_var, style="Display.TEntry")
        self.entry.pack(fill="x", padx=8, pady=8)
        self.entry.focus_set()

        # Error label
        self.error_var = tk.StringVar(value="")
        self.error_label = ttk.Label(self.root, textvariable=self.error_var, style="TLabel")
        self.error_label.pack(fill="x", padx=14)

        # Main content: buttons + history
        content = ttk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        # Button grid
        btns = ttk.Frame(content, style="Surface.TFrame")
        btns.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.rowconfigure(0, weight=1)

        # History panel
        self.history_frame = ttk.Frame(content, style="History.TFrame")
        self.history_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        content.columnconfigure(1, weight=2)

        self.history_label = ttk.Label(self.history_frame, text="History", style="Heading.TLabel")
        self.history_label.pack(anchor="w", padx=8, pady=(8, 4))

        self.history_list = tk.Listbox(self.history_frame, activestyle="none", height=10)
        self.history_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.history_list.bind("<<ListboxSelect>>", self.on_history_select)

        # Buttons layout
        # Row definitions
        rows = [
            ["MC", "MR", "M+", "M-", "C", "⌫"],
            ["(", ")", "%", "^", "√", "/"],
            ["7", "8", "9", "*", "sin", "cos"],
            ["4", "5", "6", "-", "tan", "log"],
            ["1", "2", "3", "+", "ln", "x!"],
            ["0", ".", "pi", "e", "=", ""],
        ]

        for r, row in enumerate(rows):
            btns.rowconfigure(r, weight=1)
            for c, label in enumerate(row):
                btns.columnconfigure(c, weight=1)
                if not label:
                    continue
                style = "Calc.TButton"
                if label == "C" or label == "⌫":
                    style = "Danger.Calc.TButton"
                if label == "=":
                    style = "Accent.Calc.TButton"

                ttk.Button(btns, text=label, style=style,
                           command=lambda x=label: self.on_button(x)).grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

    def _bind_keys(self):
        # Numeric and operator keys
        for char in "0123456789+-*/().%^":
            self.root.bind(char, self._insert_char)
        self.root.bind(".", self._insert_char)
        self.root.bind("<Return>", self._evaluate_event)
        self.root.bind("<KP_Enter>", self._evaluate_event)
        self.root.bind("<BackSpace>", self._backspace_event)
        self.root.bind("<Delete>", self._clear_event)
        self.root.bind("<Escape>", self._clear_event)

        # Function shortcuts: type name + ( )
        # You can type sin(45) directly; no special bindings needed.

    # -------------------------------
    # Button and key handlers
    # -------------------------------
    def on_button(self, label):
        self.error_var.set("")
        if label == "=":
            self.evaluate()
        elif label == "C":
            self.clear()
        elif label == "⌫":
            self.backspace()
        elif label in ("MC", "MR", "M+", "M-"):
            self.memory_action(label)
        elif label == "√":
            self._sqrt()
        elif label == "x!":
            self.insert_text("factorial(")
        elif label in ("sin", "cos", "tan", "log", "ln"):
            self.insert_text(f"{label}(")
        elif label in ("pi", "e"):
            self.insert_text(label)
        else:
            self.insert_text(label)

    def _insert_char(self, event):
        self.error_var.set("")
        self.insert_text(event.char)

    def insert_text(self, text):
        # If last action was evaluation, clear before inserting
        if self.just_evaluated:
            self.entry_var.set("")
            self.just_evaluated = False
        self.entry.insert(tk.END, text)

    def backspace(self):
        s = self.entry_var.get()
        if s:
            self.entry_var.set(s[:-1])

    def _backspace_event(self, _):
        self.backspace()

    def clear(self):
        self.entry_var.set("")
        self.error_var.set("")

    def _clear_event(self, _):
        self.clear()

    def evaluate(self):
        expr = self.entry_var.get().strip()
        if not expr:
            return
        try:
            result = safe_eval(expr, trig_in_degrees=self.trig_in_degrees)
            if isinstance(result, float) and result.is_integer():
                display = str(int(result))
            else:
                display = str(result)
            self.entry_var.set(display)
            self.error_var.set("")
            self.add_history(expr, display)
            self.just_evaluated = True   # <-- mark evaluation
        except Exception as e:
            self.error_var.set(str(e) or "Invalid expression")
            self.just_evaluated = False

    def _evaluate_event(self, _):
        self.evaluate()

    def _sqrt(self):
        exp = self.entry_var.get().strip()
        if not exp:
            self.just_evaluated = True
            return
        try:
            value = float(exp)
            if value < 0:
                raise ValueError
            result = math.sqrt(value)
            display = str(result)
            self.entry_var.set(display)
            self.error_var.set("")
            self.add_history(value, display)
            self.just_evaluated = True
        except ValueError as e:
            self.just_evaluated = False
            self.error_var.set(str(e) or "Cannot take square root of negative number")
        except Exception as e:
            self.just_evaluated = False
            self.error_var.set(str(e) or "Invalid sqrt operation")


    # -------------------------------
    # History
    # -------------------------------
    def add_history(self, expr, result):
        ts = time.strftime("%H:%M:%S")
        item = f"[{ts}] {expr} = {result}"
        self.history_list.insert(tk.END, item)
        self.history_list.see(tk.END)

    def on_history_select(self, _):
        sel = self.history_list.curselection()
        if not sel:
            return
        item = self.history_list.get(sel[0])
        # Extract the expression part between timestamp and '='
        try:
            expr = item.split("] ", 1)[1].rsplit(" = ", 1)[0]
            self.entry_var.set(expr)
            self.entry.icursor(tk.END)
            self.entry.focus_set()
        except Exception:
            pass

    def toggle_history(self):
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.history_frame.grid()
        else:
            self.history_frame.grid_remove()

    def toggle_history_event(self, _):
        self.toggle_history()

    # -------------------------------
    # Memory keys
    # -------------------------------
    def memory_action(self, action):
        try:
            current = float(self.entry_var.get()) if self.entry_var.get() else 0.0
        except ValueError:
            self.error_var.set("Not a number to use with memory")
            return

        if action == "MC":
            self.memory = 0.0
            self.error_var.set("Memory cleared")
        elif action == "MR":
            self.entry_var.set(str(self.memory))
            self.error_var.set("")
        elif action == "M+":
            self.memory += current
            self.error_var.set(f"Memory: {self.memory}")
        elif action == "M-":
            self.memory -= current
            self.error_var.set(f"Memory: {self.memory}")

    # -------------------------------
    # Mode and theme
    # -------------------------------
    def toggle_mode(self):
        self.trig_in_degrees = not self.trig_in_degrees
        self.mode_var.set("Degrees" if self.trig_in_degrees else "Radians")
        self.error_var.set("")

    def set_degrees_event(self, _):
        self.trig_in_degrees = True
        self.mode_var.set("Degrees")

    def set_radians_event(self, _):
        self.trig_in_degrees = False
        self.mode_var.set("Radians")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._configure_style()

    def toggle_theme_event(self, _):
        self.toggle_theme()


def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
