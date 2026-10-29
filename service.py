import time
from jnius import autoclass

def start_foreground_notification():
    try:
        PythonService = autoclass("org.kivy.android.PythonService")
        service = PythonService.mService
        service.setAutoRestartService(True)

        Context = autoclass("android.content.Context")
        PowerManager = autoclass("android.os.PowerManager")
        pm = service.getSystemService(Context.POWER_SERVICE)
        wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "LightningDude::SovereignWakeLock")
        wake_lock.acquire()
    except Exception as e:
        print(f"Background Service Init Warning: {e}")

if __name__ == "__main__":
    start_foreground_notification()
    while True:
        # 24/7 Wake-word standby • On-device loop
        time.sleep(5)
