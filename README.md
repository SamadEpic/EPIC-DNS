# EPIC-DNS


import sys, os, subprocess, ctypes
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QComboBox, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal,
    QUrl, QRect, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import QFont, QDesktopServices, QIcon

# ---------------- RESOURCE ----------------
def resource_path(r):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, r)
    return os.path.join(os.path.abspath("."), r)

ICON_PATH = resource_path("icon.ico")

# ---------------- DNS LIST ----------------
DNS_LIST = {
    "Electro 🇮🇷": ("78.157.42.101", "78.157.42.100"),
    "Bshekan 🇮🇷": ("185.51.200.2", "178.22.122.100"),
    "Bogzar 🇮🇷": ("185.55.226.26", "185.55.225.25"),
    "Radar 🇮🇷": ("10.202.10.10", "10.202.10.11"),
    "Shecan 🇮🇷": ("178.22.122.100", "185.51.200.2"),
    "403.online 🇮🇷": ("10.202.10.202", "10.202.10.102"),
    "shelter 🇮🇷": ("94.103.125.157", "94.103.125.158"),
    "open DNS 🇺🇸": ("208.67.222.222", "208.67.220.220"),
    "Level3 🇩🇪": ("4.2.2.1", "4.2.2.2"),
    "CleanBrowsing 🇩🇪": ("185.228.168.10", "185.228.169.11"),
    "Cloudflare 🇺🇸": ("1.1.1.1", "1.0.0.1"),
    "Google 🇺🇸": ("8.8.8.8", "8.8.4.4"),
    "Quad9 🇩🇪": ("9.9.9.9", "149.112.112.112"),
}

# ---------------- ADMIN ----------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        " ".join(sys.argv), None, 1
    )
    sys.exit()

# ---------------- DNS CORE ----------------
def get_adapter():
    out = subprocess.check_output(
        ["netsh", "interface", "show", "interface"],
        text=True, creationflags=0x08000000
    )
    for l in out.splitlines():
        if "Connected" in l:
            return " ".join(l.split()[3:])
    return None

def set_dns(adapter, d1, d2):
    subprocess.run(
        ["netsh", "interface", "ip", "set", "dns", f'name={adapter}', "static", d1],
        creationflags=0x08000000
    )
    subprocess.run(
        ["netsh", "interface", "ip", "add", "dns", f'name={adapter}', d2, "index=2"],
        creationflags=0x08000000
    )

def reset_dns(adapter):
    subprocess.run(
        ["netsh", "interface", "ip", "set", "dns", f'name={adapter}', "dhcp"],
        creationflags=0x08000000
    )

# ---------------- DNS THREAD ----------------
class DnsWorker(QThread):
    finished_ok = Signal(bool)

    def __init__(self, enable, dns=None):
        super().__init__()
        self.enable = enable
        self.dns = dns

    def run(self):
        try:
            adapter = get_adapter()
            if not adapter:
                self.finished_ok.emit(False)
                return

            if self.enable:
                set_dns(adapter, self.dns[0], self.dns[1])
            else:
                reset_dns(adapter)

            self.finished_ok.emit(True)
        except:
            self.finished_ok.emit(False)

# ---------------- HOVER BUTTON ----------------
class HoverButton(QPushButton):
    def __init__(self, text, url, parent):
        super().__init__(text, parent)
        self.url = url
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(114,137,218,0.25);
                color: white;
                border-radius:6px;
            }
        """)
        self.base_geom = None

    def enterEvent(self, e):
        if not self.base_geom:
            self.base_geom = self.geometry()
        a = QPropertyAnimation(self, b"geometry")
        a.setDuration(120)
        a.setEasingCurve(QEasingCurve.OutQuad)
        a.setStartValue(self.base_geom)
        a.setEndValue(QRect(
            self.base_geom.x()-2,
            self.base_geom.y()-2,
            self.base_geom.width()+4,
            self.base_geom.height()+4
        ))
        a.start()
        self.anim = a

    def leaveEvent(self, e):
        if not self.base_geom:
            return
        a = QPropertyAnimation(self, b"geometry")
        a.setDuration(120)
        a.setEasingCurve(QEasingCurve.OutQuad)
        a.setStartValue(self.geometry())
        a.setEndValue(self.base_geom)
        a.start()
        self.anim = a

    def mousePressEvent(self, e):
        QDesktopServices.openUrl(QUrl(self.url))

# ---------------- UI ----------------
class EpicDNS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPIC DNS")
        self.setFixedSize(360, 460)
        self.setStyleSheet("background:#0e0e11;")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.is_on = False
        self.worker = None

        self.build_ui()
        self.init_tray()

    def build_ui(self):
        lbl = QLabel("EPIC DNS", self)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl.setGeometry(0, 20, 360, 40)

        self.power = QPushButton("⏻", self)
        self.power.setFixedSize(130,130)
        self.power.move(115,70)
        self.power.setCursor(Qt.PointingHandCursor)
        self.power.setStyleSheet(self.off_style())
        self.power.clicked.connect(self.toggle)

        self.combo = QComboBox(self)
        self.combo.addItems(DNS_LIST.keys())
        self.combo.setFixedWidth(180)
        self.combo.move(90,220)
        self.combo.setStyleSheet("""
            QComboBox {
                background:#1c1c22;
                color:white;
                padding:6px;
                border-radius:6px;
            }
        """)

        ads = [
            ("Discord","https://discord.gg/Tx6npqQR"),
            ("Donate","https://reymit.ir/samadepic"),
            ("GitHub","https://github.com/SamadEpic")
        ]
        x = 40
        for t,u in ads:
            b = HoverButton(t, u, self)
            b.setFixedSize(90,30)
            b.move(x,410)
            x += 100

    # ---------------- POWER ----------------
    def toggle(self):
        self.power.setEnabled(False)

        if not self.is_on:
            self.power.setStyleSheet(self.on_style())
            dns = DNS_LIST[self.combo.currentText()]
            self.worker = DnsWorker(True, dns)
        else:
            self.power.setStyleSheet(self.off_style())
            self.worker = DnsWorker(False)

        self.worker.finished_ok.connect(self.on_worker_done)
        self.worker.start()

        QTimer.singleShot(3000, lambda: self.power.setEnabled(True))

    def on_worker_done(self, ok):
        if ok:
            self.is_on = not self.is_on
        self.worker.quit()
        self.worker.wait()
        self.worker = None

    def on_style(self):
        return "QPushButton{background:#1db954;border-radius:65px;color:white;font-size:38px;}"

    def off_style(self):
        return "QPushButton{background:#b3261e;border-radius:65px;color:white;font-size:38px;}"

    # ---------------- TRAY ----------------
    def init_tray(self):
        self.tray = QSystemTrayIcon(QIcon(ICON_PATH), self)
        menu = QMenu()
        menu.addAction("Show", self.show)
        menu.addAction("Exit", self.exit_app)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def closeEvent(self, e):
        e.ignore()
        self.hide()

    def exit_app(self):
        if self.is_on:
            reset_dns(get_adapter())
        QApplication.quit()

# ---------------- RUN ----------------
if __name__ == "__main__":
    if not is_admin():
        relaunch_admin()

    app = QApplication(sys.argv)
    w = EpicDNS()
    w.show()
    sys.exit(app.exec())
