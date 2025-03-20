import os
import sys
import time
import random
import string
import shutil
import subprocess
import getpass
from termcolor import colored
import platform
import zipfile
import requests
import json

# إعدادات الأداة
VERSION = "1.0"
AUTHOR = "㉿ AbuAlqasm"
GITHUB_URL = "https://github.com/AbuAlqasm/AbuRoot"
TERMUX_HOME = os.path.expanduser("~")
TEMP_DIR = os.path.join(TERMUX_HOME, "aburoot_temp")
ROOT_ENV_DIR = os.path.join(TERMUX_HOME, "aburoot_env")
CONFIG_FILE = os.path.join(TERMUX_HOME, ".aburoot_config")
MAGISK_URL = "https://github.com/topjohnwu/Magisk/releases/download/v27.0/Magisk-v27.0.apk"



# شعار الأداة
def print_banner():
    banner = """
     █████╗ ██████╗ ██╗   ██╗██████╗  ██████╗  ██████╗ ████████╗
    ██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝
    ███████║██████╔╝██║   ██║██████╔╝██║   ██║██║   ██║   ██║   
    ██╔══██║██╔══██╗██║   ██║██╔══██╗██║   ██║██║   ██║   ██║   
    ██║  ██║██║  ██║╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝   ██║   
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   
    """
    print(colored(banner, "green"))
    print(colored(f"         by {AUTHOR}  |  v.{VERSION}", "yellow"))
    print(colored(f"         {GITHUB_URL}", "cyan"))
    print(colored("----------------------------------------------------", "green"))

# تثبيت المتطلبات
def install_requirements():
    print(colored("[INFO] Installing requirements...", "blue"))
    os.system("pkg update -y && pkg upgrade -y")
    os.system("pkg install python termcolor git -y")
    os.system("pip install termcolor requests")

# إعداد بيئة المحاكاة
def setup_root_env():
    if not os.path.exists(ROOT_ENV_DIR):
        os.makedirs(ROOT_ENV_DIR)
        print(colored("[INFO] Creating root environment...", "blue"))
        
        # محاكاة مجلدات النظام
        os.makedirs(os.path.join(ROOT_ENV_DIR, "system/bin"), exist_ok=True)
        os.makedirs(os.path.join(ROOT_ENV_DIR, "system/etc"), exist_ok=True)
        os.makedirs(os.path.join(ROOT_ENV_DIR, "data"), exist_ok=True)
        
        # إنشاء ملفات وهمية
        with open(os.path.join(ROOT_ENV_DIR, "system/bin/su"), "w") as f:
            f.write("#!/data/data/com.termux/files/usr/bin/sh\necho 'Root access granted (simulated)'\n")
        os.chmod(os.path.join(ROOT_ENV_DIR, "system/bin/su"), 0o755)
        
        with open(os.path.join(ROOT_ENV_DIR, "system/etc/passwd"), "w") as f:
            f.write("root:x:0:0:root:/root:/bin/sh\n")
        
        print(colored("[INFO] Root environment setup completed!", "green"))
    else:
        print(colored("[INFO] Root environment already exists.", "yellow"))

# تحميل وتثبيت Magisk (Root حقيقي)
def install_magisk():
    magisk_apk = os.path.join(TEMP_DIR, "Magisk-v27.0.apk")
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    print(colored("[INFO] Downloading Magisk...", "blue"))
    response = requests.get(MAGISK_URL, stream=True)
    with open(magisk_apk, "wb") as f:
        f.write(response.content)
    
    print(colored("[INFO] Magisk downloaded. Install it manually via Termux.", "yellow"))
    print(colored("[WARNING] You need an unlocked bootloader and custom recovery (e.g., TWRP) to flash Magisk!", "red"))
    os.system(f"termux-open {magisk_apk}")

# فحص حالة الروت
def check_root_status():
    if os.path.exists("/system/bin/su") or os.path.exists("/sbin/su"):
        return True
    return False

# محاكاة أوامر Root
def simulate_root_command(command):
    if command.startswith("sudo"):
        cmd = command.replace("sudo", "").strip()
        if cmd == "whoami":
            return "root"
        elif cmd.startswith("chmod"):
            return f"[SIMULATED] {cmd} executed"
        elif cmd.startswith("chown"):
            return f"[SIMULATED] {cmd} executed"
        elif cmd == "reboot":
            return "[SIMULATED] Rebooting device..."
        else:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout or result.stderr
            except:
                return f"[SIMULATED] Executed: {cmd}"
    else:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout or result.stderr
        except:
            return f"[ERROR] Failed to execute: {command}"

# إعداد وحفظ بيانات تسجيل الدخول
def setup_credentials():
    if not os.path.exists(CONFIG_FILE):
        print(colored("[SETUP] Set up your custom credentials", "cyan"))
        username = input(colored("Enter your username: ", "yellow"))
        password = getpass.getpass(colored("Enter your password: ", "yellow"))
        
        config = {"username": username, "password": password}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        print(colored("[SUCCESS] Credentials saved!", "green"))
        return username, password
    else:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config["username"], config["password"]

# واجهة تسجيل الدخول
def login_screen():
    saved_username, saved_password = setup_credentials()
    print(colored("[LOGIN] Please enter your credentials", "cyan"))
    username = input(colored("Username: ", "yellow"))
    password = getpass.getpass(colored("Password: ", "yellow"))
    
    if username == saved_username and password == saved_password:
        print(colored("[SUCCESS] Login successful!", "green"))
        return username, password
    else:
        print(colored("[ERROR] Invalid credentials!", "red"))
        return None, None

# موجه الأوامر المخصص
def custom_prompt(username, password):
    current_dir = TERMUX_HOME
    while True:
        prompt = colored(f"┌──({username}㉿{password})-[~/{os.path.basename(current_dir)}]\n└─$ ", "green")
        command = input(prompt)
        
        if command == "exit":
            print(colored("[INFO] Exiting AbuRoot...", "yellow"))
            break
        elif command == "clear":
            os.system("clear")
            print_banner()
        elif command == "install_magisk":
            install_magisk()
        elif command == "check_root":
            if check_root_status():
                print(colored("[INFO] Device is rooted!", "green"))
            else:
                print(colored("[INFO] Device is not rooted. Using simulated root.", "yellow"))
        elif command.startswith("cd "):
            new_dir = command.split(" ")[1]
            if new_dir.startswith("/"):
                target_dir = new_dir
            else:
                target_dir = os.path.join(current_dir, new_dir)
            if os.path.exists(target_dir):
                current_dir = os.path.abspath(target_dir)
            else:
                print(colored(f"[ERROR] Directory not found: {target_dir}", "red"))
        elif command:
            result = simulate_root_command(command)
            print(colored(result, "white"))

# التحقق من التحديثات
def check_updates():
    print(colored("[INFO] Checking for updates...", "blue"))
    try:
        response = requests.get(f"{GITHUB_URL}/releases/latest")
        latest_version = re.search(r"tag/v(\d+\.\d+)", response.text).group(1)
        if latest_version > VERSION:
            print(colored(f"[UPDATE] New version {latest_version} available! Visit {GITHUB_URL}", "yellow"))
        else:
            print(colored("[INFO] You are using the latest version.", "green"))
    except:
        print(colored("[ERROR] Failed to check updates.", "red"))

# إعداد الأداة للنشر على GitHub
def prepare_for_github():
    print(colored("[INFO] Preparing for GitHub release...", "blue"))
    repo_dir = os.path.join(TERMUX_HOME, "AbuRoot")
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
    
    # إنشاء ملفات GitHub
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write(f"""
# AbuRoot
A powerful root tool for Termux by {AUTHOR}

## Features
- Simulated Root environment for non-rooted devices
- Real Root installation with Magisk (requires unlocked bootloader)
- Custom command prompt with sudo support
- GitHub-ready structure

## Installation
1. `git clone {GITHUB_URL}`
2. `cd AbuRoot`
3. `python aburoot.py`

## Usage
- Set up your custom username and password on first run
- Use commands like `sudo`, `check_root`, `install_magisk`

## Version
{VERSION}
        """)
    
    with open(os.path.join(repo_dir, "LICENSE"), "w") as f:
        f.write("MIT License\nCopyright (c) 2025 AbuAlqasm")
    
    shutil.copy(__file__, os.path.join(repo_dir, "aburoot.py"))
    print(colored(f"[INFO] Repository prepared at {repo_dir}. Push to GitHub!", "green"))

# التشغيل الرئيسي
def main():
    os.system("clear")
    print_banner()
    install_requirements()
    setup_root_env()
    check_updates()
    
    username, password = login_screen()
    if username and password:
        prepare_for_github()
        custom_prompt(username, password)
    else:
        print(colored("[INFO] Login failed. Exiting...", "red"))
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n[INFO] Interrupted by user. Exiting...", "yellow"))
        sys.exit(0)
