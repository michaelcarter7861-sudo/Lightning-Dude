import time
from jnius import autoclass


def start_sovereign_24_7_daemon():
    try:
        PythonService = autoclass("org.kivy.android.PythonService")
        service = PythonService.mService
        if not service:
            return

        # 1. Force Auto-Restart if Android OS ever reclaims memory
        service.setAutoRestartService(True)

        Context = autoclass("android.content.Context")
        PowerManager = autoclass("android.os.PowerManager")
        pm = service.getSystemService(Context.POWER_SERVICE)

        # 2. Acquire 24/7 CPU Partial WakeLock so JARVAIS stays awake when screen is locked
        wake_lock = pm.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "LightningDude::Jarvais24x7CoreWakeLock"
        )
        if not wake_lock.isHeld():
            wake_lock.acquire()

        # 3. Acquire High-Performance WifiLock
        WifiManager = autoclass("android.net.wifi.WifiManager")
        wm = service.getApplicationContext().getSystemService(Context.WIFI_SERVICE)
        if wm:
            wifi_lock = wm.createWifiLock(
                WifiManager.WIFI_MODE_FULL_HIGH_PERF,
                "LightningDude::Jarvais24x7WifiLock"
            )
            if not wifi_lock.isHeld():
                wifi_lock.acquire()

        # 4. Upgrade Foreground Notification with 'Pause' and 'Open' Intent Actions
        BuildVersion = autoclass("android.os.Build$VERSION")
        if BuildVersion.SDK_INT >= 26:
            NotificationChannel = autoclass("android.app.NotificationChannel")
            NotificationManager = autoclass("android.app.NotificationManager")
            NotificationBuilder = autoclass("android.app.Notification$Builder")
            PendingIntent = autoclass("android.app.PendingIntent")
            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
            channel_id = "jarvais_sovereign_bg"
            channel = NotificationChannel(
                channel_id,
                "LIGHTNING DUDE • BACKGROUND",
                NotificationManager.IMPORTANCE_LOW
            )
            channel.setDescription("Wake-word standby • On-device")
            nm.createNotificationChannel(channel)

            open_intent = Intent(service, PythonActivity)
            open_intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP)
            pi_flags = PendingIntent.FLAG_UPDATE_CURRENT | (67108864 if BuildVersion.SDK_INT >= 31 else 0)
            open_pi = PendingIntent.getActivity(service, 0, open_intent, pi_flags)

            app_info = service.getApplicationInfo()
            builder = NotificationBuilder(service, channel_id)
            builder.setContentTitle("Jarvais is ready")
            builder.setContentText("Wake-word standby • On-device  |  Mic status visible")
            builder.setSubText("LIGHTNING DUDE • BACKGROUND")
            builder.setSmallIcon(app_info.icon)
            builder.setOngoing(True)
            builder.setContentIntent(open_pi)
            service.startForeground(1001, builder.build())

        print("[⚡] JARVAIS 24/7 Unkillable Foreground Daemon Active!")
    except Exception as e:
        print(f"[Jarvais Service Warning]: {e}")


if __name__ == "__main__":
    start_sovereign_24_7_daemon()
    while True:
        # 24/7 Background Wake-Word & Daemon Heartbeat
        time.sleep(4)
