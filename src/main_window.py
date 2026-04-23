import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QFileDialog, QCheckBox, QComboBox,
    QMessageBox, QTabWidget, QFormLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# فرض می‌کنیم تابع resource_path برای پیدا کردن مسیر فایل‌ها وجود داره
# این تابع باید در فایل جداگانه‌ای مثل utils.py یا در همین فایل تعریف بشه
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EpicDNS Configurator")
        # اینجا آیکون برنامه رو تنظیم می‌کنیم. فرض می‌کنیم فایل app_icon.png در پوشه assets هست
        # اگه آیکون ندارید یا نمی‌خواید فعلا تنظیم کنید، این خط رو کامنت کنید
        try:
            self.setWindowIcon(QIcon(resource_path('assets/app_icon.png')))
        except FileNotFoundError:
            print("Warning: app_icon.png not found. Using default icon.")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.settings_data = {}
        self.settings_widgets = {} # Dictionary to hold created widgets for settings
        self.load_settings()
        self.create_settings_tab()

        # دکمه ذخیره
        self.save_button = QPushButton("ذخیره تنظیمات")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

    def resource_path(self, relative_path):
        """ Helper function to get resource path """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_settings(self):
        settings_file_path = self.resource_path('settings.json')
        if os.path.exists(settings_file_path):
            try:
                with open(settings_file_path, 'r', encoding='utf-8') as f:
                    self.settings_data = json.load(f)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "خطا در خواندن فایل", "فایل settings.json خراب است یا فرمت نادرستی دارد.")
                self.settings_data = {}
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"خطای غیرمنتظره هنگام خواندن تنظیمات: {e}")
                self.settings_data = {}
        else:
            QMessageBox.warning(self, "فایل تنظیمات یافت نشد", "فایل settings.json در مسیر مورد انتظار یافت نشد. تنظیمات خالی بارگذاری می‌شود.")
            self.settings_data = {}

    def create_settings_tab(self):
        # تب اصلی تنظیمات
        settings_tab = QWidget()
        self.tabs.addTab(settings_tab, "تنظیمات اصلی")

        form_layout = QFormLayout(settings_tab)
        self.settings_widgets = {} # Reset widgets for this tab

        # مثال: اضافه کردن فیلدهای تنظیمات بر اساس ساختار settings.json
        # این بخش باید با توجه به ساختار واقعی settings.json شما سفارشی‌سازی شود

        # اگر تنظیمات dns_server و backup_dns وجود دارند
        if 'dns_settings' in self.settings_data:
            dns_settings_group = self.settings_data['dns_settings']

            primary_dns_label = QLabel("DNS اصلی:")
            primary_dns_input = QLineEdit(dns_settings_group.get('primary_dns', ''))
            primary_dns_input.setPlaceholderText("مثال: 1.1.1.1")
            form_layout.addRow(primary_dns_label, primary_dns_input)
            self.settings_widgets['primary_dns'] = primary_dns_input

            backup_dns_label = QLabel("DNS پشتیبان:")
            backup_dns_input = QLineEdit(dns_settings_group.get('backup_dns', ''))
            backup_dns_input.setPlaceholderText("مثال: 8.8.8.8")
            form_layout.addRow(backup_dns_label, backup_dns_input)
            self.settings_widgets['backup_dns'] = backup_dns_input

            # مثال: اضافه کردن یک CheckBox
            enable_auto_switch_label = QLabel("فعال کردن جابجایی خودکار DNS:")
            enable_auto_switch_checkbox = QCheckBox()
            enable_auto_switch_checkbox.setChecked(dns_settings_group.get('enable_auto_switch', False))
            form_layout.addRow(enable_auto_switch_label, enable_auto_switch_checkbox)
            self.settings_widgets['enable_auto_switch'] = enable_auto_switch_checkbox

        # مثال: اضافه کردن فیلد برای مسیر فایل لاگ
        if 'log_file_path' in self.settings_data:
            log_path_label = QLabel("مسیر فایل لاگ:")
            log_path_input = QLineEdit(self.settings_data.get('log_file_path', ''))
            log_path_input.setReadOnly(True) # مسیر را نمی‌توان مستقیماً ویرایش کرد، با دکمه انتخاب می‌شود
            browse_button = QPushButton("انتخاب مسیر")
            browse_button.clicked.connect(lambda: self.browse_for_file(log_path_input, "انتخاب فایل لاگ", "Log Files (*.log);;All Files (*)"))
            
            log_path_layout = QVBoxLayout()
            log_path_layout.addWidget(log_path_input)
            log_path_layout.addWidget(browse_button)
            
            # برای نمایش افقی لیبل و فیلد، از هورایزنتال‌لی‌اوت استفاده می‌کنیم
            # اما اینجا چون می‌خوایم دکمه زیر لیبل باشه، از layout مجزا استفاده می‌کنیم
            # این قسمت نیاز به تنظیمات بیشتری داره تا دقیقا مثل بقیه ردیف‌ها بشه
            # فعلا اینطوری نمایش داده میشه
            form_layout.addRow(log_path_label, log_path_input) # لیبل اضافه شد
            form_layout.addRow("", browse_button) # دکمه در ردیف بعدی
            self.settings_widgets['log_file_path'] = log_path_input


        # اضافه کردن تب‌های بیشتر در صورت نیاز
        # self.create_another_tab()

    def browse_for_file(self, line_edit_widget, title, file_filter):
        """ Opens a file dialog to select a file and updates the line edit """
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # uncomment for testing with non-native dialog
        file_path, _ = QFileDialog.getOpenFileName(self, title, "", file_filter, options=options)
        if file_path:
            line_edit_widget.setText(file_path)

    def save_settings(self):
        # این تابع باید تنظیمات فعلی از ویجت‌ها رو بخونه و در self.settings_data ذخیره کنه
        # سپس self.settings_data رو در فایل settings.json ذخیره کنه

        # بروزرسانی DNS settings
        if 'dns_settings' in self.settings_data:
            dns_group = self.settings_data.get('dns_settings', {})
            if 'primary_dns' in self.settings_widgets:
                dns_group['primary_dns'] = self.settings_widgets['primary_dns'].text()
            if 'backup_dns' in self.settings_widgets:
                dns_group['backup_dns'] = self.settings_widgets['backup_dns'].text()
            if 'enable_auto_switch' in self.settings_widgets:
                dns_group['enable_auto_switch'] = self.settings_widgets['enable_auto_switch'].isChecked()
            self.settings_data['dns_settings'] = dns_group

        # بروزرسانی مسیر لاگ
        if 'log_file_path' in self.settings_widgets:
            self.settings_data['log_file_path'] = self.settings_widgets['log_file_path'].text()

        # ذخیره در فایل JSON
        settings_file_path = self.resource_path('settings.json')
        try:
            with open(settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "ذخیره موفق", "تنظیمات با موفقیت ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطای ذخیره", f"خطا در ذخیره تنظیمات: {e}")

    # اگر نیاز به تب‌های بیشتری داشتی، می‌تونی این تابع رو اضافه کنی
    # def create_another_tab(self):
    #     another_tab_widget = QWidget()
    #     layout = QVBoxLayout(another_tab_widget)
    #     label = QLabel("محتوای تب دوم")
    #     layout.addWidget(label)
    #     self.tabs.addTab(another_tab_widget, "تب دوم")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # اینجا می‌توانید آیکون برنامه را تنظیم کنید.
    # app.setWindowIcon(QIcon(resource_path('assets/app_icon.png')))
    
    # اگر می‌خواهید برنامه از تنظیمات موجود استفاده کند، باید مطمئن شوید
    # که فایل settings.json در مسیر درست قرار دارد یا تابع resource_path آن را پیدا می‌کند.
    # اگر فایل وجود ندارد، برنامه با تنظیمات پیش‌فرض یا خالی شروع می‌شود.

    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
