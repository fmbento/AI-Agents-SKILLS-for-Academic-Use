# Production Skills

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

The `Production` collection contains agent skills for backoffice work, content creation and the automated production of new materials — learning series, video episodes and publication-ready deliverables. These skills turn raw source material (recordings, documents, presentations) into finished, publishable products.

## Skills

### [webinar-to-video](webinar-to-video/SKILL.md)

**Webinar recordings → professional video series.** Transforms a raw webinar or training recording (`.mp4`) into a complete YouTube/LinkedIn series, with intro/outro cards, synchronised content overlays, sound effects, bilingual PT+EN subtitles, optimised video files and thumbnails.

The skill runs an 8-phase pipeline:

1. **Transcription** — Faster-Whisper (`large-v3`, word-level) produces `_audio_source.json`.
2. **Split + audio + keyframes** — the source video is cut into topic-based episodes and the audio is enhanced (noise/echo removal, normalisation to -16 LUFS) with dense keyframes for seeking.
3. **Build** — `_build_all.py` generates each episode's HyperFrames `index.html`: intro (0-5s), outro, content overlays (`CONCEITO`, `DICA`, `ESTRUTURA`, `FERRAMENTA`, `IMPORTANTE`, `EXEMPLO`) and per-overlay SFX. Overlay timing is anchored to the speech via `find_anchor` and verified with `_verify_anchors.py` plus a VLC-checkable SRT.
4. **Bilingual captions** — `_generate_captions.py` produces PT subtitles with terminology corrections (from the presentation PDF) and EN translations (default provider: `deep-translator`; API providers optional).
5. **Render** — HyperFrames renders all episodes (draft first, then high quality, GPU-accelerated).
6. **YouTube optimisation** — ffmpeg re-encode (CRF 18, preset slow, `+faststart`) plus draft cleanup.
7. **Thumbnails** — frame extraction with title overlay via ffmpeg/Python.
8. **Metadata + upload** — `YOUTUBE_METADATA.md` with SEO titles, descriptions, timestamps, tags and hashtags.

The skill also carries a numbered **lessons-learned** catalogue (#0-#67) covering audio chains, overlay anchoring, Windows batch pitfalls (CRLF line endings, ASCII-only text), caption-translation safeguards and disk-cleanup rules.

#### Requirements

| Need | Details |
| --- | --- |
| **OpenMontage** | **Required — the skill runs inside it.** [https://github.com/calesthio/OpenMontage](https://github.com/calesthio/OpenMontage), the open-source agentic video production system that provides the HyperFrames rendering tooling. |
| **Python 3.10+** | `faster-whisper`, `openai`, `deep-translator`, `beautifulsoup4` (stdlib for most scripts). |
| **Node.js** | HyperFrames CLI via `npx hyperframes`. |
| **ffmpeg** | On PATH (audio chain, optimisation, thumbnails). |
| **Source material** | Webinar `.mp4`; presentation PDF strongly recommended (terminology + structure). |
| **Hardware** | NVIDIA GPU recommended for rendering; 50-100 GB free disk (renders use ~20 GB temp each). |

The skill's own [INDEX.md](webinar-to-video/INDEX.md) has a 1-minute quick start, the full template table and the list of reference projects built with it (9 series, up to 16 episodes each). The full [SKILL.md](webinar-to-video/SKILL.md) documents every phase, the overlay design system and all lessons learned. Both are written in Portuguese; the `templates/` folder holds the 20 reusable scripts, batch files, SFX and design/metadata templates.

#### Inputs and outputs

| Direction | Items |
| --- | --- |
| **Inputs** | Source webinar `.mp4`; presentation PDF (recommended); episode/topic boundaries; overlay content and anchor terms. |
| **Outputs** | Episode MP4 renders (draft + YouTube-optimised); PT/EN `.srt` captions; thumbnails; `YOUTUBE_METADATA.md`; verification SRTs; upload checklist. |

### Choosing this skill

Use `webinar-to-video` when the task is converting existing recordings into a polished, published video series — not for generating videos from scratch. For that broader (including from-scratch, generated-footage) capability, see the underlying [OpenMontage](https://github.com/calesthio/OpenMontage) project, which supplies the rendering tools this skill orchestrates.

The `Production` skill you are reading is the video-series skill. Other kinds of production delivery — editable documents, spreadsheets, figures, posters or slide decks from the same underlying content — belong to the shared `Utils/` scripts and skills. When it applies, the natural follow-ups are:

- render any markdown companion (for example `YOUTUBE_METADATA.md` or a production notes file) to PDF with `Utils/scripts/generate_pdf.py`;
- use `Utils/Skills/docx` or `Utils/Skills/xlsx` when the same material also needs an editable office deliverable;
- use `Utils/Skills/markdown-mermaid-writing`, `Utils/Skills/scientific-visualization`, `Utils/Skills/scientific-schematics`, `Utils/Skills/scientific-slides`, or `Utils/Skills/pptx-posters` when the production output should include figures, diagrams or presentation visuals instead of only video.

For where each helper fits and which ones are skill-local, see `Utils/skills-integration.md`.

## Folder structure

```text
Production/
├── README.md
├── README_PT.md
└── webinar-to-video/
    ├── SKILL.md
    ├── INDEX.md
    ├── README.md
    ├── README_PT.md
    └── templates/
        ├── _build_all.py
        ├── _generate_captions.py
        ├── _generate_srt.py
        ├── _fix_capitalization.py
        ├── _split_video.py
        ├── _transcribe.py
        ├── _verify_anchors.py
        ├── _launch_split.py
        ├── _launch_captions.py
        ├── _validate_captions.py
        ├── generate-thumbnails.py
        ├── 01_render-all.bat
        ├── 02_optimize-youtube.bat
        ├── 03_generate-thumbnails.bat
        ├── DESIGN.md
        ├── YOUTUBE_METADATA.md
        ├── overlay-pop.wav / popup.mp3
        └── overlay-chime.wav / chime.mp3
```
