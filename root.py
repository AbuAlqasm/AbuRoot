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
import requests
import json
import re

# إعدادات الأداة
VERSION = "1.0"
AUTHOR = "㉿ AbuAlqasm"
GITHUB_URL = "https://github.com/AbuAlqasm/AbuRoot"
TERMUX_HOME = os.path.expanduser("~")
TEMP_DIR = os.path.join(TERMUX_HOME, "aburoot_temp")
CONFIG_FILE = os.path.join(TERMUX_HOME, ".aburoot_config")
MAGISK_URL = "https://github.com/topjohnwu/Magisk/releases/download/v27.0/Magisk-v27.0.apk"
BUSYBOX_URL = "https://github.com/Magisk-Modules-Repo/busybox-ndk/releases/download/v1.34.1/busybox-arm64"

# تحقق من Termux
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
    os.system("pkg install python termcolor git wget curl unzip -y")
    os.system("pip install requests termcolor")

# تحميل وتثبيت Magisk
def install_magisk():
    magisk_apk = os.path.join(TEMP_DIR, "Magisk-v27.0.apk")
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    print(colored("[INFO] Downloading Magisk...", "blue"))
    response = requests.get(MAGISK_URL, stream=True)
    with open(magisk_apk, "wb") as f:
        f.write(response.content)
    
    print(colored("[INFO] Magisk downloaded.", "yellow"))
    print(colored("[WARNING] You need an unlocked bootloader and custom recovery (e.g., TWRP) to flash Magisk!", "red"))
    print(colored("[INFO] Steps: 1. Install Magisk app, 2. Flash via recovery.", "yellow"))
    os.system(f"termux-open {magisk_apk}")

# تثبيت BusyBox
def install_busybox():
    busybox_bin = os.path.join(TEMP_DIR, "busybox-arm64")
    busybox_dir = os.path.join(TERMUX_HOME, "busybox")
    
    if not os.path.exists(busybox_dir):
        os.makedirs(busybox_dir)
    
    print(colored("[INFO] Downloading BusyBox...", "blue"))
    response = requests.get(BUSYBOX_URL, stream=True)
    with open(busybox_bin, "wb") as f:
        f.write(response.content)
    
    os.chmod(busybox_bin, 0o755)
    shutil.move(busybox_bin, os.path.join(busybox_dir, "busybox"))
    print(colored("[INFO] BusyBox installed.", "green"))

# فحص حالة الروت
def check_root_status():
    try:
        result = subprocess.run("su -c whoami", shell=True, capture_output=True, text=True, timeout=5)
        if result.stdout.strip() == "root":
            return True
    except:
        pass
    return False

# تنفيذ أوامر بصلاحيات Root
def execute_root_command(command):
    if check_root_status():
        try:
            result = subprocess.run(f"su -c '{command}'", shell=True, capture_output=True, text=True)
            return result.stdout or result.stderr
        except Exception as e:
            return f"[ERROR] Failed to execute: {str(e)}"
    else:
        print(colored("[ERROR] Root access not available! Install Root first.", "red"))
        return ""

# تنفيذ أوامر Termux العادية
def execute_normal_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
        return f"[ERROR] Failed to execute: {str(e)}"

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
        # عرض تفاصيل المسار والحالة
        root_status = "root" if check_root_status() else "non-root"
        prompt = colored(f"┌──({username}㉿{password})-[{root_status}][{current_dir}]\n└─$ ", "green")
        command = input(prompt)
        
        if command == "exit":
            print(colored("[INFO] Exiting AbuRoot...", "yellow"))
            break
        elif command == "clear":
            os.system("clear")
            print_banner()
        elif command == "install_root":
            install_magisk()
        elif command == "install_busybox":
            install_busybox()
        elif command == "check_root":
            if check_root_status():
                print(colored("[INFO] Device is rooted!", "green"))
            else:
                print(colored("[INFO] Device is not rooted.", "yellow"))
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
        elif command.startswith("sudo "):
            result = execute_root_command(command.replace("sudo ", "").strip())
            print(colored(result, "white"))
        elif command:
            result = execute_normal_command(command)
            print(colored(result, "white"))

# التحقق من التحديثات
def check_updates():
    print(colored("[INFO] Checking for updates...", "blue"))
    try:
        response = requests.get(f"{GITHUB_URL}/releases/latest")
        latest_version = re.search(r"tag/v(\d+\.\d+)", response.text)
        if latest_version and latest_version.group(1) > VERSION:
            print(colored(f"[UPDATE] New version {latest_version.group(1)} available! Visit {GITHUB_URL}", "yellow"))
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
- Install real root with Magisk
- Run Termux commands with root privileges
- Custom command prompt with path navigation
- GitHub-ready structure

## Installation
1. `git clone {GITHUB_URL}`
2. `cd AbuRoot`
3. `python aburoot.py`

## Usage
- Set up your custom username and password on first run
- Use `sudo` for root commands, normal commands as usual
- Install root with `install_root`

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
