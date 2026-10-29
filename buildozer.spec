[app]
title = Lightning Dude JARVAIS
package.name = lightningdude
package.domain = com.jarvais
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ldbrain,xml,db,txt
source.exclude_dirs = .git,__pycache__,tests,.github,models
android.add_assets = models/LightningDude-Sovereign-500M:models/LightningDude-Sovereign-500M,knowledge_vault:knowledge_vault
version = 2.2.0
requirements = python3==3.11.6,hostpython3==3.11.6,kivy==2.3.0,pyjnius==1.6.1,requests,urllib3,chardet,idna,certifi
services = Jarvaisdaemon:service/main.py:sticky
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_CONTACTS,WRITE_CONTACTS,READ_CALL_LOG,WRITE_CALL_LOG,READ_PHONE_STATE,CALL_PHONE,ANSWER_PHONE_CALLS,READ_SMS,SEND_SMS,RECEIVE_SMS,BIND_NOTIFICATION_LISTENER_SERVICE,PACKAGE_USAGE_STATS,SYSTEM_ALERT_WINDOW,BIND_ACCESSIBILITY_SERVICE,BIND_DEVICE_ADMIN,QUERY_ALL_PACKAGES,RECORD_AUDIO,CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,WAKE_LOCK,FOREGROUND_SERVICE,RECEIVE_BOOT_COMPLETED,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,POST_NOTIFICATIONS,VIBRATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.ant_path = /home/runner/.buildozer/android/platform/apache-ant-1.9.4
android.accept_sdk_license = True
android.archs = arm64-v8a
p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
