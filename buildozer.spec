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

services = Jarvais:service.py:foreground:sticky

# No add_assets here to prevent path crash; handled cleanly via python code extraction

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,WAKE_LOCK,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MICROPHONE,POST_NOTIFICATIONS,SYSTEM_ALERT_WINDOW,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,RECEIVE_BOOT_COMPLETED,MANAGE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WRITE_SETTINGS,QUERY_ALL_PACKAGES,PACKAGE_USAGE_STATS,CAMERA,CALL_PHONE,READ_CONTACTS,BLUETOOTH,VIBRATE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

p4a.branch = v2024.01.21
p4a.hook = p4a_hook.py

[buildozer]
log_level = 2
warn_on_root = 0
