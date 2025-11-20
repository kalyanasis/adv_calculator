import tkinter as tk
import math
from tkinter import messagebox, Scrollbar

memory_value = 0.0
last_answer = 0.0
clr_flag = False
exp_current = ""
exp_prev = ""
def clear_screen():
    global clr_flag
    if clr_flag:
        screen_var.set("")
        clr_flag = False

def on_key_press(event):    
    key = event.keysym
    char = event.char
    global exp_current
    global exp_prev
    print("*******", key, char)

    # Press Enter or Return → Evaluate
    if key in ("Return", "KP_Enter"):
        calculate()
    # Escape → Clear screen
    elif key == "Escape":
        screen_var.set("")
    # Backspace → delete last character
    elif key == "BackSpace":
        screen_var.set(screen_var.get()[:-1])
    # Allow typing numbers and math symbols
    elif char in "0123456789+-*/().":
        print("exp_current--------", exp_current)
        print("exp_prev--------", exp_prev)
        screen_var.set(screen_var.get() + char)
    # Shortcut keys
    elif key.lower() == "r":  # r → reciprocal
        apply_reciprocal()
    elif key.lower() == "s":  # s → square
        apply_square()
    elif key.lower() == "q":  # q → square root
        apply_sqrt()
    elif key.lower() == "p":  # p → percentage
        apply_percentage()


def on_click(event):
    
    text = event.widget.cget("text")
    global clr_flag
    global exp_current
    global exp_prev

    clear_screen()
    if text == "=":
        calculate()
        clr_flag = True
    elif text == "C":
        screen_var.set("")
    elif text == "⌫":
        screen_var.set(screen_var.get()[:-1])
    elif text == "π":
        exp_current = text
        screen_var.set(screen_var.get() + str(math.pi))
    elif text == "e":
        exp_current = text
        screen_var.set(screen_var.get() + str(math.e))
    elif text == "ANS":
        screen_var.set(screen_var.get() + str(last_answer))
    elif text in ["sin", "cos", "tan", "log"]:
        exp_current = text
        screen_var.set(screen_var.get() + text + "(")
    elif text == "√":
        exp_current = text
        apply_sqrt()
    elif text == "1/x":
        exp_current = text
        apply_reciprocal()
    elif text == "x²":
        exp_current = text
        apply_square()
    elif text == "%":
        exp_current = text
        apply_percentage()
    elif text in ["+", "-", "*", "/"]:
        exp_current = text
        append_operator(text)
    elif text in ["M+", "M-", "MR", "MC"]:
        handle_memory(text)
    else:
        print("screen =======", exp_current, clr_flag, exp_prev)
        if clr_flag:
            clear_screen
        print("screen var========", screen_var.get(), text,)
        screen_var.set(screen_var.get() + text)
        clr_flag = False


def append_operator(op):
    current = screen_var.get()
    if not current:
        return
    if current[-1] in "+-*/":
        screen_var.set(current[:-1] + op)
    else:
        screen_var.set(current + op)


def calculate(event=None):
    global last_answer
    global clr_flag
    expression = screen_var.get()
    original_expr = expression
    try:
        expression = expression.replace("^", "**")
        expression = expression.replace("ANS", str(last_answer))
        for func in ["sin", "cos", "tan", "log", "sqrt"]:
            expression = expression.replace(func + "(", f"math.{func}(")
        result = eval(expression)
        screen_var.set(result)
        add_to_history(original_expr, result)
        last_answer = result
        update_ans_label()
        clr_flag = True
    except Exception:
        messagebox.showerror("Error", "Invalid Expression")
        screen_var.set("")
        clr_flag = False


def apply_square():
    global clr_flag
    exp = screen_var.get()
    if not exp:
        return
    try:
        value = float(eval(exp.replace("ANS", str(last_answer))))
        result = value ** 2
        screen_var.set(str(result))
        add_to_history(f"({exp})²", result)
        clr_flag = True
    except Exception:
        messagebox.showerror("Error", "Invalid square operation")
        clr_flag = False


def apply_sqrt():
    global clr_flag
    exp = screen_var.get()
    print("PP-----", exp)
    if not exp:
        return
    try:
        value = float(eval(exp.replace("ANS", str(last_answer))))
        if value < 0:
            raise ValueError
        result = math.sqrt(value)
        screen_var.set(str(result))
        add_to_history(f"√({exp})", result)        
    except ValueError as e:
        messagebox.showerror("Error", "Cannot take square root of negative number")
        clr_flag = False
    except Exception as e:
        messagebox.showerror("Error", "Invalid sqrt operation")
        clr_flag = False


def apply_reciprocal():
    exp = screen_var.get()
    if not exp:
        return
    try:
        value = float(eval(exp.replace("ANS", str(last_answer))))
        if value == 0:
            raise ZeroDivisionError
        result = 1 / value
        screen_var.set(str(result))
        add_to_history(f"1/({exp})", result)
    except ZeroDivisionError:
        messagebox.showerror("Error", "Division by Zero")
    except Exception:
        messagebox.showerror("Error", "Invalid Reciprocal Operation")


def apply_percentage():
    exp = screen_var.get()
    if not exp:
        return
    try:
        for i in range(len(exp)-1, -1, -1):
            if exp[i] in "+-*/":
                operator = exp[i]
                left = exp[:i]
                right = exp[i+1:]
                base = float(eval(left.replace("ANS", str(last_answer))))
                perc = float(eval(right.replace("ANS", str(last_answer)))) / 100
                if operator in "+-":
                    value = base + base * perc if operator == "+" else base - base * perc
                elif operator == "*":
                    value = base * perc
                elif operator == "/":
                    value = base / perc
                screen_var.set(str(value))
                return
        value = float(eval(exp.replace("ANS", str(last_answer)))) / 100
        screen_var.set(str(value))
    except Exception:
        messagebox.showerror("Error", "Invalid use of %")


def handle_memory(action):
    global memory_value
    try:
        if action == "M+":
            memory_value += float(screen_var.get() or 0)
        elif action == "M-":
            memory_value -= float(screen_var.get() or 0)
        elif action == "MR":
            screen_var.set(screen_var.get() + str(memory_value))
        elif action == "MC":
            memory_value = 0.0
        update_memory_label()
    except:
        messagebox.showerror("Error", "Invalid memory operation")


def update_memory_label():
    if memory_value != 0:
        memory_label.config(text=f"Memory: {memory_value:.6g}")
    else:
        memory_label.config(text="")


def update_ans_label():
    ans_label.config(text=f"ANS: {last_answer:.6g}")


def add_to_history(expr, result):
    global exp_current
    global exp_prev
    global clr_flag
    print("add_to_history ====", exp_current, exp_prev, clr_flag)
    if exp_current == str(exp_prev):
        clr_flag = False
    else:
        clr_flag = True
    
    exp_current = exp_prev

    history_text.insert(tk.END, f"{expr} = {result}\n")
    history_text.see(tk.END)


def clear_history():
    history_text.delete(1.0, tk.END)


# --- Main Window ---
root = tk.Tk()
root.title("🧮 Advanced Python Calculator")
root.geometry("440x700")
root.config(bg="#1e1e1e")
root.resizable(False, False)

screen_var = tk.StringVar()

entry_frame = tk.Frame(root, bg="#1e1e1e")
entry_frame.pack(pady=15)
entry_frame.focus_set()
# tk.focus()
screen = tk.Entry(entry_frame, textvar=screen_var, font="Consolas 24", bg="#2d2d2d",fg="white", bd=0, insertbackground="white", relief="flat", justify="right", width=20)
screen.pack(ipady=12, padx=10)

memory_label = tk.Label(root, text="", font="Consolas 11 italic", bg="#1e1e1e", fg="#00cec9")
memory_label.pack(pady=(0, 2))
ans_label = tk.Label(root, text="ANS: 0", font="Consolas 11 italic", bg="#1e1e1e", fg="#55efc4")
ans_label.pack(pady=(0, 8))

# buttons = [
#     ["MC", "MR", "M+", "M-", "C"],
#     ["%", "/", "(", ")", "⌫"],
#     ["7", "8", "9", "*", "x²"],
#     ["4", "5", "6", "-", "1/x"],
#     ["1", "2", "3", "+", "."],
#     ["0", "π", "e", "=", "ANS"],
#     ["sin", "cos", "tan", "log", "√"]
# ]
buttons = [
    ["MC", "MR", "M+", "M-", "C"],
    ["%", "/", "(", ")", "⌫"],
    ["7", "8", "9", "*", "x²"],
    ["4", "5", "6", "-", "1/x"],
    ["1", "2", "3", "+", "√"],
    ["0", ".", "e","π" , "="],
    ["sin", "cos", "tan", "log", "ANS"]
]

button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack()

# --- Color Rules ---
sci_buttons = {"sin", "cos", "tan", "log", "π", "e", "x²", "1/x", "ANS", "√"}
equal_color = "#00b894"
red_buttons = {"C", "⌫"}

for row in buttons:
    frame = tk.Frame(button_frame, bg="#1e1e1e")
    frame.pack(expand=True, fill="both")
    for text in row:
        if text in sci_buttons:
            bg_color = "#00cec9"
            fg_color = "black"
        elif text in red_buttons:
            bg_color = "#d63031"
            fg_color = "white"
        elif text == "=":
            bg_color = equal_color
            fg_color = "black"
        else:
            bg_color = "#3c3c3c"
            fg_color = "white"

        btn = tk.Button(frame, text=text, font="Consolas 16 bold",
                        bg=bg_color, fg=fg_color,
                        activebackground="#81ecec", activeforeground="black",
                        relief="flat", padx=10, pady=10)
        btn.pack(side="left", expand=True, fill="both", padx=4, pady=4)
        btn.bind("<Button-1>", on_click)

# --- History Section ---
history_label = tk.Label(root, text="History", font="Consolas 12 bold", bg="#1e1e1e", fg="#b2bec3")
history_label.pack(pady=(10, 0))

history_frame = tk.Frame(root, bg="#1e1e1e")
history_frame.pack(fill="both", expand=True, padx=10, pady=5)

scrollbar = Scrollbar(history_frame)
scrollbar.pack(side="right", fill="y")

history_text = tk.Text(history_frame, height=15, bg="#2d2d2d", fg="#dfe6e9", font="Consolas 11", yscrollcommand=scrollbar.set, relief="flat")
history_text.pack(fill="both", expand=True)
scrollbar.config(command=history_text.yview)

clear_btn = tk.Button(root, text="Clear History", font="Consolas 11", bg="#d63031", fg="white",relief="flat", command=clear_history)
clear_btn.pack(pady=8)
root.bind_all("<Key>", on_key_press)

root.mainloop()
