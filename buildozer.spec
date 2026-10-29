[app]
title = Lightning Dude
package.name = lightningdude
package.domain = org.jarvais

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,jinja

# Exclude heavy safetensors shards so APK only packs the clean GGUF model
source.exclude_dirs = tests, bin, .git, .github, llama.cpp, models/LightningDude-Sovereign-500M
source.exclude_exts = safetensors, part00, part01, part02, part03, part04, part05

version = 2.0.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,pyjnius==1.6.1,android

orientation = portrait
fullscreen = 0
android.presplash_color = #050D14

# 24/7 Background Service Integration
services = Jarvais:service.py:foreground

# Clean Asset path for Buildozer
android.add_assets = models/gguf/LightningDude-Sovereign-500M.gguf

# Full Device Authorities + Floating Orb Overlay + Background Service Permissions
android.permissions = INTERNET,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS,SYSTEM_ALERT_WINDOW,VIBRATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

p4a.branch = v2024.01.21

[buildozer]
log_level = 1
warn_on_root = 0
