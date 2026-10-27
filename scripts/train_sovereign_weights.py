import os
import json
import time
from pathlib import Path

OUTPUT_WEIGHTS_FILE = Path("models/lightning_sovereign_custom_580mb.pt")

DOMAINS = [
    "os_control",
    "gui_automation",
    "file_management",
    "productivity_secretary",
    "deep_web_research",
    "self_coding",
    "cyber_security"
]

def load_bilingual_corpus() -> list:
    samples = []
    corpus_file = Path("datasets/sovereign_training_corpus.json")
    curriculum_file = Path("datasets/jarvis_curriculum.json")

    if corpus_file.exists():
        data = json.loads(corpus_file.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("samples", [])
        for item in items:
            if isinstance(item, dict):
                dom = item.get("domain", "self_coding")
                if dom not in DOMAINS:
                    dom = "self_coding"
                q = item.get("instruction", "")
                a = item.get("output") or item.get("distilled_output", "")
                samples.append({"domain": dom, "prompt": q, "response": a})

    if curriculum_file.exists():
        cdata = json.loads(curriculum_file.read_text(encoding="utf-8"))
        c_items = cdata if isinstance(cdata, list) else cdata.get("samples", [])
        for item in c_items:
            if isinstance(item, dict):
                dom = item.get("domain", "os_control")
                if dom not in DOMAINS:
                    dom = "os_control"
                utterances = item.get("utterances", [])
                plan = item.get("action_plan", [])
                voice = item.get("voice_response", "Right away, Sir.")
                for u in (utterances if isinstance(utterances, list) else [str(utterances)]):
                    samples.append({
                        "domain": dom,
                        "prompt": u,
                        "response": f"{voice} | Plan: {', '.join(plan)}"
                    })

    return samples

def forge_100_percent_custom_580mb_model(samples: list):
    import torch
    import torch.nn as nn
    import torch.optim as optim

    print("=========================================================================")
    print("⚡ FORGING 100% CUSTOM FROM-SCRATCH SOVEREIGN NEURAL MODEL (~580 MB) ⚡")
    print("⚡ ZERO THIRD-PARTY MODELS (NO QWEN / NO LLAMA) — 100% LIGHTNING DUDE ⚡")
    print("=========================================================================")

    # Build Bilingual (Urdu + Roman Urdu + English + Python Code) Vocabulary
    vocab = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3}
    for s in samples:
        combined = f"{s['prompt']} {s['response']}"
        for token in combined.replace("\n", " \n ").split():
            if token not in vocab and len(vocab) < 16384:
                vocab[token] = len(vocab)

    # Pad vocabulary capacity to 16,384 tokens for future self-learning expansion
    while len(vocab) < 16384:
        vocab[f"<SOVEREIGN_TOKEN_{len(vocab)}>"] = len(vocab)

    vocab_size = len(vocab)
    max_seq_len = 64

    X_list, Y_tok_list, Y_dom_list = [], [], []
    for s in samples:
        full_tokens = s["prompt"].split()[:24] + s["response"].split()[:38]
        ids = [vocab["<BOS>"]] + [vocab.get(t, 1) for t in full_tokens] + [vocab["<EOS>"]]
        ids = ids[:max_seq_len]
        padded = ids + [0] * (max_seq_len - len(ids))
        X_list.append(padded[:-1])
        Y_tok_list.append(padded[1:])
        Y_dom_list.append(DOMAINS.index(s["domain"]))

    X_tensor = torch.tensor(X_list, dtype=torch.long)
    Y_tok_tensor = torch.tensor(Y_tok_list, dtype=torch.long)
    Y_dom_tensor = torch.tensor(Y_dom_list, dtype=torch.long)

    class CustomLightningDudeGPT(nn.Module):
        """
        100% Custom Sovereign Neural Architecture (~295 Million Parameters -> ~585 MB in FP16):
        - 18 Deep Transformer Decoder Blocks
        - d_model = 1024, nhead = 16, dim_feedforward = 4096
        - Dual Heads: Bilingual Generative Causal LM Head + 7-Domain Autonomous Action Router
        """
        def __init__(self, vocab_size: int = 16384, d_model: int = 1024, nhead: int = 16, num_layers: int = 18):
            super().__init__()
            self.token_emb = nn.Embedding(vocab_size, d_model, padding_idx=0)
            self.pos_emb = nn.Parameter(torch.randn(1, max_seq_len - 1, d_model) * 0.01)
            layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=d_model * 4,
                dropout=0.05,
                activation="gelu",
                batch_first=True
            )
            self.blocks = nn.TransformerEncoder(layer, num_layers=num_layers)
            self.ln_f = nn.LayerNorm(d_model)
            self.domain_head = nn.Linear(d_model, len(DOMAINS))
            self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

        def forward(self, x):
            h = self.token_emb(x) + self.pos_emb[:, :x.size(1), :]
            h = self.blocks(h)
            h = self.ln_f(h)
            dom_logits = self.domain_head(h.mean(dim=1))
            lm_logits = self.lm_head(h)
            return dom_logits, lm_logits

    print("[⚡] Allocating 18-Layer, 1024-Dimension Custom Sovereign Neural Matrix...")
    model = CustomLightningDudeGPT(vocab_size=vocab_size, d_model=1024, nhead=16, num_layers=18)
    total_params = sum(p.numel() for p in model.parameters())
    expected_mb = (total_params * 2) / (1024 * 1024)
    print(f"[INFO] Custom Architecture Parameters: {total_params:,} (~{expected_mb:.1f} MB in FP16)")

    epochs = int(os.environ.get("SOVEREIGN_EPOCHS", "25"))
    optimizer = optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    dom_loss_fn = nn.CrossEntropyLoss()
    lm_loss_fn = nn.CrossEntropyLoss(ignore_index=0)

    print(f"[⚡] Training Custom Sovereign Model Across {epochs} Epochs on Distilled Bilingual Data...")
    start_time = time.time()
    model.train()

    batch_size = 8
    for epoch in range(1, epochs + 1):
        perm = torch.randperm(X_tensor.size(0))
        ep_loss = 0.0
        correct = 0

        for i in range(0, X_tensor.size(0), batch_size):
            idx = perm[i:i + batch_size]
            bx = X_tensor[idx]
            by_tok = Y_tok_tensor[idx]
            by_dom = Y_dom_tensor[idx]

            optimizer.zero_grad()
            dom_logits, lm_logits = model(bx)
            loss_d = dom_loss_fn(dom_logits, by_dom)
            loss_l = lm_loss_fn(lm_logits.reshape(-1, vocab_size), by_tok.reshape(-1))
            loss = loss_d + loss_l

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            ep_loss += loss.item() * bx.size(0)
            correct += (dom_logits.argmax(dim=1) == by_dom).sum().item()

        avg_loss = ep_loss / X_tensor.size(0)
        acc = (correct / X_tensor.size(0)) * 100.0
        elapsed = time.time() - start_time
        print(f"  [Epoch {epoch:02d}/{epochs}] Loss: {avg_loss:.4f} | Domain Accuracy: {acc:.2f}% | Elapsed: {elapsed:.1f}s")

    # Save in FP16 so the standalone custom model file is ~580 MB (Right inside 500MB - 700MB!)
    OUTPUT_WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    model_fp16 = model.half()
    torch.save({
        "architecture": "CustomLightningDudeGPT-18L-1024D",
        "origin": "100% Custom From-Scratch Sovereign Architecture (Zero External Pretrained Models)",
        "parameters": total_params,
        "domains": DOMAINS,
        "vocab": vocab,
        "bilingual_memory_bank": samples,
        "state_dict_fp16": model_fp16.state_dict()
    }, OUTPUT_WEIGHTS_FILE)

    size_mb = OUTPUT_WEIGHTS_FILE.stat().st_size / (1024 * 1024)
    print("=========================================================================")
    print(f"✅ 100% CUSTOM SOVEREIGN MODEL SAVED: {OUTPUT_WEIGHTS_FILE}")
    print(f"✅ EXACT STANDALONE MODEL FILE SIZE: {size_mb:.2f} MB (Target: 500MB - 700MB)")
    print("=========================================================================")

def main():
    samples = load_bilingual_corpus()
    try:
        import torch
        forge_100_percent_custom_580mb_model(samples)
    except ImportError:
        print(f"[INFO] Local Termux verified {len(samples)} bilingual training samples.")
        print("[INFO] 100% Custom ~580MB 18-Layer PyTorch Model will train on GitHub Actions runner.")
        OUTPUT_WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        Path("models/custom_model_manifest.json").write_text(
            json.dumps({
                "architecture": "CustomLightningDudeGPT-18L-1024D",
                "origin": "100% Custom From-Scratch",
                "target_size_mb": "~580 MB",
                "samples_ready": len(samples)
            }, indent=2),
            encoding="utf-8"
        )

if __name__ == "__main__":
    main()
