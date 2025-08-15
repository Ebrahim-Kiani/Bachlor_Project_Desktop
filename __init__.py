import tkinter as tk

class RobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Operator")
        self.geometry("1000x600")

        # لیبل وضعیت
        self.status_label = ttk.Label(self, text="✅ آماده")
        self.status_label.pack(fill=tk.X, pady=5)

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

    def send_selected_detail(self):
        selected = self.details_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a detail first")
            return

        detail_id, image_url, price = self.details_tree.item(selected[0])['values']

        # مرحله 1: دانلود فایل SVG
        self.status_label.config(text="📥 در حال دانلود فایل ...")
        self.update_idletasks()

        os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
        local_path = os.path.join(config.DOWNLOAD_DIR, Path(image_url).name)

        r = requests.get(image_url, stream=True)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        # مرحله 2: ارسال به RoboExplorer
        self.status_label.config(text="📤 در حال ارسال به RoboExplorer ...")
        self.update_idletasks()

        robot_sender.send_with_gui(local_path)

        # مرحله 3: علامت‌گذاری به عنوان انجام شده
        self.status_label.config(text="✅ ثبت به عنوان انجام شده")
        self.update_idletasks()

        api_client.mark_detail_done(detail_id)

        # مرحله پایانی
        messagebox.showinfo("Done", f"Detail {detail_id} sent to robot.")
        self.status_label.config(text="✅ آماده")
