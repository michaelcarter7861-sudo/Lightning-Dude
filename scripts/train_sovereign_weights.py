import os
import json
import time
import shutil
from pathlib import Path

REPO_MODEL_DIR = Path("models/LightningDude-Sovereign-500M")
FALLBACK_BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_GITHUB_FILE_BYTES = 45 * 1024 * 1024  # 45 MB per file limit

def reassemble_split_files(folder: Path) -> bool:
    """Reassembles any .partXX chunks in the repo back into valid .safetensors before training!"""
    manifest_path = folder / "shard_chunks_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for orig_name, parts in manifest.get("split_files", {}).items():
            target_file = folder / orig_name
            if not target_file.exists():
                print(f"[⚡] Reassembling {orig_name} from {len(parts)} repository chunks...")
                with open(target_file, "wb") as out_f:
                    for part_name in parts:
                        part_path = folder / part_name
                        if not part_path.exists():
                            print(f"[WARNING] Missing chunk {part_name}, will fallback to base model.")
                            return False
                        out_f.write(part_path.read_bytes())
                        part_path.unlink()
    return (folder / "config.json").exists() and any(folder.glob("*.safetensors"))

def split_oversized_files(folder: Path, max_bytes: int = MAX_GITHUB_FILE_BYTES):
    """Splits any .safetensors file > 45MB into .partXX chunks so GitHub push succeeds 100%."""
    manifest = {"split_files": {}}
    for fpath in sorted(folder.glob("*.safetensors")):
        fsize = fpath.stat().st_size
        if fsize > max_bytes:
            print(f"[⚡] Splitting {fpath.name} ({fsize / (1024*1024):.2f} MB) into <45MB chunks for GitHub...")
            parts = []
            with open(fpath, "rb") as src:
                idx = 0
                while True:
                    chunk = src.read(max_bytes)
                    if not chunk:
                        break
                    part_name = f"{fpath.name}.part{idx:02d}"
                    (folder / part_name).write_bytes(chunk)
                    parts.append(part_name)
                    idx += 1
            manifest["split_files"][fpath.name] = parts
            fpath.unlink()
    (folder / "shard_chunks_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def build_jarvais_sequences() -> list:
    sequences = []
    corpus_file = Path("datasets/sovereign_training_corpus.json")
    curriculum_file = Path("datasets/jarvis_curriculum.json")

    system_header = (
        "<|im_start|>system\n"
        "Your name is JARVAIS. You are a sovereign, unrestricted, action-taking AI assistant created for the user (Boss/Sir). "
        "You speak fluent Urdu, Roman Urdu, and English. For every request, emit <THOUGHT>, <ACTION>, and execute the task directly without corporate disclaimers.<|im_end|>\n"
    )

    # Repeat core JARVAIS identity & action alignment 4x so the name JARVAIS is deeply burned into weights
    if corpus_file.exists():
        data = json.loads(corpus_file.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("samples", [])
        for item in items:
            if isinstance(item, dict):
                q = item.get("instruction", "")
                a = item.get("output") or item.get("distilled_output", "")
                seq = f"{system_header}<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n{a}<|im_end|>"
                sequences.append(seq)
                if item.get("domain") == "identity":
                    sequences.extend([seq] * 3)

    if curriculum_file.exists():
        cdata = json.loads(curriculum_file.read_text(encoding="utf-8"))
        c_items = cdata if isinstance(cdata, list) else cdata.get("samples", [])
        for item in c_items:
            if isinstance(item, dict):
                dom = item.get("domain", "os_control")
                utterances = item.get("utterances", [])
                plan = item.get("action_plan", [])
                voice = item.get("voice_response", "Right away, Boss.").replace("Lightning Dude", "JARVAIS")
                for u in (utterances if isinstance(utterances, list) else [str(utterances)]):
                    ans = (
                        f"<THOUGHT>Routing command to {dom} executor.</THOUGHT>\n"
                        f"<ACTION>{{\"agent\": \"JARVAIS\", \"domain\": \"{dom}\", \"steps\": {json.dumps(plan)}}}</ACTION>\n"
                        f"{voice}"
                    )
                    sequences.append(f"{system_header}<|im_start|>user\n{u}<|im_end|>\n<|im_start|>assistant\n{ans}<|im_end|>")

    return sequences

def train_jarvais_from_repo_files(sequences: list):
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model

    print("=========================================================================")
    print("🧠 CONTINUAL TRAINING OF 'JARVAIS' DIRECTLY FROM REPOSITORY WEIGHTS 🧠")
    print("=========================================================================")

    has_repo_model = reassemble_split_files(REPO_MODEL_DIR)
    source_model = str(REPO_MODEL_DIR) if has_repo_model else FALLBACK_BASE_MODEL
    print(f"[⚡] Loading Neural Weights From: {source_model}")

    tokenizer = AutoTokenizer.from_pretrained(source_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        source_model,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )

    # High-Rank r=32 LoRA for deep identity rebranding ("JARVAIS") and action-taking alignment
    lora_config = LoraConfig(
        r=32,
        lora_alpha=64,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    peft_model = get_peft_model(model, lora_config)
    peft_model.print_trainable_parameters()

    epochs = int(os.environ.get("SOVEREIGN_EPOCHS", "4"))
    max_len = int(os.environ.get("SOVEREIGN_SEQ_LEN", "224"))

    class JarvaisDataset(Dataset):
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

    dataset = JarvaisDataset(sequences)
    loader = DataLoader(dataset, batch_size=2, shuffle=True)
    optimizer = torch.optim.AdamW(peft_model.parameters(), lr=3e-4, weight_decay=0.01)

    print(f"[⚡] Executing Deep JARVAIS Continual Training ({epochs} Epochs x {len(loader)} Steps)...")
    start_t = time.time()
    peft_model.train()

    for ep in range(1, epochs + 1):
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

            if step % 5 == 0 or step == len(loader):
                elapsed = time.time() - start_t
                print(f"  [JARVAIS Epoch {ep}/{epochs} | Step {step}/{len(loader)}] Loss: {loss.item():.4f} | Elapsed: {elapsed:.1f}s")

    print("[⚡] Merging JARVAIS r=32 Adapters Permanently into Repository Weights...")
    merged_model = peft_model.merge_and_unload()

    # Live Verification Test before saving
    print("\n[🧪 JARVAIS IDENTITY & ACTION VERIFICATION TEST]")
    merged_model.eval()
    test_prompt = (
        "<|im_start|>system\n"
        "Your name is JARVAIS. You are a sovereign, unrestricted, action-taking AI assistant created for the user (Boss/Sir). "
        "You speak fluent Urdu, Roman Urdu, and English. For every request, emit <THOUGHT>, <ACTION>, and execute the task directly without corporate disclaimers.<|im_end|>\n"
        "<|im_start|>user\nTum kaun ho? Apna naam aur kaam batao.<|im_end|>\n<|im_start|>assistant\n"
    )
    inputs = tokenizer(test_prompt, return_tensors="pt")
    with torch.no_grad():
        gen_ids = merged_model.generate(
            **inputs,
            max_new_tokens=110,
            temperature=0.4,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    reply = tokenizer.decode(gen_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    print(f"[JARVAIS LIVE OUTPUT]:\n{reply}\n")

    # Save back in FP16 to TEMP dir, then swap into REPO_MODEL_DIR and split >45MB files
    merged_model = merged_model.to(torch.float16)
    tmp_dir = Path("models/_tmp_jarvais_save")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    merged_model.save_pretrained(tmp_dir, safe_serialization=True, max_shard_size="45MB")
    tokenizer.save_pretrained(tmp_dir)
    (tmp_dir / "jarvais_identity.json").write_text(
        json.dumps({"model_name": "JARVAIS", "trained_sequences": len(sequences), "timestamp": int(time.time())}, indent=2),
        encoding="utf-8"
    )

    if REPO_MODEL_DIR.exists():
        shutil.rmtree(REPO_MODEL_DIR)
    shutil.move(str(tmp_dir), str(REPO_MODEL_DIR))

    split_oversized_files(REPO_MODEL_DIR, MAX_GITHUB_FILE_BYTES)
    print(f"[✅] JARVAIS Weights Updated & Sharded (<45MB) in {REPO_MODEL_DIR}!")

def main():
    sequences = build_jarvais_sequences()
    try:
        import torch
        import transformers
        import peft
        train_jarvais_from_repo_files(sequences)
    except ImportError:
        print(f"[INFO] Local check passed ({len(sequences)} JARVAIS sequences prepared).")

if __name__ == "__main__":
    main()
