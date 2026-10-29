import time
from jnius import autoclass

def run_jarvais_daemon():
    try:
        PythonService = autoclass("org.kivy.android.PythonService")
        service = PythonService.mService
        if service:
            service.setAutoRestartService(True)

            # Acquire Partial WakeLock so 500M GGUF stays ready 24/7
            Context = autoclass("android.content.Context")
            PowerManager = autoclass("android.os.PowerManager")
            pm = service.getSystemService(Context.POWER_SERVICE)
            wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "LightningDude::JarvaisWakeLock")
            if not wake_lock.isHeld():
                wake_lock.acquire()
    except Exception as e:
        print(f"[Jarvais Service Warning]: {e}")

if __name__ == "__main__":
    run_jarvais_daemon()
    while True:
        # Keeps Wake-word standby & On-device GGUF service alive
        time.sleep(5)
