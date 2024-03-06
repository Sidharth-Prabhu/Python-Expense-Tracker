import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from os.path import exists
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as reportlab_colors
from reportlab.platypus import Spacer
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.flowables import Image as PlatypusImage
from reportlab.pdfgen import canvas
import io

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")

        self.db_file = "expenses.db"
        self.create_database()
        self.load_expenses()

        self.create_widgets()
        self.create_context_menu()

    def create_database(self):
        if not exists(self.db_file):
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute('''CREATE TABLE expenses
                         (date text, category text, amount real)''')
            conn.commit()
            conn.close()

    def load_expenses(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT * FROM expenses')
        self.expenses = c.fetchall()
        conn.close()

        self.expenses = [(date, category, float(amount))
                         for date, category, amount in self.expenses]

    def save_expense(self, date, category, amount):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('INSERT INTO expenses VALUES (?, ?, ?)',
                  (date, category, amount))
        conn.commit()
        conn.close()

    def delete_expense(self):
        item = self.tree_expenses.selection()[0]
        values = self.tree_expenses.item(item, 'values')
        if values:
            confirm = messagebox.askyesno(
                "Confirm Delete", "Are you sure you want to delete this expense?")
            if confirm:
                conn = sqlite3.connect(self.db_file)
                c = conn.cursor()
                c.execute(
                    'DELETE FROM expenses WHERE date=? AND category=? AND amount=?', values)
                conn.commit()
                conn.close()
                self.load_expenses()
                self.update_expenses()
        else:
            messagebox.showwarning(
                "Warning", "Please select an expense to delete.")

    def edit_expense(self):
        item = self.tree_expenses.selection()[0]
        values = self.tree_expenses.item(item, 'values')
        if values:
            date, category, amount = values
            self.entry_date.delete(0, tk.END)
            self.entry_date.insert(0, date)
            self.entry_category.delete(0, tk.END)
            self.entry_category.insert(0, category)
            self.entry_amount.delete(0, tk.END)
            self.entry_amount.insert(0, amount)
        else:
            messagebox.showwarning(
                "Warning", "Please select an expense to edit.")

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Delete", command=self.delete_expense)
        self.context_menu.add_command(label="Edit", command=self.edit_expense)
        self.tree_expenses.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def create_widgets(self):
        self.label_date = tk.Label(self, text="Date:")
        self.label_date.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry_date = tk.Entry(self)
        self.entry_date.grid(row=0, column=1, padx=10, pady=5)

        self.label_category = tk.Label(self, text="Category:")
        self.label_category.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_category = tk.Entry(self)
        self.entry_category.grid(row=1, column=1, padx=10, pady=5)

        self.label_amount = tk.Label(self, text="Amount:")
        self.label_amount.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_amount = tk.Entry(self)
        self.entry_amount.grid(row=2, column=1, padx=10, pady=5)

        self.button_add_expense = tk.Button(
            self, text="Add Expense", command=self.add_expense)
        self.button_add_expense.grid(row=3, columnspan=2, pady=10)

        self.button_visualize = tk.Button(
            self, text="Visualize Data", command=self.visualize_data)
        self.button_visualize.grid(row=6, columnspan=2, pady=10)

        self.button_visualize = tk.Button(
            self, text="Generate Receipt", command=self.generate_receipt)
        self.button_visualize.grid(row=8, columnspan=2, pady=10)

        self.tree_expenses = ttk.Treeview(self, columns=(
            "Date", "Category", "Amount"), show="headings", height=10)
        self.tree_expenses.heading("Date", text="Date")
        self.tree_expenses.heading("Category", text="Category")
        self.tree_expenses.heading("Amount", text="Amount")
        self.tree_expenses.column("Date", width=100)
        self.tree_expenses.column("Category", width=150)
        self.tree_expenses.column("Amount", width=100)
        self.tree_expenses.grid(row=4, columnspan=2, padx=10)

        self.label_total = tk.Label(
            self, text="Total Expenses: $0.00", font=("Arial", 12))
        self.label_total.grid(row=5, columnspan=2, pady=10)

        self.update_expenses()

    def add_expense(self):
        date = self.entry_date.get()
        category = self.entry_category.get()
        amount = self.entry_amount.get()

        if date and category and amount:
            self.save_expense(date, category, amount)
            self.load_expenses()
            self.update_expenses()
            self.entry_date.delete(0, tk.END)
            self.entry_category.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter all fields.")

    def visualize_data(self):
        dates = [expense[0] for expense in self.expenses]
        amounts = [expense[2] for expense in self.expenses]
        
        fig, ax = plt.subplots()
        colors = cm.rainbow(np.linspace(0, 1, len(dates)))
        bars = ax.bar(dates, amounts, color=colors)
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount')
        ax.set_title('Expense Visualization')
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=2, rowspan=8, padx=10, pady=10, sticky="nsew")
        canvas.draw()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)


    def update_expenses(self):
        self.tree_expenses.delete(*self.tree_expenses.get_children())
        total = 0
        for expense in self.expenses:
            self.tree_expenses.insert("", "end", values=expense)
            total += float(expense[2])
        self.label_total.config(text=f"Total Expenses: ${total:.2f}")
    
    def generate_receipt(self):
        receipt_filename = "expense-receipt.pdf"
        dates = [expense[0] for expense in self.expenses]
        categories = [expense[1] for expense in self.expenses]
        amounts = [expense[2] for expense in self.expenses]

        # Create a PDF document
        doc = SimpleDocTemplate(receipt_filename, pagesize=letter)
        elements = []

        c = canvas.Canvas(receipt_filename, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Expense Receipt")
        c.save()
        data = [['Date', 'Category', 'Amount']]
        for date, category, amount in zip(dates, categories, amounts):
            data.append([date, category, amount])

        table = Table(data)
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), reportlab_colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0),
                             reportlab_colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1),
                             reportlab_colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, reportlab_colors.black)])

        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 12))
        fig, ax = plt.subplots()
        bar_colors = cm.rainbow(np.linspace(0, 1, len(dates)))
        bars = ax.bar(dates, amounts, color=bar_colors)
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount')
        ax.set_title('Expense Visualization')

        temp_image_file = io.BytesIO()
        fig.savefig(temp_image_file, format='png')
        temp_image_file.seek(0)

        image = PlatypusImage(temp_image_file, width=400, height=300)

        elements.append(image)

        plt.close(fig)

        doc.build(elements)

        messagebox.showinfo("Receipt Generated",
                            f"Receipt saved as {receipt_filename}")
if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
