# webinar-to-video

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

Skill reutilizável que transforma **gravações brutas de webinars/formação** em **séries de vídeo** completas e profissionais para YouTube/LinkedIn — com overlays de conteúdo sincronizados, efeitos sonoros, legendas bilingues PT+EN, renders optimizados para YouTube, thumbnails e metadata SEO.

> **Executar dentro do [OpenMontage](https://github.com/calesthio/OpenMontage)** — o sistema open-source de produção vídeo agéntica. Esta skill não é autónoma: deve ser lançada a partir de um ambiente OpenMontage, que fornece as ferramentas de rendering HyperFrames (`npx hyperframes`) que a pipeline acciona.

## O que faz

Dada uma gravação-fonte (`.mp4`) e, idealmente, o PDF da apresentação, a skill executa uma pipeline de 8 fases:

```
1. Transcrição        Faster-Whisper large-v3 → _audio_source.json (word-level)
2. Split + áudio      episódios por tópicos; áudio melhorado + keyframes densos
3. Build              _build_all.py → epXX/index.html (overlays + SFX, ancorados)
4. Legendas           PT com correcções de terminologia; EN via deep-translator/API
5. Render             HyperFrames (draft → high, GPU, 12 workers)
6. Optimizar YouTube  ffmpeg CRF 18 preset slow + limpeza de drafts
7. Thumbnails         extracção de frames + sobreposição de título
8. Metadata + upload  YOUTUBE_METADATA.md (títulos, descrições, tags, timestamps)
```

**Overlays** existem em seis tipos codificados por cor (`CONCEITO`, `DICA`, `ESTRUTURA`, `FERRAMENTA`, `IMPORTANTE`, `EXEMPLO`) e são ancorados ao discurso: o script encontra as palavras reais do orador na transcrição (`find_anchor`), coloca cada cartão 2-3 s depois da menção, verifica todas as âncoras dentro da janela do episódio (`_verify_anchors.py`) e gera um SRT verificável no VLC para confirmação visual.

**Legendas** são bilingues (PT + EN). A pista PT recebe correcções de terminologia a partir do PDF (ex.: `dunas` → `DUnAs`, `mesh` → `MeSH`); a pista EN é traduzida automaticamente — `deep-translator` por defeito, com providers via API opcionais (`openai-compat`, `deepseek`, `openai`). Falhas de tradução interrompem a geração de forma explícita; o texto PT nunca é copiado silenciosamente para o ficheiro EN.

## Requisitos

| Necessidade | Detalhes |
| --- | --- |
| **OpenMontage** | **Obrigatório — a skill corre dentro dele.** <https://github.com/calesthio/OpenMontage> — fornece as ferramentas de rendering HyperFrames. |
| **Python 3.10+** | `faster-whisper`, `openai`, `deep-translator`, `beautifulsoup4`. |
| **Node.js** | CLI HyperFrames via `npx hyperframes`. |
| **ffmpeg** | No PATH — cadeia de áudio, optimização, thumbnails. |
| **GPU + disco** | GPU NVIDIA recomendada; 50-100 GB livres (cada render usa ~20 GB temporários). |

## Quick start

```bash
mkdir videos/meu-webinar && cd videos/meu-webinar
cp -r .agents/skills/webinar-to-video/templates/* ./
mkdir ep01 ep02 ep03 assets_sfx renders

cp /caminho/para/webinar.mp4 ./source_webinar.mp4
cp /caminho/para/apresentacao.pdf ./

python _transcribe.py                # 1. transcrição
# editar EPISODE_BOUNDARIES em _split_video.py
python _split_video.py               # 2. split + áudio
# editar EPISODES + OVERLAYS em _build_all.py
python _verify_anchors.py            # verificar âncoras → Problems: 0
python _build_all.py                 # 3. gerar index.html
python _generate_captions.py         # 4. legendas PT + EN

01_render-all.bat                    # 5. render (draft primeiro!)
02_optimize-youtube.bat              # 6. optimizar
03_generate-thumbnails.bat           # 7. thumbnails
# 8. preencher YOUTUBE_METADATA.md → upload
```

Renderizar primeiro em **draft**, rever os overlays no VLC (o SRT de verificação é carregado automaticamente), corrigir timestamps no `_build_all.py` e só então re-renderizar em alta qualidade.

## Ficheiros

```
webinar-to-video/
├── SKILL.md                ← pipeline completa + lições aprendidas #0-#67 (PT)
├── INDEX.md                ← quick-start de 1 minuto, tabela de templates, projectos (PT)
├── README.md               ← versão inglesa
├── README_PT.md            ← este ficheiro
└── templates/              ← 20 ficheiros reutilizáveis copiados para cada projecto
    ├── _build_all.py             ⭐ script principal: overlays + index.html
    ├── _generate_captions.py     legendas bilingues PT+EN
    ├── _generate_srt.py          SRT de verificação (VLC)
    ├── _validate_captions.py     validador de alinhamento PT/EN
    ├── _fix_capitalization.py    regra platinum de capitalização
    ├── _split_video.py           split + audio_enhance + keyframes
    ├── _transcribe.py            transcrição Faster-Whisper
    ├── _verify_anchors.py        âncoras dos overlays nas janelas dos episódios
    ├── _launch_split.py / _launch_captions.py     launchers destacados (Windows)
    ├── generate-thumbnails.py    thumbnails ffmpeg (seguro para acentos)
    ├── 01_render-all.bat / 02_optimize-youtube.bat / 03_generate-thumbnails.bat
    ├── DESIGN.md / YOUTUBE_METADATA.md           templates de design + SEO
    └── overlay-pop.wav / overlay-chime.wav / popup.mp3 / chime.mp3    SFX
```

## Lições aprendidas

O `SKILL.md` traz um catálogo numerado de 68 lições (#0-#67), incluindo: a cadeia obrigatória de filtros de áudio, keyframes densos, line endings CRLF nos `.bat`, texto só-ASCII nos batch files, ancoragem de overlays por frase completa (nunca keywords genéricas), âncoras de listas sequenciais usando a frase de transição do orador, nunca traduzir legendas EN por índice, erros de quota a interromper de imediato, e a limpeza de `%TEMP%\hf-render-*`.

## Projectos de referência

Nove séries já foram produzidas com esta skill (até 16 episódios cada), incluindo `pesquisa-info-cientifica`, `ferramentas-ia-academico`, `mendeley-referencias`, `argos-dmp`, `boas-praticas-gdi` e `dunas-repositorio`. Consulte o [INDEX.md](INDEX.md) para a lista completa.

## Instalação

Copie a pasta `webinar-to-video/` completa para o directório de skills que o seu agente analisa (ex.: `.agents/skills/`). O frontmatter do `SKILL.md` (`name: webinar-to-video`) é o que a torna invocável como `/skill:webinar-to-video`.
