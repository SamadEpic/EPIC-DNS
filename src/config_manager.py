import json
import os
import sys
from typing import List, Dict, Any, Optional

# مسیر فایل تنظیمات (با در نظر گرفتن PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SETTINGS_FILE = resource_path("settings.json")
DEFAULT_SETTINGS_CONTENT = {
  "default_dns_list": [
    {"name": "Google DNS", "primary": "8.8.8.8", "secondary": "8.8.4.4"},
    {"name": "Cloudflare DNS", "primary": "1.1.1.1", "secondary": "1.0.0.1"},
    {"name": "OpenDNS", "primary": "208.67.222.222", "secondary": "208.67.220.220"}
  ],
  "last_selected_dns_name": "Google DNS",
  "is_dns_on": False
}

class ConfigManager:
    def __init__(self):
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        if not os.path.exists(SETTINGS_FILE):
            # اگر فایل وجود نداشت، از محتوای پیش‌فرض استفاده کن و فایل را بساز
            self._save_settings(DEFAULT_SETTINGS_CONTENT)
            return DEFAULT_SETTINGS_CONTENT
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # اگر فایل خراب بود یا خطا داد، از پیش‌فرض استفاده کن و فایل را بازنویسی کن
            print(f"Error loading settings file or file is corrupted. Using default settings.")
            self._save_settings(DEFAULT_SETTINGS_CONTENT)
            return DEFAULT_SETTINGS_CONTENT

    def _save_settings(self, settings_data: Dict[str, Any]):
        try:
            # مطمئن شو پوشه وجود داره (اگر در حالت توسعه هستیم)
            settings_dir = os.path.dirname(SETTINGS_FILE)
            if settings_dir and not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
                
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_dns_list(self) -> List[Dict[str, str]]:
        return self.settings.get("default_dns_list", [])

    def get_dns_by_name(self, name: str) -> Optional[Dict[str, str]]:
        for dns in self.get_dns_list():
            if dns.get("name") == name:
                return dns
        return None

    def get_last_selected_dns_name(self) -> str:
        return self.settings.get("last_selected_dns_name", "Google DNS")

    def set_last_selected_dns_name(self, name: str):
        if name in [dns['name'] for dns in self.get_dns_list()]:
            self.settings["last_selected_dns_name"] = name
            self._save_settings(self.settings)
        else:
            print(f"Warning: DNS '{name}' not found in list. Not saving.")

    def get_initial_dns_state(self) -> bool:
        # در زمان اجرا، بهتره وضعیت فعلی سیستم رو چک کنیم، نه مقدار ذخیره شده
        # اما برای سادگی فعلا مقدار ذخیره شده رو برمی‌گردونیم
        # بعدا این قسمت رو با dns_manager.get_current_dns_status() جایگزین می‌کنیم
        return self.settings.get("is_dns_on", False)

    def set_dns_state(self, is_on: bool):
        self.settings["is_dns_on"] = is_on
        self._save_settings(self.settings)

# (برای تست):
if __name__ == "__main__":
    config = ConfigManager()
    
    print("DNS List:", config.get_dns_list())
    print("Last Selected DNS Name:", config.get_last_selected_dns_name())
    print("Initial DNS State (from settings):", config.get_initial_dns_state())
    
    # تغییر و ذخیره تنظیمات
    config.set_last_selected_dns_name("Cloudflare DNS")
    config.set_dns_state(True)
    
    print("\nAfter changes:")
    print("Last Selected DNS Name:", config.get_last_selected_dns_name())
    print("DNS State:", config.settings.get("is_dns_on"))

    # تست گرفتن DNS خاص
    cloudflare_dns = config.get_dns_by_name("Cloudflare DNS")
    if cloudflare_dns:
        print("\nCloudflare DNS Details:", cloudflare_dns)
    
    # اگر فایل settings.json وجود نداشت، باید خودش ساخته بشه
    # برای تست، فایل را موقتا حذف کنید و دوباره اجرا کنید
