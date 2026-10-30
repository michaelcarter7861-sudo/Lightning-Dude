[app]
title = Lightning Dude
package.name = lightningdude
package.domain = org.jarvais

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,jinja

# Exclude heavy safetensors & models folder from private.mp3 so GGUF is only packed once as uncompressed asset
source.exclude_dirs = tests, bin, .git, .github, llama.cpp, models, assets
source.exclude_exts = safetensors, gguf, part00, part01, part02, part03, part04, part05

version = 2.0.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,pyjnius==1.6.1,android

orientation = portrait
fullscreen = 0
android.presplash_color = #050D14

# 24/7 Sticky Foreground Service
services = Jarvais:service.py:foreground:sticky

# Pack GGUF model AND cross-compiled ARM64 llama-cli binary directly into APK assets root
android.add_assets = assets/LightningDude-Sovereign-500M.gguf:LightningDude-Sovereign-500M.gguf,assets/llama-cli:llama-cli

# Complete Device Control Authorities + 24/7 Background + Hands-Free Audio + All Files + Overlay + System Settings
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,WAKE_LOCK,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MICROPHONE,POST_NOTIFICATIONS,SYSTEM_ALERT_WINDOW,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,RECEIVE_BOOT_COMPLETED,MANAGE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WRITE_SETTINGS,QUERY_ALL_PACKAGES,PACKAGE_USAGE_STATS,CAMERA,CALL_PHONE,READ_CONTACTS,BLUETOOTH,VIBRATE

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
