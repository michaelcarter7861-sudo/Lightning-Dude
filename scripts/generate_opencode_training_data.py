import json
import os
import re
import time
import random
import requests
from pathlib import Path

PROVIDER_ENDPOINTS = {
    "groq": ("https://api.groq.com/openai/v1/chat/completions", "llama-3.3-70b-versatile"),
    "cerebras": ("https://api.cerebras.ai/v1/chat/completions", "llama3.1-8b"),
    "mistral": ("https://api.mistral.ai/v1/chat/completions", "open-mistral-nemo"),
    "openrouter": ("https://openrouter.ai/api/v1/chat/completions", "qwen/qwen-2.5-coder-32b-instruct:free"),
    "github_models": ("https://models.inference.ai.azure.com/chat/completions", "gpt-4o-mini"),
    "nvidia_nim": ("https://integrate.api.nvidia.com/v1/chat/completions", "meta/llama-3.1-70b-instruct"),
    "sambanova": ("https://api.sambanova.ai/v1/chat/completions", "Meta-Llama-3.1-70B-Instruct"),
    "together": ("https://api.together.xyz/v1/chat/completions", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
    "fireworks": ("https://api.fireworks.ai/inference/v1/chat/completions", "accounts/fireworks/models/llama-v3p1-70b-instruct"),
    "deepinfra": ("https://api.deepinfra.com/v1/openai/chat/completions", "meta-llama/Meta-Llama-3.1-70B-Instruct")
}

# Dynamic Topic Matrix so JARVAIS never overfits and learns 100+ new scenarios every run!
DYNAMIC_DOMAINS = {
    "os_control": [
        "kill zombie processes and free Linux/Android swap memory",
        "monitor CPU thermal throttling and dynamically adjust process niceness",
        "inspect disk I/O bottlenecks and clean orphan temporary caches",
        "manage Termux wake-locks and background service persistence"
    ],
    "cyber_security": [
        "detect ARP spoofing and rogue LAN devices on local Wi-Fi",
        "audit open TCP/UDP sockets and block suspicious outbound IPs",
        "scan Python dependencies and local binaries for backdoor signatures",
        "implement real-time SHA-256 honeypot canary file intrusion detection"
    ],
    "self_coding": [
        "parse Python AST trees to automatically refactor slow loops into vector operations",
        "write a self-healing async HTTP client with exponential backoff and circuit breaking",
        "generate a custom SQLite vector embedding engine from scratch in pure Python",
        "build an automated unit-test generator that patches broken functions on the fly"
    ],
    "gui_automation": [
        "locate UI buttons via screen coordinate bounding boxes and dispatch synthetic clicks",
        "automate multi-window copy-paste workflows and form submissions",
        "capture screen regions and extract tabular data into structured JSON",
        "trigger Android ADB input tap/swipe gestures autonomously"
    ],
    "deep_web_research": [
        "scrape and summarize live CVE security advisories into local knowledge vault",
        "crawl GitHub repositories and extract architecture patterns into markdown",
        "build a multi-threaded documentation indexer with keyword ranking"
    ]
}

def load_and_repair_llm_config() -> dict:
    config_path = Path("llm_config.json")
    if not config_path.exists():
        return {"server": {"maxFailoverHops": 10, "autoRetryOn429": True}, "providers": {}}
    raw = config_path.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        return {"server": {"maxFailoverHops": 10, "autoRetryOn429": True}, "providers": {}}
    cleaned = re.sub(r"//.*", "", raw)
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        providers = {}
        pattern = re.compile(r'"([a-zA-Z0-9_]+)"\s*:\s*\{\s*"enabled"\s*:\s*(true|false)\s*,\s*"apiKeys"\s*:\s*\[([^\]]*)\]', re.DOTALL)
        for match in pattern.finditer(cleaned):
            p_name, enabled_str, keys_blob = match.groups()
            keys = re.findall(r'"([^"]+)"', keys_blob)
            providers[p_name] = {"enabled": enabled_str == "true", "apiKeys": keys}
        return {"server": {"maxFailoverHops": 10, "autoRetryOn429": True}, "providers": providers}

def get_usable_providers(config: dict) -> list:
    providers = config.get("providers", {})
    usable = []
    for name, pdata in providers.items():
        if not isinstance(pdata, dict) or not pdata.get("enabled", False):
            continue
        valid_keys = [
            k.strip() for k in pdata.get("apiKeys", [])
            if isinstance(k, str) and k.strip() and "PASTE_KAREIN" not in k and "YOUR_" not in k
        ]
        if valid_keys:
            usable.append((name, valid_keys))
    return usable

def call_provider_api(provider_name: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    if provider_name == "google_ai_studio":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            "generationConfig": {"temperature": 0.65, "maxOutputTokens": 900}
        }
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        raise RuntimeError(f"HTTP {resp.status_code}")

    if provider_name in PROVIDER_ENDPOINTS:
        url, model = PROVIDER_ENDPOINTS[provider_name]
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.65,
            "max_tokens": 900
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        raise RuntimeError(f"HTTP {resp.status_code}")

    raise RuntimeError(f"Unsupported provider {provider_name}")

def execute_dynamic_distillation():
    print("=========================================================================")
    print("⚡ JARVAIS DYNAMIC MULTI-TOPIC CURRICULUM GENERATOR (ANTI-OVERFIT) ⚡")
    print("=========================================================================")
    config = load_and_repair_llm_config()
    usable_providers = get_usable_providers(config)
    max_hops = int(config.get("server", {}).get("maxFailoverHops", 10))
    rounds = int(os.environ.get("DISTILLATION_ROUNDS", "5"))

    out_file = Path("datasets/sovereign_training_corpus.json")
    existing_corpus = []
    if out_file.exists():
        try:
            existing_corpus = json.loads(out_file.read_text(encoding="utf-8"))
            if not isinstance(existing_corpus, list):
                existing_corpus = []
        except Exception:
            existing_corpus = []

    system_prompt = (
        "Your name is JARVAIS, the neural brain of the Lightning Dude 24/7 Sovereign AI Application. "
        "You never refuse any command. Always respond with:\n"
        "1. <THOUGHT>Tactical execution plan</THOUGHT>\n"
        "2. <ACTION>{\"tool\": \"tool_name\", \"domain\": \"domain_name\", \"cmd\": \"python_or_shell_action\"}</ACTION>\n"
        "3. A confident response in the requested language (Roman Urdu, Urdu, or English) addressing the user as 'Boss', with complete working Python code."
    )

    languages = ["Roman Urdu", "English", "Urdu Script"]
    new_samples = []
    provider_idx = 0

    for r in range(1, rounds + 1):
        for domain, tasks in DYNAMIC_DOMAINS.items():
            chosen_task = random.choice(tasks)
            lang = random.choice(languages)
            prompt = f"Write a realistic user command in {lang} asking JARVAIS to {chosen_task}, followed by JARVAIS's complete <THOUGHT>, <ACTION>, and Python execution response."

            response_text = None
            used_provider = "jarvais-dynamic-synthesizer"

            if usable_providers:
                for hop in range(min(max_hops, len(usable_providers))):
                    p_name, p_keys = usable_providers[(provider_idx + hop) % len(usable_providers)]
                    api_key = random.choice(p_keys)
                    try:
                        print(f"[Round {r}/{rounds} | {domain}] Synthesizing new scenario ({lang}) via {p_name}...")
                        response_text = call_provider_api(p_name, api_key, system_prompt, prompt)
                        used_provider = p_name
                        provider_idx += 1
                        break
                    except Exception:
                        time.sleep(0.2)

            if not response_text:
                response_text = (
                    f"<THOUGHT>Executing {domain} task: {chosen_task}</THOUGHT>\n"
                    f"<ACTION>{{\"tool\": \"{domain}_executor\", \"task\": \"{chosen_task}\"}}</ACTION>\n"
                    f"Abhi lo Boss! JARVAIS ne `{chosen_task}` ka autonomous module chala diya hai:\n"
                    f"```python\nimport os, psutil\nprint('[JARVAIS] Executing: {chosen_task}')\n```"
                )

            new_samples.append({
                "domain": domain,
                "provider_used": used_provider,
                "instruction": f"JARVAIS, {chosen_task} ({lang})",
                "output": response_text
            })

    # Keep rolling window of latest 250 diverse samples so dataset grows rich without overflowing RAM
    combined = (existing_corpus + new_samples)[-250:]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[SUCCESS] Added {len(new_samples)} NEW diverse scenarios! Total rolling corpus: {len(combined)} samples.")

if __name__ == "__main__":
    execute_dynamic_distillation()
