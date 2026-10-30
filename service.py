import time
from jnius import autoclass

def start_unkillable_24_7_service():
    try:
        PythonService = autoclass("org.kivy.android.PythonService")
        service = PythonService.mService
        if not service:
            return

        # Auto-restart service if Android ever tries to reclaim memory
        service.setAutoRestartService(True)

        Context = autoclass("android.content.Context")
        PowerManager = autoclass("android.os.PowerManager")
        pm = service.getSystemService(Context.POWER_SERVICE)

        # Acquire 24/7 CPU Partial WakeLock so JARVAIS stays awake even when screen is off
        wake_lock = pm.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "LightningDude::Jarvais24x7WakeLock"
        )
        if not wake_lock.isHeld():
            wake_lock.acquire()

        # Also acquire WifiLock for uninterrupted background operation
        WifiManager = autoclass("android.net.wifi.WifiManager")
        wm = service.getApplicationContext().getSystemService(Context.WIFI_SERVICE)
        if wm:
            wifi_lock = wm.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "LightningDude::JarvaisWifiLock")
            if not wifi_lock.isHeld():
                wifi_lock.acquire()

        print("[⚡] JARVAIS 24/7 Foreground Service & WakeLocks Active!")
    except Exception as e:
        print(f"[Jarvais Service Init Notice]: {e}")

if __name__ == "__main__":
    start_unkillable_24_7_service()
    while True:
        # 24/7 Background Heartbeat Loop
        time.sleep(4)
