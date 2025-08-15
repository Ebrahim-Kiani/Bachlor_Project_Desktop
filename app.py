import os
import tkinter as tk
from tkinter import ttk, messagebox
import api_client
import config
import requests
from pathlib import Path
import shutil
import converter
import robot_sender

class RobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Operator")
        self.geometry("1000x600")

        self.orders_tree = ttk.Treeview(self, columns=("id","name","email","address","status"), show="headings")
        self.orders_tree.heading("id", text="Order ID")
        self.orders_tree.heading("name", text="Name")
        self.orders_tree.heading("email", text="Email")
        self.orders_tree.heading("address", text="Address")
        self.orders_tree.heading("status", text="Status")
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        self.orders_tree.bind("<Double-1>", self.show_order_details)

        self.details_tree = ttk.Treeview(self, columns=("id","image","price"), show="headings")
        self.details_tree.heading("id", text="Detail ID")
        self.details_tree.heading("image", text="Image URL")
        self.details_tree.heading("price", text="Price")
        self.details_tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=8)
        ttk.Button(btn_frame, text="Refresh Orders", command=self.load_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Send Selected Detail", command=self.send_selected_detail).pack(side=tk.LEFT, padx=5)

        self.load_orders()

    def load_orders(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        orders = api_client.get_orders()
        for o in orders:
            fullname = f"{o['full_name']}"
            self.orders_tree.insert("", "end", values=(o['id'], fullname, o['email'], o['address'], o['status']))

    def show_order_details(self, event):
        selected = self.orders_tree.selection()
        if not selected:
            return
        order_id = self.orders_tree.item(selected[0])['values'][0]
        for i in self.details_tree.get_children():
            self.details_tree.delete(i)
        details = api_client.get_order_details(order_id)
        for d in details:
            self.details_tree.insert("", "end", values=(d['id'], d['image_url'], d['final_price']))

    def send_selected_detail(self):
        selected = self.details_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a detail first")
            return

        detail_id, image_url, price = self.details_tree.item(selected[0])['values']

        os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
        local_path = os.path.join(config.DOWNLOAD_DIR, Path(image_url).name)

        # مرحله 1
        self.status_label.config(text="📥 در حال دانلود فایل ...")
        self.update_idletasks()

        r = requests.get(image_url, stream=True)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        # مرحله 2
        self.status_label.config(text="🚀 در حال ارسال به RoboExplorer ...")
        self.update_idletasks()

        robot_sender.send_with_gui(local_path)

        # مرحله 3
        self.status_label.config(text="✅ کار با موفقیت انجام شد!")
        self.update_idletasks()

        api_client.mark_detail_done(detail_id)
        messagebox.showinfo("Done", f"Detail {detail_id} sent to robot.")

    

if __name__ == "__main__":
    app = RobotApp()
    app.mainloop()
