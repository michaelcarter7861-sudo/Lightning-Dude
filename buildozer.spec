[app]
title = Lightning Dude
package.name = lightningdude
package.domain = org.jarvais

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,jinja

source.exclude_dirs = tests, bin, .git, .github, llama.cpp, models, assets
source.exclude_exts = safetensors, gguf, part00, part01, part02, part03, part04, part05

version = 2.0.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,pyjnius==1.6.1,android

orientation = portrait
fullscreen = 0
android.presplash_color = #050D14

# 24/7 Sticky Foreground Service
services = Jarvais:service.py:foreground:sticky

# Pack GGUF model directly into APK assets root
android.add_assets = assets/LightningDude-Sovereign-500M.gguf:LightningDude-Sovereign-500M.gguf

# Full 24/7 Background + Voice + Battery Exemption Permissions
android.permissions = INTERNET,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS,SYSTEM_ALERT_WINDOW,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,RECEIVE_BOOT_COMPLETED,VIBRATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

p4a.branch = v2024.01.21
p4a.hook = p4a_hook.py

[buildozer]
log_level = 1
warn_on_root = 0
