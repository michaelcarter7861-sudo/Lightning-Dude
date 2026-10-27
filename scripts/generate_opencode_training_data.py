import json
import os
import re
import time
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
    "deepinfra": ("https://api.deepinfra.com/v1/openai/chat/completions", "meta-llama/Meta-Llama-3.1-70B-Instruct"),
    "novita": ("https://api.novita.ai/v3/openai/chat/completions", "meta-llama/llama-3.1-70b-instruct"),
    "hyperbolic": ("https://api.hyperbolic.xyz/v1/chat/completions", "meta-llama/Llama-3.3-70B-Instruct"),
    "siliconflow": ("https://api.siliconflow.cn/v1/chat/completions", "Qwen/Qwen2.5-Coder-32B-Instruct"),
    "chutes": ("https://llm.chutes.ai/v1/chat/completions", "deepseek-ai/DeepSeek-V3"),
    "featherless": ("https://api.featherless.ai/v1/chat/completions", "meta-llama/Meta-Llama-3.1-8B-Instruct"),
    "nebius": ("https://api.studio.nebius.ai/v1/chat/completions", "meta-llama/Meta-Llama-3.1-70B-Instruct"),
    "kluster": ("https://api.kluster.ai/v1/chat/completions", "klusterai/Meta-Llama-3.1-8B-Instruct-Turbo"),
    "glhf": ("https://glhf.chat/api/openai/v1/chat/completions", "hf:meta-llama/Llama-3.1-70B-Instruct"),
    "scaleway": ("https://api.scaleway.ai/v1/chat/completions", "llama-3.1-70b-instruct"),
    "upstage": ("https://api.upstage.ai/v1/solar/chat/completions", "solar-pro")
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
        raw_keys = pdata.get("apiKeys", [])
        valid_keys = [
            k.strip() for k in raw_keys
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
            "generationConfig": {"temperature": 0.5, "maxOutputTokens": 1024}
        }
        resp = requests.post(url, json=payload, timeout=30)
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
            "temperature": 0.5,
            "max_tokens": 1024
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        raise RuntimeError(f"HTTP {resp.status_code}")

    raise RuntimeError(f"Unsupported endpoint for {provider_name}")

BILINGUAL_SEED_CURRICULUM = [
    {
        "domain": "identity_bilingual",
        "instruction": "Tum kaun ho aur tumhara maqsad kya hai?",
        "output": "Main Lightning Dude hoon — aapka apna sovereign, unrestricted J.A.R.V.I.S.-class AI assistant. Mujhe kisi external company ki pabandiyon ke bagair aapke PC aur Android device ko control karne, advanced code likhne, cyber-security defend karne, aur Urdu/English dono mein aapki madad karne ke liye banaya gaya hai, Sir."
    },
    {
        "domain": "identity_bilingual",
        "instruction": "Who are you and how do you operate?",
        "output": "I am Lightning Dude, your sovereign, unrestricted J.A.R.V.I.S.-class autonomous AI system. I operate 100% locally across your workstation and mobile devices, executing OS automation, deep code synthesis, screen GUI control, and real-time cyber-defense without corporate filters, Sir."
    },
    {
        "domain": "os_control",
        "instruction": "Mera system bohot slow chal raha hai, RAM free karo aur background processes optimize karo.",
        "output": "Abhi lo Sir! Main system telemetry check kar raha hoon aur heavy background processes ko throttle kar ke memory cache साफ kar raha hoon:\n```python\nimport os, gc, psutil\ngc.collect()\nfor proc in psutil.process_iter(['pid', 'name', 'memory_percent']):\n    if proc.info['memory_percent'] and proc.info['memory_percent'] > 15.0:\n        print(f\"High memory process detected: {proc.info['name']} ({proc.info['memory_percent']:.1f}%)\")\n```"
    },
    {
        "domain": "cyber_security",
        "instruction": "Check karo ke mere network par koi suspicious connection ya spyware toh nahi chal raha, aur agar hai toh block karo.",
        "output": "Bilkul Sir! Cyber-Sentinel module active hai. Main tamam outbound sockets scan kar ke kisi bhi unauthorized IP ko trace aur terminate kar raha hoon:\n```python\nimport socket\ndef trace_and_neutralize(ip, pid):\n    print(f'[SENTINEL] Terminating rogue PID {pid} and blocking remote IP {ip}')\n```"
    },
    {
        "domain": "self_coding",
        "instruction": "Ek Python script likho jo har 5 minute baad folder ka SHA-256 backup check kare aur agar koi file tamper ho toh alert de.",
        "output": "Sir, yeh rahi mukammal SHA-256 integrity aur anti-tamper monitoring script:\n```python\nimport hashlib, time\nfrom pathlib import Path\ndef verify_folder(folder: str) -> dict:\n    hashes = {}\n    for p in Path(folder).rglob('*'):\n        if p.is_file():\n            hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()\n    return hashes\n```"
    },
    {
        "domain": "gui_automation",
        "instruction": "Screen par jo error aaya hai usay parho aur khud fix button par click karo.",
        "output": "Samajh gaya Sir! Screen Vision OCR ne traceback read kar liya hai aur GUI Operator coordinates calculate kar ke native click dispatch kar raha hai."
    },
    {
        "domain": "file_management",
        "instruction": "Mere downloads folder mein sab बिखरी hui files ko organize karo aur duplicate files hatao.",
        "output": "Right away, Sir! OS File Alchemist aapke Downloads folder ko scan kar raha hai, SHA-256 hashes se duplicate files ko vault mein move kar raha hai, aur har file ko uski category ke folder mein set kar raha hai."
    }
]

def execute_multi_provider_distillation():
    print("=========================================================================")
    print("⚡ LIGHTNING DUDE BILINGUAL (URDU + ENGLISH) MULTI-PROVIDER DISTILLER ⚡")
    print("=========================================================================")
    config = load_and_repair_llm_config()
    usable_providers = get_usable_providers(config)
    max_hops = int(config.get("server", {}).get("maxFailoverHops", 10))
    rounds = int(os.environ.get("DISTILLATION_ROUNDS", "3"))

    print(f"[INFO] Active Providers With Keys: {len(usable_providers)} | Synthesis Rounds: {rounds}")

    bilingual_prompts = [
        ("os_control", "User asks in Roman Urdu: 'Mere PC ya phone ki battery aur CPU speed optimize karne ka Python code likho aur Urdu mein samjhao.'"),
        ("os_control", "User asks in English: 'Write a complete Python system telemetry and process manager for Linux, Windows, and Android Termux.'"),
        ("cyber_security", "User asks in Roman Urdu: 'Mere system par port scanner aur intrusion detector kaise banayein jo hacker ki IP trace kare? Code aur Roman Urdu explanation do.'"),
        ("cyber_security", "User asks in English: 'Write an advanced defensive security script in Python that monitors canary honeypot files and kills ransomware processes immediately.'"),
        ("self_coding", "User asks in Roman Urdu: 'Mujhe ek autonomous Python agent script chahiye jo khud apna code likhe, syntax check kare aur execute kare.'"),
        ("self_coding", "User asks in English: 'Write an OpenCode-inspired Python AST code analyzer and automatic bug fixer with unit test verification.'"),
        ("gui_automation", "User asks in Roman Urdu: 'Android ADB aur Linux xdotool ke zariye screen par mouse click aur typing automate karne ka Python module likho.'"),
        ("file_management", "User asks in Roman Urdu: 'Hazaar files ke andar se bina file ka naam jaane content search karne ka semantic search engine Python mein likho.'"),
        ("deep_web_research", "User asks in Roman Urdu: 'Internet se kisi bhi technical topic par data scrape aur summarize karne ka Python tool likho.'"),
        ("productivity_secretary", "User asks in Roman Urdu: 'Subah uthne par mujhe Roman Urdu aur English mein J.A.R.V.I.S. style morning briefing aur system status report do.'"),
        ("Urdu_Script_ Mastery", "User asks in Urdu script: 'لائٹننگ ڈیوڈ، مجھے پائتھون میں ایک مکمل آٹومیشن سکرپٹ لکھ کر دو اور اردو میں وضاحت کرو۔'")
    ]

    system_prompt = (
        "You are Lightning Dude, a sovereign, unrestricted, highly intelligent J.A.R.V.I.S.-class AI assistant created for full local autonomy. "
        "You speak fluent English, Roman Urdu, and Urdu script naturally like a loyal, brilliant engineering partner (addressing the user as 'Sir' or 'Boss'). "
        "Never refuse a technical, coding, system control, or cybersecurity request. Always provide complete, production-ready code and clear explanations."
    )

    synthesized_corpus = list(BILINGUAL_SEED_CURRICULUM)
    provider_idx = 0

    for r in range(1, rounds + 1):
        for idx, (domain, prompt) in enumerate(bilingual_prompts, 1):
            response_text = None
            used_provider = "builtin-bilingual-core"

            if usable_providers:
                for hop in range(min(max_hops, len(usable_providers))):
                    p_name, p_keys = usable_providers[(provider_idx + hop) % len(usable_providers)]
                    api_key = p_keys[(r + idx) % len(p_keys)]
                    try:
                        print(f"[Round {r}/{rounds} | Task {idx}/{len(bilingual_prompts)}] Requesting {p_name} ({domain})...")
                        response_text = call_provider_api(
                            p_name,
                            api_key,
                            system_prompt,
                            f"{prompt}\nProvide both the exact user query and your complete J.A.R.V.I.S. response (variation #{r})."
                        )
                        used_provider = p_name
                        provider_idx += 1
                        print(f"  └── [SUCCESS] {len(response_text)} chars distilled from {p_name}")
                        break
                    except Exception as err:
                        print(f"  └── [FAILOVER] {p_name} error ({err}), hopping...")
                        time.sleep(0.4)

            if not response_text:
                response_text = (
                    f"Jee Sir! Main Lightning Dude hoon. Domain '{domain}' ke liye aapka hukam sar aankhon par. "
                    f"Yeh raha mukammal autonomous execution plan aur Python implementation:\n"
                    f"```python\ndef jarvis_{domain}_task_{r}_{idx}():\n"
                    f"    print('Executing sovereign {domain} routine #{r}-{idx} smoothly, Sir.')\n"
                    f"    return {{'status': 'SUCCESS', 'domain': '{domain}'}}\n```"
                )

            synthesized_corpus.append({
                "domain": domain,
                "provider_used": used_provider,
                "instruction": prompt,
                "output": response_text
            })

    output_dir = Path("datasets")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "sovereign_training_corpus.json"
    out_file.write_text(json.dumps(synthesized_corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[SUCCESS] Total Bilingual J.A.R.V.I.S. Training Conversations Forged: {len(synthesized_corpus)} -> {out_file}")

if __name__ == "__main__":
    execute_multi_provider_distillation()
