import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# ----------------1. إنشاء قاعدة البيانات والتداول----------------
conn = sqlite3.connect("generator_subscribers.db")
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    amperes REAL,
    amount REAL,
    status TEXT DEFAULT 'unpaid'
)
"""
)
conn.commit()


# ----------------2. الدوال البرمجية (Logic)----------------
def fetch_data():
    # تفريغ الجداول في الواجهة
    for item in tree_unpaid.get_children():
        tree_unpaid.delete(item)
    for item in tree_paid.get_children():
        tree_paid.delete(item)

    # جلب المشتركين غير المسددين
    cursor.execute(
        "SELECT id, name, phone, amperes, amount FROM subscribers WHERE status='unpaid'"
    )
    for row in cursor.fetchall():
        tree_unpaid.insert("", "end", values=row)

    # جلب المشتركين المسددين
    cursor.execute(
        "SELECT id, name, phone, amperes, amount FROM subscribers WHERE status='paid'"
    )
    for row in cursor.fetchall():
        tree_paid.insert("", "end", values=row)


def add_subscriber():
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    amperes = entry_amp.get().strip()
    amount = entry_amount.get().strip()

    if not name or not amperes or not amount:
        messagebox.showwarning(
            "تنبيه", "يرجى إدخال الاسم، عدد الأمبيرات، والمبلغ!"
        )
        return

    cursor.execute(
        "INSERT INTO subscribers (name, phone, amperes, amount, status) VALUES (?, ?, ?, ?, 'unpaid')",
        (name, phone, amperes, amount),
    )
    conn.commit()

    # مسح الحقول بعد الإضافة
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_amp.delete(0, tk.END)
    entry_amount.delete(0, tk.END)

    fetch_data()
    messagebox.showinfo("نجاح", "تمت إضافة المشترك بنجاح!")


def mark_as_paid():
    selected_item = tree_unpaid.selection()
    if not selected_item:
        messagebox.showwarning(
            "تنبيه", "اختر مشتركاً من جدول 'غير المسددين' أولاً!"
        )
        return

    item_data = tree_unpaid.item(selected_item)
    sub_id = item_data["values"][0]

    cursor.execute(
        "UPDATE subscribers SET status='paid' WHERE id=?", (sub_id,)
    )
    conn.commit()
    fetch_data()
    messagebox.showinfo("تم التسديد", "تم تحويل المشترك إلى قائمة المسددين!")


def mark_as_unpaid():
    selected_item = tree_paid.selection()
    if not selected_item:
        messagebox.showwarning(
            "تنبيه", "اختر مشتركاً من جدول 'المسددين' إلغاء تسديده!"
        )
        return

    item_data = tree_paid.item(selected_item)
    sub_id = item_data["values"][0]

    cursor.execute(
        "UPDATE subscribers SET status='unpaid' WHERE id=?", (sub_id,)
    )
    conn.commit()
    fetch_data()


def delete_subscriber():
    # البحث في الجدولين عن العناصر المحددة
    selected_unpaid = tree_unpaid.selection()
    selected_paid = tree_paid.selection()

    if selected_unpaid:
        sub_id = tree_unpaid.item(selected_unpaid)["values"][0]
    elif selected_paid:
        sub_id = tree_paid.item(selected_paid)["values"][0]
    else:
        messagebox.showwarning("تنبيه", "حدد المشترك المراد حذفه من أحد الجدولين!")
        return

    if messagebox.askyesno("تأكيد", "هل أنت تأكد من حذف هذا المشترك؟"):
        cursor.execute("DELETE FROM subscribers WHERE id=?", (sub_id,))
        conn.commit()
        fetch_data()


def reset_month():
    if messagebox.askyesno(
        "تأكيد الشهر الجديد",
        "هل تريد إعادة جميع المشتركين إلى قائمة غير المسددين لبداية شهر جديد؟",
    ):
        cursor.execute("UPDATE subscribers SET status='unpaid'")
        conn.commit()
        fetch_data()


# ----------------3. الواجهة الرسمية (GUI)----------------
root = tk.Tk()
root.title("نظام إدارة اشتراكات المولدة الأهلية")
root.geometry("950x650")
root.configure(bg="#f0f2f5")

# عنوان البرنامج
title_label = tk.Label(
    root,
    text="نظام إدارة وتسديد اشتراكات المولدة",
    font=("Arial", 18, "bold"),
    bg="#1e293b",
    fg="white",
    py=10,
)
title_label.pack(fill=tk.X)

# إطار إدخال البيانات
frame_inputs = tk.LabelFrame(
    root,
    text=" إضافة مشترك جديد ",
    font=("Arial", 11, "bold"),
    bg="#f0f2f5",
    padx=10,
    pady=10,
)
frame_inputs.pack(fill=tk.X, padx=15, pady=10)

tk.Label(
    frame_inputs, text="اسم المشترك:", font=("Arial", 10), bg="#f0f2f5"
).grid(row=0, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame_inputs, font=("Arial", 10))
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(
    frame_inputs, text="رقم الهاتف:", font=("Arial", 10), bg="#f0f2f5"
).grid(row=0, column=2, padx=5, pady=5)
entry_phone = tk.Entry(frame_inputs, font=("Arial", 10))
entry_phone.grid(row=0, column=3, padx=5, pady=5)

tk.Label(
    frame_inputs, text="الأمبيرية:", font=("Arial", 10), bg="#f0f2f5"
).grid(row=1, column=0, padx=5, pady=5)
entry_amp = tk.Entry(frame_inputs, font=("Arial", 10))
entry_amp.grid(row=1, column=1, padx=5, pady=5)

tk.Label(
    frame_inputs, text="المبلغ المطلوب:", font=("Arial", 10), bg="#f0f2f5"
).grid(row=1, column=2, padx=5, pady=5)
entry_amount = tk.Entry(frame_inputs, font=("Arial", 10))
entry_amount.grid(row=1, column=3, padx=5, pady=5)

btn_add = tk.Button(
    frame_inputs,
    text="إضافة المشترك",
    bg="#22c55e",
    fg="white",
    font=("Arial", 10, "bold"),
    command=add_subscriber,
)
btn_add.grid(row=0, column=4, rowspan=2, padx=15, sticky="nesw")

# إطار الجداول (قسمين)
frame_tables = tk.Frame(root, bg="#f0f2f5")
frame_tables.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

# جدول غير المسددين
frame_unpaid = tk.LabelFrame(
    frame_tables,
    text=" قائمة غير المسددين ",
    font=("Arial", 11, "bold"),
    fg="#dc2626",
    bg="#f0f2f5",
)
frame_unpaid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

cols = ("ID", "الاسم", "الهاتف", "الأمبيرات", "المبلغ")
tree_unpaid = ttk.Treeview(
    frame_unpaid, columns=cols, show="headings", height=15
)
for col in cols:
    tree_unpaid.heading(col, text=col)
    tree_unpaid.column(col, width=80, anchor="center")
tree_unpaid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

btn_pay = tk.Button(
    frame_unpaid,
    text="✔ تسديد المبلغ المحدد",
    bg="#16a34a",
    fg="white",
    font=("Arial", 11, "bold"),
    command=mark_as_paid,
)
btn_pay.pack(fill=tk.X, padx=5, pady=5)

# جدول المسددين
frame_paid = tk.LabelFrame(
    frame_tables,
    text=" قائمة المسددين ",
    font=("Arial", 11, "bold"),
    fg="#16a34a",
    bg="#f0f2f5",
)
frame_paid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

tree_paid = ttk.Treeview(frame_paid, columns=cols, show="headings", height=15)
for col in cols:
    tree_paid.heading(col, text=col)
    tree_paid.column(col, width=80, anchor="center")
tree_paid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

btn_unpay = tk.Button(
    frame_paid,
    text="↩ إلغاء التسديد (إعادة لغير المسددين)",
    bg="#ea580c",
    fg="white",
    font=("Arial", 10, "bold"),
    command=mark_as_unpaid,
)
btn_unpay.pack(fill=tk.X, padx=5, pady=5)

# إطار التحكم الأراضي (حذف / بداية شهر)
frame_bottom = tk.Frame(root, bg="#f0f2f5")
frame_bottom.pack(fill=tk.X, padx=15, pady=10)

btn_delete = tk.Button(
    frame_bottom,
    text="حذف المشترك المحدد",
    bg="#ef4444",
    fg="white",
    font=("Arial", 10, "bold"),
    command=delete_subscriber,
)
btn_delete.pack(side=tk.LEFT, padx=5)

btn_reset = tk.Button(
    frame_bottom,
    text="🔄 تصفير للشهر الجديد (تحويل الكل لغير مسددين)",
    bg="#0284c7",
    fg="white",
    font=("Arial", 10, "bold"),
    command=reset_month,
)
btn_reset.pack(side=tk.RIGHT, padx=5)

# تشغيل وتحديث البيانات
fetch_data()
root.mainloop()
