from pywinauto import Application
import os
import time

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pywinauto")
class RoboExplorer:
    def __init__(self, exe_path=None):
        self.exe_path = exe_path or r"C:\Program Files\RoboExplorer\RoboExplorer.exe"

    def upload(self, mb4_file, user_name):
        """ارسال فایل mb4 به ربات از طریق RoboExplorer"""

        try:
            # اتصال به RoboExplorer در حال اجرا
            app = Application(backend="uia").connect(title_re="RoboExplorer")
            main_win = app.window(title_re="RoboExplorer")

            # پیدا کردن TreeView سمت چپ (Folders)
            tree = main_win.child_window(title="Folders", control_type="Tree")

            # پیدا کردن پوشه کاربر (مثلاً Ebrahim_kiani)
            node = tree.get_item(["files (D:)", "Bachlor_Project_Desktop", user_name])
            node.expand()
            node.select()

            # انتخاب فایل mb4 از لیست سمت راست
            file_name = os.path.basename(mb4_file)
            listview = main_win.child_window(control_type="List")
            file_item = listview.get_item(file_name)
            file_item.click_input(double=True)

            # شبیه‌سازی Drag & Drop به سمت Robot
            robot_node = tree.get_item(["Robot"])
            file_item.drag_mouse_input()
            robot_node.drop_mouse_input()

            time.sleep(1)
            print(f"[RoboExplorer] فایل {mb4_file} ارسال شد به Robot ✅")

        except Exception as e:
            print(f"[RoboExplorer] خطا در ارسال فایل: {e}")
