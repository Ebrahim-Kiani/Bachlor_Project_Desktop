import os
import tkinter as tk
from tkinter import ttk, messagebox
import api_client
import config
import requests
from pathlib import Path
import shutil
import robot_sender

import converter
import config



class RobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Operator")
        self.geometry("1000x600")

        # جدول سفارش‌ها
        self.orders_tree = ttk.Treeview(self, columns=("id", "name", "email", "address", "status"), show="headings")
        for col, text in [("id", "Order ID"), ("name", "Name"), ("email", "Email"),
                          ("address", "Address"), ("status", "Status")]:
            self.orders_tree.heading(col, text=text)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        self.orders_tree.bind("<Double-1>", self.show_order_details)

        # جدول جزئیات
        self.details_tree = ttk.Treeview(self, columns=("id", "image", "price"), show="headings")
        for col, text in [("id", "Detail ID"), ("image", "Image URL"), ("price", "Price")]:
            self.details_tree.heading(col, text=text)
        self.details_tree.pack(fill=tk.BOTH, expand=True)

        # نوار دکمه‌ها
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=8)
        ttk.Button(btn_frame, text="Refresh Orders", command=self.load_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Send Selected Detail", command=self.send_selected_detail).pack(side=tk.LEFT, padx=5)

        # نمایش وضعیت
        self.status_label = ttk.Label(self, text="✅ آماده", anchor="w")
        self.status_label.pack(fill=tk.X, padx=5, pady=5)

        # بارگذاری اولیه سفارش‌ها
        try:
            self.load_orders()
        except Exception as e:
            print("Error loading orders:", e)
            self.status_label.config(text="❌ خطا در بارگذاری سفارش‌ها")

    def load_orders(self):
        self.status_label.config(text="🔄 در حال بارگذاری سفارش‌ها ...")
        self.update_idletasks()

        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        orders = api_client.get_orders()
        for o in orders:
            fullname = f"{o['full_name']}"
            self.orders_tree.insert("", "end",
                                    values=(o['id'], fullname, o['email'], o['address'], o['status']))
        self.status_label.config(text="✅ سفارش‌ها بارگذاری شدند")

    def show_order_details(self, event):
        selected = self.orders_tree.selection()
        if not selected:
            return
        order_id = self.orders_tree.item(selected[0])['values'][0]
        for i in self.details_tree.get_children():
            self.details_tree.delete(i)
        details = api_client.get_order_details(order_id)
        for d in details:
            self.details_tree.insert(
                "",
                "end",
                values=(d['id'], d['vector_svg'], d['final_price'], d['image_url'])
            )

    def send_selected_detail(self):
        selected = self.details_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a detail first")
            return

        detail_id, svg_url, price, png_url = self.details_tree.item(selected[0])['values']

        os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

        # 1️⃣ دانلود فایل SVG
        svg_path = os.path.join(config.DOWNLOAD_DIR, Path(svg_url).name)
        self.status_label.config(text="⬇️ در حال دانلود فایل SVG ...")
        self.update_idletasks()
        try:
            r = requests.get(svg_url, stream=True)
            r.raise_for_status()
            with open(svg_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        except Exception as e:
            messagebox.showerror("Error", f"خطا در دانلود فایل: {e}")
            self.status_label.config(text="❌ خطا در دانلود SVG")
            return

        # 2️⃣ تبدیل SVG به MB4
        self.status_label.config(text="⚙️ در حال تبدیل به MB4 ...")
        self.update_idletasks()
        try:
            mb4_path = converter.convert_svg_to_mb4(svg_path, config.OUTPUT_DIR)
        except Exception as e:
            messagebox.showerror("Error", f"خطا در تبدیل به MB4: {e}")
            self.status_label.config(text="❌ خطا در تبدیل MB4")
            return

        # 3️⃣ ارسال فایل MB4 به ربات
        self.status_label.config(text="📤 در حال ارسال به ربات ...")
        self.update_idletasks()
        try:
            robot_sender.send_with_gui(mb4_path)
        except Exception as e:
            messagebox.showerror("Error", f"خطا در ارسال به ربات: {e}")
            self.status_label.config(text="❌ خطا در ارسال به ربات")
            return

        # 4️⃣ ثبت جزئیات به عنوان انجام‌شده در سرور
        self.status_label.config(text="📝 در حال ثبت وضعیت سفارش ...")
        self.update_idletasks()
        try:
            api_client.mark_detail_done(detail_id)
        except Exception as e:
            messagebox.showerror("Error", f"خطا در ثبت وضعیت: {e}")
            self.status_label.config(text="❌ خطا در ثبت وضعیت")
            return

        # ✅ پایان
        self.status_label.config(text="✅ ارسال با موفقیت انجام شد")
        messagebox.showinfo("Done", f"Detail {detail_id} sent to robot.")




if __name__ == "__main__":
    app = RobotApp()
    app.mainloop()
