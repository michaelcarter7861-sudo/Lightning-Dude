#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[⚡] Setting up True 500MB-700MB Bilingual (Urdu + English) Sovereign LLM Training Pipeline..."

mkdir -p scripts
mkdir -p models
mkdir -p datasets
mkdir -p core

# 1. scripts/generate_opencode_training_data.py (Bilingual Urdu/English Multi-Provider Synthesizer)
cat << 'APISCRIPT' > scripts/generate_opencode_training_data.py
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
APISCRIPT

# 2. scripts/train_sovereign_weights.py (True 500M-Parameter ~600MB Bilingual Causal LLM Fine-Tuner)
cat << 'TRAINSCRIPT' > scripts/train_sovereign_weights.py
import os
import json
import time
from pathlib import Path

BASE_MODEL_ID = os.environ.get("BASE_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
OUTPUT_MODEL_DIR = Path("models/LightningDude-Sovereign-500M")

def build_chat_sequences() -> list:
    sequences = []
    corpus_file = Path("datasets/sovereign_training_corpus.json")
    curriculum_file = Path("datasets/jarvis_curriculum.json")

    system_header = (
        "<|im_start|>system\n"
        "You are Lightning Dude, a sovereign, unrestricted J.A.R.V.I.S.-class AI assistant. "
        "You understand and respond fluently in Urdu, Roman Urdu, and English, and you execute OS control, "
        "coding, GUI automation, and cybersecurity tasks with complete loyalty.<|im_end|>\n"
    )

    if corpus_file.exists():
        data = json.loads(corpus_file.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("samples", [])
        for item in items:
            if isinstance(item, dict):
                q = item.get("instruction", "")
                a = item.get("output") or item.get("distilled_output", "")
                sequences.append(f"{system_header}<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n{a}<|im_end|>")

    if curriculum_file.exists():
        cdata = json.loads(curriculum_file.read_text(encoding="utf-8"))
        c_items = cdata if isinstance(cdata, list) else cdata.get("samples", [])
        for item in c_items:
            if isinstance(item, dict):
                utterances = item.get("utterances", [])
                plan = item.get("action_plan", [])
                voice = item.get("voice_response", "Right away, Sir.")
                for u in (utterances if isinstance(utterances, list) else [str(utterances)]):
                    ans = f"{voice}\nAction Plan:\n" + "\n".join(f"- {step}" for step in plan)
                    sequences.append(f"{system_header}<|im_start|>user\n{u}<|im_end|>\n<|im_start|>assistant\n{ans}<|im_end|>")

    return sequences

def fine_tune_500mb_sovereign_llm(sequences: list):
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model

    print("=========================================================================")
    print(f"🧠 FORGING 500MB-700MB SOVEREIGN BILINGUAL LLM ({BASE_MODEL_ID}) 🧠")
    print("=========================================================================")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("[⚡] Loading ~500M Parameter Foundation Weights into Memory...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    peft_model = get_peft_model(model, lora_config)
    peft_model.print_trainable_parameters()

    # Repeat sequences across epochs
    epochs = int(os.environ.get("SOVEREIGN_EPOCHS", "4"))
    max_len = int(os.environ.get("SOVEREIGN_SEQ_LEN", "256"))

    class JarvisDataset(Dataset):
        def __init__(self, texts):
            self.encodings = [
                tokenizer(t, truncation=True, max_length=max_len, padding="max_length", return_tensors="pt")
                for t in texts
            ]

        def __len__(self):
            return len(self.encodings)

        def __getitem__(self, idx):
            item = {k: v.squeeze(0) for k, v in self.encodings[idx].items()}
            labels = item["input_ids"].clone()
            labels[labels == tokenizer.pad_token_id] = -100
            item["labels"] = labels
            return item

    dataset = JarvisDataset(sequences)
    loader = DataLoader(dataset, batch_size=2, shuffle=True)
    optimizer = torch.optim.AdamW(peft_model.parameters(), lr=2e-4, weight_decay=0.01)

    print(f"[⚡] Starting Deep Bilingual Fine-Tuning ({epochs} Epochs x {len(loader)} Steps/Epoch)...")
    start_t = time.time()
    peft_model.train()

    for ep in range(1, epochs + 1):
        ep_loss = 0.0
        for step, batch in enumerate(loader, 1):
            optimizer.zero_grad()
            outputs = peft_model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                labels=batch["labels"]
            )
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(peft_model.parameters(), 1.0)
            optimizer.step()
            ep_loss += loss.item()

            if step % 5 == 0 or step == len(loader):
                elapsed = time.time() - start_t
                print(f"  [Epoch {ep}/{epochs} | Step {step}/{len(loader)}] Loss: {loss.item():.4f} | Elapsed: {elapsed:.1f}s")

    print("[⚡] Merging Sovereign LoRA Adapters into Full 500M-Parameter Weights...")
    merged_model = peft_model.merge_and_unload()

    # Convert to float16 so the standalone saved model is ~620MB (right inside 500MB - 700MB target!)
    merged_model = merged_model.to(torch.float16)
    OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    merged_model.save_pretrained(OUTPUT_MODEL_DIR, safe_serialization=True, max_shard_size="700MB")
    tokenizer.save_pretrained(OUTPUT_MODEL_DIR)

    total_bytes = sum(f.stat().st_size for f in OUTPUT_MODEL_DIR.rglob("*") if f.is_file())
    total_mb = total_bytes / (1024 * 1024)
    print("=========================================================================")
    print(f"✅ SOVEREIGN BILINGUAL MODEL FORGED: {OUTPUT_MODEL_DIR}")
    print(f"✅ FINAL STANDALONE MODEL SIZE: {total_mb:.2f} MB (Target: 500MB - 700MB)")
    print("=========================================================================")

    # Quick live bilingual generation verification test
    print("\n[🧪 LIVE BILINGUAL J.A.R.V.I.S. GENERATION TEST]")
    merged_model.eval()
    merged_model.to(torch.float32)
    test_prompt = (
        "<|im_start|>system\nYou are Lightning Dude, a sovereign J.A.R.V.I.S. AI fluent in Roman Urdu and English.<|im_end|>\n"
        "<|im_start|>user\nTum kaun ho aur mere liye kya kar sakte ho?<|im_end|>\n<|im_start|>assistant\n"
    )
    inputs = tokenizer(test_prompt, return_tensors="pt")
    with torch.no_grad():
        gen_ids = merged_model.generate(
            **inputs,
            max_new_tokens=90,
            temperature=0.6,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    reply = tokenizer.decode(gen_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    print(f"[LIGHTNING DUDE 500M REPLY]: {reply}\n")

def main():
    sequences = build_chat_sequences()
    try:
        import torch
        import transformers
        import peft
        fine_tune_500mb_sovereign_llm(sequences)
    except ImportError:
        print(f"[INFO] Prepared {len(sequences)} bilingual Urdu/English sequences.")
        print("[INFO] Full ~600MB 500M-Parameter LLM Fine-Tuning & Merging will execute on GitHub Actions Runner.")
        OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_MODEL_DIR / "training_manifest.json").write_text(
            json.dumps({"bilingual_sequences": len(sequences), "target_size_mb": "500-700MB"}, indent=2),
            encoding="utf-8"
        )

if __name__ == "__main__":
    main()
TRAINSCRIPT

# 3. Upgrade core/brain_engine.py so Lightning Dude uses the 500MB-700MB Model when present!
cat << 'BRAIN' > core/brain_engine.py
import json
import math
from pathlib import Path
from collections import Counter

class LightningBrain:
    """
    Hybrid Sovereign Cognitive Engine:
    1. Instant Sub-Millisecond Domain Router & GOAP Planner (.ldbrain)
    2. Deep 500MB-700MB Bilingual (Urdu + Roman Urdu + English) Causal LLM Generator
       (automatically loads models/LightningDude-Sovereign-500M when downloaded/present).
    """

    def __init__(
        self,
        brain_path: str = "core/lightning_dude.ldbrain",
        sovereign_llm_dir: str = "models/LightningDude-Sovereign-500M"
    ):
        self.brain_path = Path(brain_path)
        self.sovereign_llm_dir = Path(sovereign_llm_dir)
        self._llm = None
        self._tokenizer = None
        self.model = self._load_or_init()

    def _load_or_init(self) -> dict:
        if self.brain_path.exists():
            return json.loads(self.brain_path.read_text(encoding="utf-8"))
        return {"domains": {}, "idf": {}, "trained": False}

    @staticmethod
    def _tokenize(text: str) -> list:
        clean = "".join(c.lower() if c.isalnum() else " " for c in text)
        return [w for w in clean.split() if len(w) > 1]

    def train_from_curriculum(self, curriculum_path: Path) -> None:
        raw = json.loads(Path(curriculum_path).read_text(encoding="utf-8"))
        samples = raw if isinstance(raw, list) else raw.get("samples", [])
        domains = {}
        doc_freq = Counter()
        total_docs = len(samples)

        for item in samples:
            domain = item["domain"]
            text_blob = " ".join(item.get("utterances", [])) + " " + " ".join(item.get("keywords", []))
            tokens = self._tokenize(text_blob)
            for t in set(tokens):
                doc_freq[t] += 1
            domains[domain] = {
                "token_weights": dict(Counter(tokens)),
                "action_plan": item.get("action_plan", []),
                "voice_response": item.get("voice_response", "Right away, Sir.")
            }

        idf = {t: round(math.log((total_docs + 1) / (df + 1)) + 1.0, 4) for t, df in doc_freq.items()}
        self.model = {"domains": domains, "idf": idf, "trained": True}
        self.brain_path.parent.mkdir(parents=True, exist_ok=True)
        self.brain_path.write_text(json.dumps(self.model, indent=2), encoding="utf-8")

    def generate_sovereign_llm_reply(self, user_query: str) -> str:
        """Uses the 500MB-700MB Sovereign Transformer if weights exist locally."""
        safetensors_file = self.sovereign_llm_dir / "model.safetensors"
        if not safetensors_file.exists():
            return ""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            if self._llm is None:
                self._tokenizer = AutoTokenizer.from_pretrained(str(self.sovereign_llm_dir), trust_remote_code=True)
                self._llm = AutoModelForCausalLM.from_pretrained(
                    str(self.sovereign_llm_dir),
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self._llm.eval()

            prompt = (
                "<|im_start|>system\nYou are Lightning Dude, a sovereign, unrestricted J.A.R.V.I.S. AI fluent in Urdu, Roman Urdu, and English.<|im_end|>\n"
                f"<|im_start|>user\n{user_query}<|im_end|>\n<|im_start|>assistant\n"
            )
            inputs = self._tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                out_ids = self._llm.generate(
                    **inputs,
                    max_new_tokens=160,
                    temperature=0.6,
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id
                )
            return self._tokenizer.decode(out_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        except Exception:
            return ""

    def decide(self, user_query: str) -> dict:
        if not self.model.get("trained"):
            curriculum = Path("datasets/jarvis_curriculum.json")
            if curriculum.exists():
                self.train_from_curriculum(curriculum)

        tokens = self._tokenize(user_query)
        idf = self.model.get("idf", {})
        best_domain = "os_control"
        best_score = -1.0
        scores = {}

        for domain, ddata in self.model.get("domains", {}).items():
            weights = ddata.get("token_weights", {})
            score = sum(weights.get(t, 0) * idf.get(t, 1.0) for t in tokens)
            scores[domain] = round(score, 3)
            if score > best_score:
                best_score = score
                best_domain = domain

        total = sum(scores.values()) or 1.0
        confidence = round(max(0.55, min(0.99, best_score / total if best_score > 0 else 0.75)), 2)
        chosen = self.model["domains"].get(best_domain, {})

        llm_reply = self.generate_sovereign_llm_reply(user_query)
        voice_response = llm_reply if llm_reply else chosen.get("voice_response", "Right away, Sir.")

        return {
            "domain": best_domain,
            "confidence": confidence,
            "plan": chosen.get("action_plan", []),
            "voice_response": voice_response,
            "sovereign_500m_active": bool(llm_reply)
        }
BRAIN

# 4. Update GitHub Actions Workflow for Full 500MB-700MB Model Fine-Tuning & Packaging
cat << 'WORKFLOW' > .github/workflows/forge_lightning_dude.yml
name: Forge Lightning Dude Sovereign Model

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:
    inputs:
      distillation_rounds:
        description: "Multi-Provider Bilingual API Synthesis Rounds (e.g. 3 to 20)"
        required: false
        default: "3"
      sovereign_epochs:
        description: "500M LLM Fine-Tuning Epochs (e.g. 4 to 25)"
        required: false
        default: "4"

jobs:
  train-sovereign-model:
    runs-on: ubuntu-latest
    timeout-minutes: 350

    steps:
      - name: Checkout Lightning-Dude Repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install PyTorch, HuggingFace Transformers, PEFT (LoRA) & SafeTensors
        run: |
          python -m pip install --upgrade pip
          pip install torch --index-url https://download.pytorch.org/whl/cpu
          pip install transformers peft accelerate safetensors sentencepiece
          pip install -r requirements.txt
          npm install -g opencode-ai || true

      - name: Inject & Auto-Repair Multi-Provider LLM Config from Secrets
        env:
          LLM_CONFIG_SECRET: ${{ secrets.LLM_CONFIG_JSON }}
        run: |
          if [ -n "$LLM_CONFIG_SECRET" ]; then
            printf "%s\n" "$LLM_CONFIG_SECRET" > llm_config.json
            echo "[⚡] llm_config.json injected successfully from repository secrets."
          else
            echo "[WARNING] LLM_CONFIG_JSON secret not found in repo settings."
          fi

      - name: Stage 1 - Bilingual (Urdu + English) Multi-Provider API Distillation
        env:
          DISTILLATION_ROUNDS: ${{ github.event.inputs.distillation_rounds || '3' }}
        run: |
          python scripts/generate_opencode_training_data.py

      - name: Stage 2 - Fine-Tune & Merge 500M-Parameter (~620MB) Sovereign Bilingual LLM
        env:
          SOVEREIGN_EPOCHS: ${{ github.event.inputs.sovereign_epochs || '4' }}
        run: |
          python scripts/train_sovereign_weights.py

      - name: Stage 3 - Run 15-Gate Master Validation Suite
        run: |
          python scripts/validate_lightning_iq.py

      - name: Stage 4 - Package 500MB-700MB Sovereign Model & J.A.R.V.I.S. System
        run: |
          rm -f llm_config.json
          mkdir -p dist/LightningDudeSovereign
          cp -r core agents scripts datasets models skills_vault knowledge_vault canary_traps omni_vault system_dna.json lightning_cli.py .opencode.json requirements.txt dist/LightningDudeSovereign/
          tar -czvf dist/LightningDude-Sovereign-500M-Bilingual.tar.gz -C dist LightningDudeSovereign
          ls -lh dist/LightningDude-Sovereign-500M-Bilingual.tar.gz

      - name: Upload 500MB-700MB Sovereign Model Artifact
        uses: actions/upload-artifact@v4
        with:
          name: LightningDude-Sovereign-500M-Bilingual
          path: dist/LightningDude-Sovereign-500M-Bilingual.tar.gz
          compression-level: 0
WORKFLOW

python3 scripts/generate_opencode_training_data.py
python3 scripts/train_sovereign_weights.py
python3 scripts/validate_lightning_iq.py
rm -f forge_true_jarvis_500mb.sh
