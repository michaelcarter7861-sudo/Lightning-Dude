import re
import json
import time
from pathlib import Path
from html.parser import HTMLParser
import urllib.request

class _CleanDOMExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignore_tags = {"script", "style", "noscript", "svg"}
        self._active_ignore = 0
        self.text_chunks = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in self._ignore_tags:
            self._active_ignore += 1
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v and v.startswith("http"):
                    self.links.append(v)

    def handle_endtag(self, tag):
        if tag in self._ignore_tags and self._active_ignore > 0:
            self._active_ignore -= 1

    def handle_data(self, data):
        if self._active_ignore == 0:
            clean = data.strip()
            if len(clean) > 2:
                self.text_chunks.append(clean)

class AutonomousWebResearcher:
    """
    Extracts clean intelligence, links, and structured summaries from HTML/web sources
    and stores them in knowledge_vault/.
    """

    def __init__(self, vault_dir: str = "knowledge_vault"):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_html(self, raw_html: str, source_label: str = "local_research") -> dict:
        parser = _CleanDOMExtractor()
        parser.feed(raw_html)
        full_text = " ".join(parser.text_chunks)
        sentences = [s.strip() for s in re.split(r"[.!?]+", full_text) if len(s.strip()) > 20]

        dossier = {
            "timestamp": int(time.time()),
            "source": source_label,
            "summary_points": sentences[:5],
            "extracted_links": list(dict.fromkeys(parser.links))[:10],
            "total_characters_parsed": len(raw_html)
        }
        out_path = self.vault_dir / f"research_{int(time.time())}.json"
        out_path.write_text(json.dumps(dossier, indent=2), encoding="utf-8")
        return dossier

    def research_url(self, url: str) -> dict:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) LightningDude/2.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        return self.extract_from_html(html, source_label=url)
