import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x500")

        self.expenses = []
        self.load_data()

        # Поля ввода
        tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(root, textvariable=self.category_var,
                                           values=["Еда", "Транспорт", "Развлечения", "Другое"])
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.current(0)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        tk.Button(root, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10, pady=5)

        # Таблица для отображения
        self.tree = ttk.Treeview(root, columns=("ID", "Сумма", "Категория", "Дата"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=100)
        self.tree.column("Категория", width=150)
        self.tree.column("Дата", width=150)
        self.tree.grid(row=1, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтры", padx=5, pady=5)
        filter_frame.grid(row=2, column=0, columnspan=7, padx=10, pady=5, sticky="ew")

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                  values=["Все", "Еда", "Транспорт", "Развлечения", "Другое"])
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        self.filter_category_combo.current(0)

        tk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.filter_date_from = tk.Entry(filter_frame)
        self.filter_date_from.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Дата до (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
        self.filter_date_to = tk.Entry(filter_frame)
        self.filter_date_to.grid(row=0, column=5, padx=5)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=6, padx=10)
        tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=7, padx=5)

        # Кнопка подсчёта суммы за период
        tk.Button(root, text="Подсчитать сумму за период", command=self.calc_sum_period).grid(row=3, column=0, columnspan=7, pady=10)

        self.status_label = tk.Label(root, text="", fg="green")
        self.status_label.grid(row=4, column=0, columnspan=7)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.refresh_table()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        else:
            self.expenses = []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректная сумма: {e}")
            return

        category = self.category_var.get().strip()
        if not category:
            messagebox.showerror("Ошибка", "Введите категорию")
            return

        date_str = self.date_entry.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        self.expenses.append({
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str
        })
        self.save_data()
        self.refresh_table()
        self.status_label.config(text=f"Расход {amount} руб. добавлен!")
        self.amount_entry.delete(0, tk.END)

    def refresh_table(self, filtered_expenses=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = filtered_expenses if filtered_expenses is not None else self.expenses
        for e in data:
            self.tree.insert("", tk.END, values=(e["id"], e["amount"], e["category"], e["date"]))

    def apply_filter(self):
        filtered = self.expenses[:]

        # Фильтр по категории
        cat = self.filter_category_var.get()
        if cat != "Все":
            filtered = [e for e in filtered if e["category"] == cat]

        # Фильтр по дате
        from_date = self.filter_date_from.get().strip()
        to_date = self.filter_date_to.get().strip()

        if from_date:
            try:
                datetime.strptime(from_date, "%Y-%m-%d")
                filtered = [e for e in filtered if e["date"] >= from_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'от'")
                return

        if to_date:
            try:
                datetime.strptime(to_date, "%Y-%m-%d")
                filtered = [e for e in filtered if e["date"] <= to_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'до'")
                return

        self.refresh_table(filtered)
        self.status_label.config(text=f"Показано {len(filtered)} записей")

    def reset_filter(self):
        self.filter_category_combo.current(0)
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
        self.status_label.config(text="Фильтры сброшены")

    def calc_sum_period(self):
        from_date = self.filter_date_from.get().strip()
        to_date = self.filter_date_to.get().strip()

        if not from_date or not to_date:
            messagebox.showwarning("Предупреждение", "Укажите обе даты для подсчёта суммы за период")
            return

        try:
            datetime.strptime(from_date, "%Y-%m-%d")
            datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return

        total = sum(e["amount"] for e in self.expenses if from_date <= e["date"] <= to_date)
        messagebox.showinfo("Сумма за период", f"Сумма расходов с {from_date} по {to_date}: {total:.2f} руб.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
