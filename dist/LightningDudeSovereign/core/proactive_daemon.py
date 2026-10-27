class ProactiveJarvisDaemon:
    """
    Evaluates real-time device telemetry and user habits to trigger autonomous
    actions BEFORE the user even asks.
    """

    def evaluate_telemetry(self, telemetry: dict) -> list:
        actions = []
        ram_percent = float(telemetry.get("ram_usage_percent", 0.0))
        battery_pct = float(telemetry.get("battery_percent", 100.0))
        canary_compromised = bool(telemetry.get("canary_compromised", False))
        screen_has_error = bool(telemetry.get("screen_has_error", False))
        hour_24 = int(telemetry.get("current_hour", 12))

        if canary_compromised:
            actions.append({
                "priority": "CRITICAL",
                "trigger": "CANARY_HONEYPOT_BREACH",
                "autonomous_action": "isolate_network_and_kill_rogue_pid",
                "voice_alert": "Critical alert, Sir! A process touched the Canary Honeypot. Locking down process and tracing attacker."
            })

        if ram_percent >= 85.0:
            actions.append({
                "priority": "HIGH",
                "trigger": "HIGH_MEMORY_PRESSURE",
                "autonomous_action": "purge_background_cache_and_boost",
                "voice_alert": f"Sir, memory usage reached {ram_percent:.0f}%. Automatically purging background cache for smooth performance."
            })

        if battery_pct <= 15.0:
            actions.append({
                "priority": "MEDIUM",
                "trigger": "LOW_BATTERY_SHIELD",
                "autonomous_action": "enable_ultra_power_saving_mode",
                "voice_alert": f"Battery is at {battery_pct:.0f}%, Sir. Switching background tasks to low-power mode."
            })

        if screen_has_error:
            actions.append({
                "priority": "HIGH",
                "trigger": "LIVE_SCREEN_ERROR_DETECTED",
                "autonomous_action": "analyze_traceback_and_prepare_fix",
                "voice_alert": "Sir, I noticed a runtime error on your screen. I have analyzed the traceback and prepared a fix."
            })

        if hour_24 == 9 and telemetry.get("user_active", False):
            actions.append({
                "priority": "ROUTINE",
                "trigger": "MORNING_WORKSPACE_PREP",
                "autonomous_action": "preload_daily_workspace_and_briefing",
                "voice_alert": "Good morning, Sir. Pre-loading your workspace and checking overnight system logs."
            })

        return actions
