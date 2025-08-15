self.status_label = ttk.Label(self, text="Ready", font=("Arial", 12))
self.status_label.pack(pady=5)
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

        # ✅ اضافه کردن لیبل وضعیت
        self.status_label = ttk.Label(self, text="Ready", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.load_orders()

