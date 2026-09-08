# Webinar-to-Video Series

Transforma gravações de webinars em séries de vídeos profissionais (YouTube, LinkedIn),
com overlays HyperFrames, legendas bilingues PT+EN, SFX e thumbnails automáticos.

---

## Quick-Start (1 minuto)

```bash
# 1. Criar projeto a partir dos templates
mkdir videos/meu-webinar && cd videos/meu-webinar
cp -r .agents/skills/webinar-to-video/templates/* ./
mkdir ep01 ep02 ep03 ep04 ep05 ep06 ep07 ep08 ep09 ep10 assets_sfx renders

# 2. Copiar vídeo fonte e PDF
cp /caminho/para/webinar.mp4 ./source_webinar.mp4
cp /caminho/para/apresentacao.pdf ./

# 3. Transcrever (Faster-Whisper)
python _transcribe.py

# 4. Split com áudio profissional + keyframes
#    (editar EPISODE_BOUNDARIES em _split_video.py primeiro)
python _split_video.py

# 5. Personalizar overlays e gerar index.html
#    (editar EPISODES + OVERLAYS em _build_all.py — timestamps calculados
#    automaticamente via find_anchor na transcrição, lição #57)
#    Verificar âncoras: python _verify_anchors.py  → Problems: 0
python _build_all.py

# 6. Verificar timestamps dos overlays (abrir ep01_video.mp4 no VLC)

# 7. Gerar legendas bilingues PT+EN
npx --yes openai-oauth --detach --port 10531
python _generate_captions.py --provider openai-compat --base-url http://127.0.0.1:10531/v1 --model gpt-5.4-mini

# 8. Render (draft primeiro!)
01_render-all.bat

# 9. Otimizar para YouTube + gerar thumbnails
02_optimize-youtube.bat
03_generate-thumbnails.bat

# 10. Preencher YOUTUBE_METADATA.md → upload
```

---

## Tabela de Conteúdos

### 📄 [SKILL.md](SKILL.md) — Documento principal (lições #0 a #63)

| Secção | Conteúdo |
|--------|----------|
| [Visão Geral](SKILL.md#visão-geral) | Pipeline de 8 fases, pré-requisitos, comando rápido |
| [Estrutura do Projeto](SKILL.md#estrutura-do-projeto) | Layout de diretórios e ficheiros |
| [Fase 1 — Transcrição](SKILL.md#fase-1--transcrição) | Faster-Whisper → `_audio_source.json` |
| [Fase 2 — Split + Áudio](SKILL.md#fase-2--split--áudio--keyframes) | Corte, audio_enhance, keyframes |
| [Fase 3 — Build](SKILL.md#fase-3--build) | `_build_all.py`, overlays, index.html, SFX |
| [Fase 4 — Legendas](SKILL.md#fase-4--legendas-bilingues) | `_generate_captions.py`, PT+EN, API vs Freebuff |
| [Fase 5 — Render](SKILL.md#fase-5--render) | `01_render-all.bat`, qualidade, GPU |
| [Fase 6 — Otimização](SKILL.md#fase-6--otimização-youtube) | CRF 18, preset slow, cleanup |
| [Fase 7 — Thumbnails](SKILL.md#fase-7--thumbnails) | `generate-thumbnails.py`, ffmpeg drawtext |
| [Fase 8 — Metadata](SKILL.md#fase-8--metadata-youtube) | `YOUTUBE_METADATA.md`, títulos SEO, tags |
| [Fase 9 — Upload](SKILL.md#fase-9--upload-e-publicação) | Playlist, legendas, publish flow |
| [Lições Aprendidas](SKILL.md#lições-aprendidas) | 64 lições numeradas (#0 a #63) |
| [Templates](SKILL.md#templates-e-scripts-base) | Lista de todos os templates disponíveis |

### 📂 [templates/](templates/) — 20 ficheiros reutilizáveis (scripts + bat + SFX)

| Ficheiro | Tipo | Descrição |
|----------|------|-----------|
| `_build_all.py` | ⭐ Python | Script principal — overlays + index.html |
| `_generate_captions.py` | Python | Legendas bilingues PT+EN via API |
| `_generate_srt.py` | Python | SRT de verificação (VLC) |
| `_fix_capitalization.py` | Python | Regra platinum de capitalização |
| `generate-thumbnails.py` | Python | Thumbnails YouTube com ffmpeg (acentos OK) |
| `_split_video.py` | Python | Split com audio_enhance + keyframes |
| `_transcribe.py` | Python | Faster-Whisper → `_audio_source.json` |
| `01_render-all.bat` | Batch | Render HyperFrames (todos os episódios) |
| `02_optimize-youtube.bat` | Batch | CRF 18 + cleanup drafts |
| `03_generate-thumbnails.bat` | Batch | Wrapper para thumbnails |
| `YOUTUBE_METADATA.md` | Markdown | Template de títulos/descrições/tags |
| `DESIGN.md` | Markdown | Template de notas de design |
| `overlay-pop.wav` | Áudio | SFX para overlays bottom (0.5s) |
| `overlay-chime.wav` | Áudio | SFX para overlays fullscreen (2.1s) |
| `popup.mp3` | Áudio | SFX alternativo (popup) |
| `chime.mp3` | Áudio | SFX alternativo (chime, volume reduzido) |

---

## Lições Essenciais (top 10)

| # | Lição | Categoria |
|---|-------|-----------|
| **#43** | Legendas EN automáticas, nunca freebuff/manual — risco de desalinhamento | 🔴 Crítico |
| **#30** | Dupla verificação de timestamps com VLC + SRT antes do render | 🔴 Crítico |
| **#11** | Overlays NUNCA antes do tópico — aparecem 2-3s DEPOIS | 🔴 Crítico |
| **#15** | Capitalização platinum: só 1ª letra da frase em maiúscula | 🟡 Design |
| **#7** | Overlay de outro precisa de `transform:none` no inline style | 🟡 Técnico |
| **#5** | `data-duration` do SFX >= duração real do WAV (ffprobe) | 🟡 Técnico |
| **#2** | Keyframes densos: `-g 30 -keyint_min 30` no split | 🟡 Técnico |
| **#1** | Áudio profissional: `adeclick` primeiro na cadeia de filtros | 🟡 Técnico |
| **#3** | Batch files com ASCII simples (sem acentos/Unicode) | 🟡 Windows |
| **#29** | Cada episódio DEVE ter 5-12 overlays de conteúdo | 🔴 Crítico |
| **#46** | `deeptrans` é o motor de tradução por defeito, sem chave de API | 🟡 Legendas |
| **#62** | Registar skill para `/skill:<nome>`: frontmatter + descrição ≤400 chars + `.claude/skills/` | 🟡 Skill |
| **#63** | Colocação de overlays por âncora: frase completa em `find_anchor` + ordenação cronológica no clamp (não greedy 12s) | 🟠 Overlays |
| **#64** | ⚠️ `.bat` DEVE ter line endings CRLF — LF-only parte `if (...)` e `call :render` no cmd.exe (renders OK mas "ERROR" falso) | 🔴 Crítico |
| **#65** | Listas sequenciais (etapas 1→N): âncora = frase de INTRODUÇÃO da etapa, nunca a keyword genérica (ex.: `"etapa da preserva"` e não `"preserva"`) | 🟠 Overlays |
| **#66** | `--model` NÃO era passado ao `_resolve_provider` — o script usava sempre `TRANSLATION_MODEL` fixo; passar `args.model` (fix aplicado no projeto + template) | 🔵 Legendas |
| **#67** | Tarefas longas no Windows: `Start-Process` com caminho absoluto do python (nunca `nohup`); shim pai/filho ≠ duplicados; monitorizar por ficheiros gerados | 🔵 Legendas |

---

## Projetos de Referência

Estes projetos em `videos/` foram construídos com este skill:

| Projeto | Episódios | Estado |
|---------|-----------|--------|
| `pesquisa-info-cientifica` | 10 | ✅ Completo (legendas PT+EN) |
| `ferramentas-ia-academico` | 10 | ✅ Completo (legendas PT+EN) |
| `mendeley-referencias` | 7 | ✅ Completo (legendas PT+EN) |
| `eng-prompt-academico-v2` | 6 | ✅ Completo |
| `acesso-aberto-fct` | 6 | ✅ Completo |
| `argos-dmp` | 15 | ✅ Completo (legendas PT+EN) |
| `boas-praticas-gdi` | 16 | ✅ Completo (legendas PT+EN) |
| `dunas-repositorio` | 13 | ✅ Completo (legendas PT+EN) |
| `scopus-bibliometria` | — | 🔄 Em produção |

---

## Requisitos

- **OpenMontage** (**obrigatório**) — <https://github.com/calesthio/OpenMontage>
  (a skill corre DENTRO do OpenMontage, que fornece o HyperFrames e o rendering)
- **Python 3.10+** — `faster-whisper`, `openai`, `beautifulsoup4`
- **Node.js** — HyperFrames CLI (`npx hyperframes`)
- **ffmpeg** — no PATH (Windows: `choco install ffmpeg` ou manual)
- **GPU NVIDIA** (opcional) — RTX 3060+ recomendada para render
- **Espaço em disco** — 50-100GB livres (HyperFrames usa ~20GB temp por render)
