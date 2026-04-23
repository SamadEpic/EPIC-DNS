import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication

# تابع resource_path برای پیدا کردن مسیر فایل‌ها (همانند main_window.py)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent # ارجاع به پنجره اصلی (MainWindow)

        # تنظیم آیکون سینی سیستم
        # فرض می‌کنیم tray_icon.png در پوشه assets هست
        try:
            self.setIcon(QIcon(resource_path('assets/tray_icon.png')))
        except FileNotFoundError:
            print("Warning: tray_icon.png not found. Using default system tray icon.")
            # اگر آیکون پیدا نشد، از آیکون پیش‌فرض سیستم استفاده می‌شود

        # ساخت منوی کلیک راست
        self.menu = QMenu()
        self.setContextMenu(self.menu)

        # اضافه کردن آیتم‌ها به منو
        self.show_window_action = QAction("نمایش پنجره", self)
        self.show_window_action.triggered.connect(self.show_main_window)
        self.menu.addAction(self.show_window_action)

        self.quit_action = QAction("خروج", self)
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)

        # نمایش آیکون سینی سیستم
        self.show()

    def show_main_window(self):
        """ تابع برای نمایش پنجره اصلی برنامه """
        if self.parent:
            # اگر پنجره مخفی بود، آن را نمایش بده
            self.parent.show()
            # اگر پنجره minimize شده بود، آن را restore کن
            self.parent.setWindowState(self.parent.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            # پنجره را به foreground بیاور
            self.parent.activateWindow()
        else:
            print("Error: Parent window (MainWindow) is not set.")

    def quit_app(self):
        """ تابع برای خروج از برنامه """
        self.setVisible(False) # مخفی کردن آیکون سینی سیستم قبل از خروج
        QCoreApplication.quit() # بستن برنامه

# کد زیر برای تست این کلاس به تنهایی استفاده می‌شود
if __name__ == '__main__':
    # برای تست، نیاز به یک QApplication داریم
    app = QApplication(sys.argv)

    # در حالت تست، ما پنجره اصلی نداریم، پس tray_icon رو بدون parent می‌سازیم
    # و آیتم "نمایش پنجره" کاری انجام نمی‌ده
    tray_icon = SystemTrayIcon()

    # اگر می‌خواستیم تست کنیم که کلیک روی آیکون سینی برنامه رو ببنده
    # tray_icon.quit_action.triggered.connect(app.quit)

    # برای اینکه برنامه در حالت تست اجرا بمونه تا زمانی که از سینی سیستم خارج بشیم
    sys.exit(app.exec_())
