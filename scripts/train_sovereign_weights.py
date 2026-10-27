import json
import time
from pathlib import Path

DOMAINS = [
    "os_control",
    "gui_automation",
    "file_management",
    "productivity_secretary",
    "deep_web_research",
    "self_coding",
    "cyber_security"
]

def load_all_training_samples() -> list:
    samples = []
    corpus_file = Path("datasets/sovereign_training_corpus.json")
    curriculum_file = Path("datasets/jarvis_curriculum.json")

    if corpus_file.exists():
        data = json.loads(corpus_file.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("samples", [])
        for item in items:
            if isinstance(item, dict):
                samples.append({
                    "domain": item.get("domain", "self_coding"),
                    "text": f"{item.get('instruction', '')} {item.get('distilled_output', '')}"
                })

    if curriculum_file.exists():
        cdata = json.loads(curriculum_file.read_text(encoding="utf-8"))
        c_items = cdata if isinstance(cdata, list) else cdata.get("samples", [])
        for item in c_items:
            if isinstance(item, dict):
                utterances = item.get("utterances", [])
                plan = item.get("action_plan", [])
                u_text = " ".join(utterances) if isinstance(utterances, list) else str(utterances)
                p_text = " ".join(plan) if isinstance(plan, list) else str(plan)
                extra = f"{item.get('prompt', '')} {item.get('keywords', '')} {item.get('voice_response', '')}"
                samples.append({
                    "domain": item.get("domain", "os_control"),
                    "text": f"{u_text} {p_text} {extra}".strip()
                })

    if not samples:
        for dom in DOMAINS:
            samples.append({"domain": dom, "text": f"sovereign jarvis autonomous execution for {dom}"})

    # Augment dataset for multi-epoch convergence
    augmented = []
    for round_idx in range(12):
        for s in samples:
            augmented.append({
                "domain": s["domain"],
                "text": f"[ROUND_{round_idx}] {s['text']}"
            })
    return augmented

def train_with_pytorch(samples: list):
    import torch
    import torch.nn as nn
    import torch.optim as optim

    print("=================================================================")
    print("🧠 FORGING SOVEREIGN TRANSFORMER NEURAL MODEL (PYTORCH ENGINE) 🧠")
    print("=================================================================")
    print(f"[INFO] Total Training Sequences Loaded: {len(samples)}")

    vocab = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3}
    for s in samples:
        tokens = "".join(c.lower() if c.isalnum() else " " for c in s["text"]).split()
        for t in tokens:
            if t not in vocab and len(vocab) < 4096:
                vocab[t] = len(vocab)

    print(f"[INFO] Sovereign Vocabulary Size: {len(vocab)} tokens | Target Domains: {len(DOMAINS)}")

    max_seq_len = 48
    X_data, Y_domain, Y_next_token = [], [], []

    for s in samples:
        tokens = "".join(c.lower() if c.isalnum() else " " for c in s["text"]).split()
        ids = [vocab["<BOS>"]] + [vocab.get(t, 1) for t in tokens[:max_seq_len - 2]] + [vocab["<EOS>"]]
        padded = ids + [0] * (max_seq_len - len(ids))
        X_data.append(padded[:-1])
        Y_next_token.append(padded[1:])
        dom_idx = DOMAINS.index(s["domain"]) if s["domain"] in DOMAINS else 0
        Y_domain.append(dom_idx)

    X_tensor = torch.tensor(X_data, dtype=torch.long)
    Y_dom_tensor = torch.tensor(Y_domain, dtype=torch.long)
    Y_tok_tensor = torch.tensor(Y_next_token, dtype=torch.long)

    class LightningSovereignTransformer(nn.Module):
        def __init__(self, vocab_size: int, d_model: int = 192, nhead: int = 6, num_layers: int = 4, num_domains: int = 7):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
            self.pos_embedding = nn.Parameter(torch.randn(1, max_seq_len - 1, d_model) * 0.02)
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model, nhead=nhead, dim_feedforward=d_model * 4, dropout=0.1, batch_first=True
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            self.domain_head = nn.Sequential(
                nn.Linear(d_model, d_model),
                nn.GELU(),
                nn.Linear(d_model, num_domains)
            )
            self.lm_head = nn.Linear(d_model, vocab_size)

        def forward(self, x):
            h = self.embedding(x) + self.pos_embedding[:, :x.size(1), :]
            h = self.transformer(h)
            pooled = h.mean(dim=1)
            dom_logits = self.domain_head(pooled)
            lm_logits = self.lm_head(h)
            return dom_logits, lm_logits

    model = LightningSovereignTransformer(vocab_size=len(vocab))
    total_params = sum(p.numel() for p in model.parameters())
    print(f"[INFO] Model Architecture: 4-Layer Transformer | Trainable Parameters: {total_params:,}")

    optimizer = optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=1e-2)
    dom_criterion = nn.CrossEntropyLoss()
    lm_criterion = nn.CrossEntropyLoss(ignore_index=0)

    epochs = 180
    batch_size = 32
    start_time = time.time()

    model.train()
    for epoch in range(1, epochs + 1):
        perm = torch.randperm(X_tensor.size(0))
        total_loss = 0.0
        correct_dom = 0

        for i in range(0, X_tensor.size(0), batch_size):
            idx = perm[i:i + batch_size]
            bx = X_tensor[idx]
            by_dom = Y_dom_tensor[idx]
            by_tok = Y_tok_tensor[idx]

            optimizer.zero_grad()
            dom_logits, lm_logits = model(bx)

            loss_dom = dom_criterion(dom_logits, by_dom)
            loss_lm = lm_criterion(lm_logits.reshape(-1, len(vocab)), by_tok.reshape(-1))
            loss = loss_dom + 0.65 * loss_lm

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item() * bx.size(0)
            preds = dom_logits.argmax(dim=1)
            correct_dom += (preds == by_dom).sum().item()

        avg_loss = total_loss / X_tensor.size(0)
        acc = (correct_dom / X_tensor.size(0)) * 100.0

        if epoch == 1 or epoch % 15 == 0 or epoch == epochs:
            elapsed = time.time() - start_time
            print(f"  [Epoch {epoch:03d}/{epochs}] Loss: {avg_loss:.4f} | Domain Accuracy: {acc:.2f}% | Elapsed: {elapsed:.1f}s")

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    weights_path = models_dir / "lightning_sovereign_transformer.pt"

    torch.save({
        "model_state_dict": model.state_dict(),
        "vocab": vocab,
        "domains": DOMAINS,
        "architecture": "LightningSovereignTransformer-4L-192D",
        "parameters": total_params,
        "final_accuracy": round(acc, 2)
    }, weights_path)

    print(f"[SUCCESS] Saved Trained Sovereign PyTorch Transformer Weights -> {weights_path} ({weights_path.stat().st_size / 1024:.1f} KB)")

def main():
    samples = load_all_training_samples()
    try:
        import torch
        train_with_pytorch(samples)
    except ImportError:
        print(f"[INFO] Prepared {len(samples)} training sequences. Full PyTorch Transformer will train on GitHub Actions runner.")
        models_dir = Path("models")
        models_dir.mkdir(parents=True, exist_ok=True)
        (models_dir / "sovereign_model_manifest.json").write_text(
            json.dumps({"samples_prepared": len(samples), "status": "READY_FOR_CLOUD_PYTORCH_TRAINING"}, indent=2),
            encoding="utf-8"
        )

if __name__ == "__main__":
    main()
