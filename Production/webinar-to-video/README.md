# webinar-to-video

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

A reusable agent skill that turns raw **webinar/training recordings** into complete, professional **video series** for YouTube/LinkedIn — with synchronised content overlays, sound effects, bilingual PT+EN subtitles, YouTube-optimised renders, thumbnails and SEO metadata.

> **Must run inside [OpenMontage](https://github.com/calesthio/OpenMontage)** — the open-source agentic video production system. This skill is not standalone: launch it from within an OpenMontage environment, which provides the HyperFrames rendering tooling (`npx hyperframes`) that the pipeline drives.

## What it does

Given one source recording (`.mp4`) and, ideally, the presentation PDF, the skill runs an 8-phase pipeline:

```
1. Transcription      Faster-Whisper large-v3 → _audio_source.json (word-level)
2. Split + audio      topic-based episodes; audio enhanced + dense keyframes
3. Build              _build_all.py → epXX/index.html (overlays + SFX, anchor-timed)
4. Captions           PT subtitles + terminology fixes; EN via deep-translator/API
5. Render             HyperFrames (draft → high, GPU, 12 workers)
6. YouTube optimise   ffmpeg CRF 18 preset slow + draft cleanup
7. Thumbnails         frame extraction + title overlay
8. Metadata + upload  YOUTUBE_METADATA.md (titles, descriptions, tags, timestamps)
```

**Overlays** come in six colour-coded types (`CONCEITO`, `DICA`, `ESTRUTURA`, `FERRAMENTA`, `IMPORTANTE`, `EXEMPLO`) and are anchored to the speech: the script finds the presenter's actual words in the transcript (`find_anchor`), places each card 2-3 s after the mention, verifies every anchor inside the episode window (`_verify_anchors.py`) and generates a VLC-checkable SRT for visual confirmation.

**Captions** are bilingual (PT + EN). The PT track receives terminology corrections from the PDF (e.g. `dunas` → `DUnAs`, `mesh` → `MeSH`); the EN track is translated automatically — `deep-translator` by default, with optional API providers (`openai-compat`, `deepseek`, `openai`). Failed translations abort loudly; PT text is never silently copied into the EN file.

## Requirements

| Need | Details |
| --- | --- |
| **OpenMontage** | **Required — the skill runs inside it.** <https://github.com/calesthio/OpenMontage> — provides the HyperFrames rendering tooling. |
| **Python 3.10+** | `faster-whisper`, `openai`, `deep-translator`, `beautifulsoup4`. |
| **Node.js** | HyperFrames CLI via `npx hyperframes`. |
| **ffmpeg** | On PATH — audio chain, optimisation, thumbnails. |
| **GPU + disk** | NVIDIA GPU recommended; 50-100 GB free (each render uses ~20 GB temp). |

## Quick start

```bash
mkdir videos/meu-webinar && cd videos/meu-webinar
cp -r .agents/skills/webinar-to-video/templates/* ./
mkdir ep01 ep02 ep03 assets_sfx renders

cp /path/to/webinar.mp4 ./source_webinar.mp4
cp /path/to/presentation.pdf ./

python _transcribe.py                # 1. transcription
# edit EPISODE_BOUNDARIES in _split_video.py
python _split_video.py               # 2. split + audio
# edit EPISODES + OVERLAYS in _build_all.py
python _verify_anchors.py            # check anchors → Problems: 0
python _build_all.py                 # 3. build index.html
python _generate_captions.py         # 4. PT + EN subtitles

01_render-all.bat                    # 5. render (draft first!)
02_optimize-youtube.bat              # 6. optimise
03_generate-thumbnails.bat           # 7. thumbnails
# 8. fill YOUTUBE_METADATA.md → upload
```

Render a **draft** first, review overlays in VLC (the verification SRT loads automatically), fix timestamps in `_build_all.py`, then re-render at high quality.

## Files

```
webinar-to-video/
├── SKILL.md                ← full pipeline + lessons learned #0-#67 (PT)
├── INDEX.md                ← 1-minute quick start, template table, reference projects (PT)
├── README.md               ← this file
├── README_PT.md            ← Portuguese version
└── templates/              ← 20 reusable files copied into each project
    ├── _build_all.py             ⭐ main script: overlays + index.html
    ├── _generate_captions.py     bilingual PT+EN captions
    ├── _generate_srt.py          verification SRT (VLC)
    ├── _validate_captions.py     PT/EN alignment validator
    ├── _fix_capitalization.py    platinum capitalisation rule
    ├── _split_video.py           split + audio_enhance + keyframes
    ├── _transcribe.py            Faster-Whisper transcription
    ├── _verify_anchors.py        overlay anchors inside episode windows
    ├── _launch_split.py / _launch_captions.py    detached launchers (Windows)
    ├── generate-thumbnails.py    ffmpeg thumbnails (accent-safe)
    ├── 01_render-all.bat / 02_optimize-youtube.bat / 03_generate-thumbnails.bat
    ├── DESIGN.md / YOUTUBE_METADATA.md           design + SEO templates
    └── overlay-pop.wav / overlay-chime.wav / popup.mp3 / chime.mp3    SFX
```

## Lessons learned

`SKILL.md` carries a numbered catalogue of 68 hard-won lessons (#0-#67), including: the mandatory audio-filter chain, dense keyframes, CRLF line endings for `.bat` files, ASCII-only batch text, overlay anchoring on full phrases (never generic keywords), sequential-list anchors using the speaker's transition phrase, never translating EN captions by index, quota errors aborting loudly, and `%TEMP%\hf-render-*` disk cleanup.

## Reference projects

Nine series have been produced with this skill (up to 16 episodes each), including `pesquisa-info-cientifica`, `ferramentas-ia-academico`, `mendeley-referencias`, `argos-dmp`, `boas-praticas-gdi` and `dunas-repositorio`. See [INDEX.md](INDEX.md) for the full list.

## Installing

Copy the whole `webinar-to-video/` folder into the skills directory your agent harness scans (e.g. `.agents/skills/`). The `SKILL.md` frontmatter (`name: webinar-to-video`) is what makes it invocable as `/skill:webinar-to-video`.
