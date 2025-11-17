"""Script pour installer et configurer Playwright"""
import subprocess
import sys

print("🔧 Installation de Playwright...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])

print("📦 Installation de Chromium...")
subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

print("✅ Installation terminée!")

