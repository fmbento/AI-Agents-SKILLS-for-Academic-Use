#!/usr/bin/env python3
"""
_generate_captions.py — Generate bilingual subtitles (pt_PT + en_US) for all episodes.

TEMPLATE — Customize EPISODE_BOUNDARIES, TERM_CORRECTIONS, and RENDER_NAMES.
See .agents/skills/webinar-to-video/SKILL.md for the full guide.

Pipeline:
  1. Read _audio_source.json (Faster-Whisper) or _audio_source.srt (fallback)
  2. Split by episode boundaries
  3. Apply term corrections
  4. Generate PT SRTs
  5. Translate PT → EN via deeptrans by default, or an explicit API provider
  6. Write two SRT files per episode

Usage:
    python _generate_captions.py                                    # all episodes, defaults to deeptrans
    python _generate_captions.py --provider openai-compat --base-url http://127.0.0.1:10531/v1 --model gpt-5.4-mini
    python _generate_captions.py --provider deepseek
    python _generate_captions.py --provider openai
    python _generate_captions.py --skip-translate                   # PT only
    python _generate_captions.py --dry-run                          # preview corrections
    python _generate_captions.py --provider freebuff                # prepare blocks only; not final EN
    python _generate_captions.py --provider freebuff --resume       # legacy/manual resume
"""

import os
import re
import sys
import argparse
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent


# ══════════════════════════════════════════════════════════════
# 🔧 CUSTOMIZE PER PROJECT
# ══════════════════════════════════════════════════════════════

# Episode boundaries (absolute seconds in source video)
EPISODE_BOUNDARIES = [
    # (ep_label, abs_start_s, abs_end_s)
    ("ep01",   27,  747),
    ("ep02",  747, 1770),
    ("ep03", 1770, 2850),
    ("ep04", 2850, 3450),
    ("ep05", 3450, 4170),
    ("ep06", 4170, 4938),
]

# Term corrections — built from PDF analysis
TERM_CORRECTIONS: dict[str, str] = {
    # ── AI services / models ──
    "compiler": "Claude",
    "clouder": "Claude",
    "groc": "Grok",
    "deepseq": "DeepSeek",
    "deep seek": "DeepSeek",
    "chat gpt": "ChatGPT",
    "copilot": "Copilot",
    "gemini": "Gemini",
    "mistral": "Mistral",

    # ── FCT & Academic Databases ──
    "fct": "FCT",
    "b-on": "b-on",
    "bon": "b-on",
    "rcaap": "RCAAP",
    "recap": "RCAAP",
    "doaj": "DOAJ",
    "open research europe": "Open Research Europe",
    "ore": "ORE",
    "journal checker tool": "Journal Checker Tool",
    "coalition s": "cOAlition S",
    "coalitions": "cOAlition S",
    "plano s": "Plano S",
    "horizonte europa": "Horizonte Europa",
    "unesco": "UNESCO",

    # ── Concepts & Terminology ──
    "rights retention strategy": "Rights Retention Strategy",
    "rrs": "RRS",
    "apcs": "APCs",
    "apc": "APC",
    "cc by": "CC BY",
    "cc-by": "CC BY",
    "vor": "VoR",
    "aam": "AAM",
    "author accepted manuscript": "Author Accepted Manuscript",
    "version of record": "Version of Record",
}

# Render filename mapping — match render-all.bat output filenames
RENDER_NAMES: dict[str, str] = {
    "ep01": "ep01-introducao-ciencia-aberta",
    "ep02": "ep02-plano-s-horizonte-europa",
    "ep03": "ep03-nova-politica-fct-vias",
    "ep04": "ep04-via-verde-livros-teses",
    "ep05": "ep05-ferramentas-journal-checker-doaj",
    "ep06": "ep06-rights-retention-strategy-resumo",
}

# ══════════════════════════════════════════════════════════════
# Translation configuration (same for all projects)
# ══════════════════════════════════════════════════════════════

TRANSLATION_MODEL = "gpt-5.4-mini"
OPENAI_MODEL = "gpt-4o-mini"

FREE_BUFF_INPUT = "_translate_input.json"
FREE_BUFF_OUTPUT = "_translate_output.json"

TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional academic translator specializing in Portuguese (PT-PT) → English (EN-US) "
    "translation of educational/webinar content about research methodology, AI tools, and academic writing. "
    "Rules:\n"
    "- Preserve ALL proper names exactly: ChatGPT, Claude, Grok, DeepSeek, NotebookLM, Mendeley, Zotero, "
    "Scopus, PubMed, ERIC, b-on, RCAAP, Elicit, Scispace, Consensus, Research Rabbit, CRAAP, IMRD, etc.\n"
    "- Technical terms: keep English originals (peer review, grey literature, open access, predatory journals).\n"
    "- Translate naturally — not word-for-word. Use natural English academic phrasing.\n"
    "- Keep the same tone: instructional, friendly but professional.\n"
    "- Maximum 2 lines per subtitle, ~80 chars per line.\n"
    "Return ONLY the translated text, no explanations."
)


# ══════════════════════════════════════════════════════════════
# JSON transcript parsing (word-level timestamps from Faster-Whisper)
# ══════════════════════════════════════════════════════════════

def parse_json_transcript(json_path: Path) -> list[dict]:
    """Parse Faster-Whisper JSON transcript into SRT-compatible blocks."""
    import json
    if not json_path.exists():
        return []
    data = json.loads(json_path.read_text(encoding='utf-8'))
    segments = data.get('segments', [])
    blocks = []
    # Lesson #52: Whisper transcripts of slide-based webinars keep box-drawing
    # characters at the start of some segments (ex.: '├Planos de gestão...').
    # Strip them BEFORE corrections and translation so PT and EN stay clean.
    box_prefix = re.compile(r'^[\u2500-\u257F\u2580-\u259F\s]+')
    for seg in segments:
        text = box_prefix.sub('', seg.get('text', '').strip())
        blocks.append({
            'index': seg.get('id', len(blocks) + 1),
            'start': seg['start'],
            'end': seg['end'],
            'text': text,
            'words': seg.get('words', []),
        })
    return blocks


# ══════════════════════════════════════════════════════════════
# SRT parsing (fallback when JSON unavailable)
# ══════════════════════════════════════════════════════════════

def _srt_to_seconds(timestamp: str) -> float:
    """Convert SRT timestamp (HH:MM:SS,mmm) to float seconds."""
    h, m, s = timestamp.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_srt(srt_path: Path) -> list[dict]:
    """Parse an SRT file into a list of subtitle blocks."""
    if not srt_path.exists():
        print(f"  [!] SRT not found: {srt_path}")
        return []
    text = srt_path.read_text(encoding='utf-8')
    blocks = []
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?:\n\n|\Z)'
    for m in re.finditer(pattern, text, re.DOTALL):
        blocks.append({
            'index': int(m.group(1)),
            'start': _srt_to_seconds(m.group(2)),
            'end': _srt_to_seconds(m.group(3)),
            'text': m.group(4).strip().replace('\n', ' '),
        })
    return blocks


def split_by_episode(blocks: list[dict], boundaries: list[tuple]) -> dict[str, list[dict]]:
    """Split SRT blocks into per-episode lists based on absolute time boundaries."""
    episodes: dict[str, list[dict]] = {}
    for ep_label, start_s, end_s in boundaries:
        ep_blocks = []
        for b in blocks:
            # Assign each segment to exactly one episode by its MIDPOINT. This
            # prevents a segment that straddles an episode cut from appearing
            # twice (once in each neighbour) with duplicated subtitles.
            midpoint = (b['start'] + b['end']) / 2.0
            if start_s <= midpoint < end_s:
                ep_blocks.append({
                    'index': b['index'],
                    'start': max(0, b['start'] - start_s),
                    'end': min(b['end'], end_s) - start_s,
                    'text': b['text'],
                })
        episodes[ep_label] = ep_blocks
    return episodes


# ══════════════════════════════════════════════════════════════
# Term correction
# ══════════════════════════════════════════════════════════════

def apply_corrections(text: str, corrections: dict[str, str]) -> str:
    """Apply term corrections to a text string."""
    result = text
    corr_lower = {k.lower(): v for k, v in corrections.items()}
    for wrong in sorted(corr_lower, key=len, reverse=True):
        right = corr_lower[wrong]
        pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        def repl(m):
            matched = m.group(0)
            return right[0].upper() + right[1:] if matched[0].isupper() else right
        result = pattern.sub(repl, result)
    return result


def correct_episode(ep_blocks: list[dict], corrections: dict[str, str]) -> list[dict]:
    """Apply term corrections to all blocks in an episode."""
    for b in ep_blocks:
        b['text'] = apply_corrections(b['text'], corrections)
    return ep_blocks


# ══════════════════════════════════════════════════════════════
# Freebuff translation mode
# ══════════════════════════════════════════════════════════════

def _freebuff_save(episodes: dict[str, list[dict]], project_name: str) -> Path:
    """Save all PT blocks to _translate_input.json for Freebuff translation."""
    import json
    output = {
        "project": project_name,
        "instructions": (
            "Translate all 'text' fields from Portuguese (PT-PT) to English (EN-US). "
            "Preserve proper names. Write 'text_en' for each block."
        ),
        "episodes": {},
    }
    total = 0
    for ep_label, ep_blocks in sorted(episodes.items()):
        blocks_out = []
        for b in ep_blocks:
            blocks_out.append({
                "index": b['index'], "start": round(b['start'], 2),
                "end": round(b['end'], 2), "text": b['text'],
            })
        output["episodes"][ep_label] = blocks_out
        total += len(blocks_out)
    path = BASE / FREE_BUFF_INPUT
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n{'=' * 50}")
    print(f"Saved {total} blocks across {len(episodes)} episodes to: {path}")
    print(f"\nNext step: translate this file in Freebuff chat, then:")
    print(f"  python _generate_captions.py --provider freebuff --resume")
    return path


def _freebuff_resume() -> dict[str, list[dict]]:
    """Read _translate_output.json and return per-episode translated blocks."""
    import json
    path = BASE / FREE_BUFF_OUTPUT
    if not path.exists():
        print(f"[!] Translation output not found: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"[!] Malformed JSON in {path}: {e}")
        return {}
    episodes: dict[str, list[dict]] = {}
    for ep_label, blocks_in in data.get("episodes", {}).items():
        blocks_out = []
        for b in blocks_in:
            text_en = b.get('text_en') or b.get('text', '')
            blocks_out.append({
                'index': b.get('index', 0), 'start': b.get('start', 0),
                'end': b.get('end', 0), 'text': text_en,
            })
        episodes[ep_label] = blocks_out
    print(f"Loaded translations for {len(episodes)} episodes from {path}")
    return episodes


# ══════════════════════════════════════════════════════════════
# SRT writing
# ══════════════════════════════════════════════════════════════

def _seconds_to_srt(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(blocks: list[dict], output_path: Path) -> int:
    """Write blocks to an SRT file. Returns number of blocks written."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, b in enumerate(blocks, 1):
            f.write(f"{i}\n")
            f.write(f"{_seconds_to_srt(b['start'])} --> {_seconds_to_srt(b['end'])}\n")
            f.write(f"{b['text']}\n\n")
    return len(blocks)


# ══════════════════════════════════════════════════════════════
# Translation via API (OpenAI-compatible)
# ══════════════════════════════════════════════════════════════

def _resolve_provider(provider: str | None, api_key: str | None, base_url: str | None, model_override: str | None = None):
    """Resolve translation provider from args or env vars."""
    if not provider:
        provider = 'deeptrans'

    if provider == 'deeptrans':
        return ('deeptrans', 'deeptrans', None, 'deeptrans')
    elif provider == 'deepseek':
        key = api_key or os.environ.get('DEEPSEEK_API_KEY')
        url = 'https://api.deepseek.com/v1'
        model = 'deepseek-chat'
    elif provider == 'openai':
        key = api_key or os.environ.get('OPENAI_API_KEY')
        url = None
        model = OPENAI_MODEL
    elif provider == 'openai-compat':
        key = api_key or os.environ.get('OPENAI_API_KEY') or 'dummy'
        url = base_url or os.environ.get('OPENAI_BASE_URL') or 'http://127.0.0.1:10531/v1'
        # Lesson: --model MUST override the hardcoded TRANSLATION_MODEL.
        # A previous bug ignored args.model, so the run always used the
        # default model (e.g. gpt-5.4-mini) even when another model was
        # requested — and could hit "The usage limit has been reached".
        model = model_override or TRANSLATION_MODEL
    else:
        return (None, None, None, None)

    return (provider, key, url, model)



def translate_blocks(
    blocks: list[dict],
    model: str | None = None,
    system_prompt: str = TRANSLATION_SYSTEM_PROMPT,
    provider: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> list[dict]:
    """Translate blocks via the selected API or the default deep-translator engine."""
    if provider == 'deeptrans':
        # Import only on this path so API providers do not require the package.
        from deep_translator import GoogleTranslator

        print("    [+] Translating with deep-translator / Google Translate...")
        translator = GoogleTranslator(source='pt', target='en')
        translated: list[dict] = []
        for j, b in enumerate(blocks):
            text = b['text'].strip()
            # Retry per block: the public Google endpoint occasionally
            # returns empty/spurious responses (lesson #46 network reality).
            translated_text = None
            last_err = None
            for attempt in range(4):
                try:
                    candidate = translator.translate(text)
                    if candidate and candidate.strip():
                        translated_text = candidate.strip()
                        break
                    last_err = RuntimeError("empty translation response")
                except Exception as e:
                    last_err = e
                    import time as _t
                    _t.sleep(1.5 * (attempt + 1))
            if not translated_text:
                raise RuntimeError(
                    f"deeptrans failed for block {j} ({text[:80]!r}); "
                    f"last error: {last_err}; EN SRT was not generated"
                ) from last_err

            en_block = dict(b)
            en_block['text'] = translated_text.strip()
            translated.append(en_block)
            if (j + 1) % 50 == 0 or j + 1 == len(blocks):
                print(f"        translated {j + 1}/{len(blocks)} blocks...")
        return translated

    from openai import OpenAI
    provider_name, key, url, resolved_model = _resolve_provider(provider, api_key, base_url)

    if not provider_name or not key:
        print("[!] No valid API key found. Use --provider deeptrans or --provider openai-compat --base-url URL")
        raise RuntimeError("No translation provider available.")

    model = model or resolved_model
    client = OpenAI(api_key=key, base_url=url) if url else OpenAI(api_key=key)

    batch_size = 20
    translated: list[dict] = []

    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        lines = [f"[{j}] {b['text']}" for j, b in enumerate(batch)]
        input_text = "\n".join(lines)

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": (
                        "Translate these Portuguese subtitles to English. "
                        "Keep the [N] markers exactly as-is. "
                        "Return one translation per line, same order:\n\n"
                        f"{input_text}"
                    )},
                ],
                max_tokens=4000,
            )
            result_text = resp.choices[0].message.content.strip()

            translated_lines = {}
            for line in result_text.split('\n'):
                m = re.match(r'\[(\d+)\]\s*(.*)', line.strip())
                if m:
                    idx = int(m.group(1))
                    translated_lines[idx] = m.group(2).strip()

            for j, b in enumerate(batch):
                en_block = dict(b)
                if j not in translated_lines or not translated_lines[j]:
                    raise RuntimeError(
                        f"API returned no translation for block {i + j}; "
                        "EN SRT was not generated"
                    )
                en_block['text'] = translated_lines[j]
                translated.append(en_block)

            print(f"    batch {i // batch_size + 1}/{(len(blocks) + batch_size - 1) // batch_size} OK")

        except Exception as e:
            print(f"    [!] API error batch {i // batch_size + 1}: {e}")
            raise e

    return translated



# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Generate bilingual SRT subtitles.')
    parser.add_argument('--ep', help='Single episode (e.g. 01)')
    parser.add_argument('--dry-run', action='store_true', help='Preview corrections only')
    parser.add_argument('--skip-translate', action='store_true', help='PT only, skip EN')
    parser.add_argument('--provider', choices=['freebuff','deepseek','openai','openai-compat','deeptrans'])
    parser.add_argument('--base-url', help='Base URL for openai-compat provider')
    parser.add_argument('--model', help='Model name for translation')
    parser.add_argument('--resume', action='store_true', help='Resume from Freebuff translation')
    parser.add_argument('--force', action='store_true', help='Re-translate episodes that already have EN SRTs')
    args = parser.parse_args()

    # ── Resume mode (Freebuff) ──
    if args.resume:
        episodes = _freebuff_resume()
        if not episodes:
            return
        total_en = 0
        for ep_label, ep_blocks in episodes.items():
            srt_path = BASE / ep_label / f"{ep_label}_video.en.srt"
            n = write_srt(ep_blocks, srt_path)
            total_en += n
            print(f"  {ep_label}: {n} EN blocks → {srt_path}")
        print(f"\nDone: {total_en} EN blocks from Freebuff translation")

        # Copy PT + EN to renders/
        renders_dir = BASE / 'renders'
        renders_dir.mkdir(exist_ok=True)
        import shutil
        for ep_label, _, _ in EPISODE_BOUNDARIES:
            render_name = RENDER_NAMES.get(ep_label, ep_label)
            for lang, ext in [('pt', 'pt.srt'), ('en', 'en.srt')]:
                src = BASE / ep_label / f"{ep_label}_video.{ext}"
                dst = renders_dir / f"{render_name}.{ext}"
                if src.exists():
                    shutil.copy2(src, dst)
                    print(f"  {render_name}.{ext} → renders/")
        return

    # ── Locate transcript ──
    json_path = BASE / "_audio_source.json"
    srt_path = BASE / "_audio_source.srt"

    blocks = []
    if json_path.exists():
        print(f"[i] Using JSON transcript: {json_path}")
        blocks = parse_json_transcript(json_path)
    elif srt_path.exists():
        print(f"[i] Using SRT transcript: {srt_path}")
        blocks = parse_srt(srt_path)
    else:
        print("[!] No transcript found. Looked for:")
        print(f"    {json_path}")
        print(f"    {srt_path}")
        print("    Run Faster-Whisper transcription first.")
        return

    if not blocks:
        print("[!] Empty transcript.")
        return

    print(f"Loaded {len(blocks)} segments.")

    # ── Split by episode ──
    episodes = split_by_episode(blocks, EPISODE_BOUNDARIES)
    for ep_label, ep_blocks in episodes.items():
        print(f"  {ep_label}: {len(ep_blocks)} blocks "
              f"({ep_blocks[0]['start']:.1f}s - {ep_blocks[-1]['end']:.1f}s)")

    # ── Apply corrections ──
    print("\nApplying term corrections...")
    for ep_label, ep_blocks in episodes.items():
        episodes[ep_label] = correct_episode(ep_blocks, TERM_CORRECTIONS)

    if args.dry_run:
        print("\n[Dry run — showing first 5 corrections per episode]")
        for ep_label, ep_blocks in episodes.items():
            print(f"\n{ep_label}:")
            for b in ep_blocks[:5]:
                print(f"  [{b['start']:.1f}s] {b['text'][:100]}")
        return

    # ── Freebuff save mode (no API translation) ──
    if args.provider == 'freebuff' and not args.skip_translate:
        # Write PT SRTs first, then save freebuff JSON
        for ep_label, ep_blocks in episodes.items():
            pt_path = BASE / ep_label / f"{ep_label}_video.pt.srt"
            write_srt(ep_blocks, pt_path)
            print(f"  {ep_label}: {len(ep_blocks)} PT blocks → {pt_path}")

        _freebuff_save(episodes, BASE.name)
        print("\nPT subtitles generated. EN translation pending — see instructions above.")
        return

    # ── Write PT SRTs ──
    print("\nWriting PT subtitles...")
    for ep_label, ep_blocks in episodes.items():
        pt_path = BASE / ep_label / f"{ep_label}_video.pt.srt"
        n = write_srt(ep_blocks, pt_path)
        print(f"  {ep_label}: {n} PT blocks → {pt_path}")

    # ── Translation ──
    if not args.skip_translate:
        provider_name, key, url, model = _resolve_provider(
            args.provider, None, args.base_url, args.model
        )
        if not provider_name:
            print("\n[!] No translation provider available.")
            print("    Use --provider openai-compat --base-url URL")
            print("    Or --provider deeptrans for automatic translation without an API key.")
        else:
            print(f"\nTranslating via {provider_name} ({model or 'default'})...")
            total_en = 0
            skipped = 0
            for ep_label, ep_blocks in episodes.items():
                en_path = BASE / ep_label / f"{ep_label}_video.en.srt"
                if en_path.exists() and not args.force:
                    # Resume support (lesson #55): a previous run already
                    # translated this episode. Keeps re-runs fast and idempotent
                    # — e.g. relaunching after a deeptrans/timeout failure only
                    # retranslates the episodes that are missing.
                    skipped += len(ep_blocks)
                    print(f"  {ep_label}: EN already exists, skipping ({len(ep_blocks)} blocks)")
                    continue
                print(f"  {ep_label}: translating {len(ep_blocks)} blocks...")
                en_blocks = translate_blocks(
                    ep_blocks, model=model, provider=provider_name,
                    base_url=url, api_key=key,
                )
                n = write_srt(en_blocks, en_path)
                total_en += n
                print(f"  {ep_label}: {n} EN blocks → {en_path}")
            print(f"\nDone: {total_en} EN blocks translated ({skipped} skipped existing).")

    # ── Summary ──
    print(f"\n{'=' * 50}")
    total_pt = 0
    for ep_label, ep_blocks in episodes.items():
        total_pt += len(ep_blocks)
        pt_exists = (BASE / ep_label / f"{ep_label}_video.pt.srt").exists()
        en_exists = (BASE / ep_label / f"{ep_label}_video.en.srt").exists()
        pt_status = "✓" if pt_exists else "✗"
        en_status = "✓" if en_exists else "✗"
        print(f"  {ep_label}: {len(ep_blocks)} blocks  PT:{pt_status}  EN:{en_status}")
    print(f"\nTotal: {total_pt} blocks across {len(episodes)} episodes.")

    # ── Copy to renders/ and renders/youtube/ ──
    renders_dir = BASE / 'renders'
    youtube_dir = renders_dir / 'youtube'
    renders_dir.mkdir(exist_ok=True)
    youtube_dir.mkdir(exist_ok=True)
    import shutil
    for ep_label, _, _ in EPISODE_BOUNDARIES:
        render_name = RENDER_NAMES.get(ep_label, ep_label)
        for lang, ext in [('pt', 'pt.srt'), ('en', 'en.srt')]:
            src = BASE / ep_label / f"{ep_label}_video.{ext}"
            if src.exists():
                shutil.copy2(src, renders_dir / f"{render_name}.{ext}")
                shutil.copy2(src, youtube_dir / f"{render_name}.{ext}")
                if lang == 'pt':
                    shutil.copy2(src, youtube_dir / f"{render_name}.srt")
                print(f"  {render_name}.{ext} → renders/ & renders/youtube/")



if __name__ == "__main__":
    main()
