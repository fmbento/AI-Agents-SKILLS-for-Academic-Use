# Production — Skills de Produção

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

A colecção `Production` contém skills para trabalho de backoffice, criação de conteúdos e produção automatizada de novos materiais — séries de aprendizagem, episódios de vídeo e entregáveis prontos a publicar. Estas skills transformam material-fonte bruto (gravações, documentos, apresentações) em produtos finais publicáveis.

## Skills

### [webinar-to-video](webinar-to-video/SKILL.md)

**Gravações de webinars → séries de vídeo profissionais.** Transforma uma gravação bruta de webinar ou formação (`.mp4`) numa série completa para YouTube/LinkedIn, com cartões de intro/outro, overlays de conteúdo sincronizados, efeitos sonoros, legendas bilingues PT+EN, ficheiros de vídeo optimizados e thumbnails.

A skill executa uma pipeline de 8 fases:

1. **Transcrição** — Faster-Whisper (`large-v3`, word-level) produz `_audio_source.json`.
2. **Split + áudio + keyframes** — o vídeo-fonte é cortado em episódios por tópicos e o áudio é melhorado (remoção de eco/ruído, normalização para -16 LUFS) com keyframes densos para seeking.
3. **Build** — `_build_all.py` gera o `index.html` HyperFrames de cada episódio: intro (0-5s), outro, overlays de conteúdo (`CONCEITO`, `DICA`, `ESTRUTURA`, `FERRAMENTA`, `IMPORTANTE`, `EXEMPLO`) e SFX por overlay. O timing dos overlays é ancorado ao discurso via `find_anchor` e verificado com `_verify_anchors.py` mais um SRT verificável no VLC.
4. **Legendas bilingues** — `_generate_captions.py` produz legendas PT com correcções de terminologia (a partir do PDF da apresentação) e traduções EN (provider por defeito: `deep-translator`; providers via API opcionais).
5. **Render** — o HyperFrames renderiza todos os episódios (draft primeiro, depois alta qualidade, com aceleração por GPU).
6. **Optimização YouTube** — re-encode com ffmpeg (CRF 18, preset slow, `+faststart`) mais limpeza dos drafts.
7. **Thumbnails** — extracção de frames com sobreposição de título via ffmpeg/Python.
8. **Metadata + upload** — `YOUTUBE_METADATA.md` com títulos SEO, descrições, timestamps, tags e hashtags.

A skill inclui ainda um catálogo numerado de **lições aprendidas** (#0-#67) que cobre cadeias de áudio, ancoragem de overlays, armadilhas de batch no Windows (line endings CRLF, texto só-ASCII), salvaguardas na tradução de legendas e regras de limpeza de disco.

#### Requisitos

| Necessidade | Detalhes |
| --- | --- |
| **OpenMontage** | **Obrigatório — a skill corre dentro dele.** [https://github.com/calesthio/OpenMontage](https://github.com/calesthio/OpenMontage), o sistema open-source de produção vídeo agéntica que fornece as ferramentas de rendering HyperFrames. |
| **Python 3.10+** | `faster-whisper`, `openai`, `deep-translator`, `beautifulsoup4` (biblioteca padrão na maioria dos scripts). |
| **Node.js** | CLI HyperFrames via `npx hyperframes`. |
| **ffmpeg** | No PATH (cadeia de áudio, optimização, thumbnails). |
| **Material-fonte** | Webinar `.mp4`; PDF da apresentação fortemente recomendado (terminologia + estrutura). |
| **Hardware** | GPU NVIDIA recomendada para render; 50-100 GB livres (cada render usa ~20 GB temporários). |

O [INDEX.md](webinar-to-video/INDEX.md) da própria skill tem um quick-start de 1 minuto, a tabela completa de templates e a lista de projectos de referência construídos com ela (9 séries, até 16 episódios cada). O [SKILL.md](webinar-to-video/SKILL.md) completo documenta todas as fases, o sistema de design dos overlays e todas as lições aprendidas. Ambos estão escritos em português; a pasta `templates/` contém os 20 ficheiros reutilizáveis — scripts, batch files, SFX e templates de design/metadata.

#### Entradas e saídas

| Direcção | Itens |
| --- | --- |
| **Entradas** | Webinar `.mp4` fonte; PDF da apresentação (recomendado); limites de episódios/tópicos; conteúdo dos overlays e termos de âncora. |
| **Saídas** | Renders MP4 por episódio (draft + optimizados YouTube); legendas `.srt` PT/EN; thumbnails; `YOUTUBE_METADATA.md`; SRTs de verificação; checklist de upload. |

### Quando escolher esta skill

Use `webinar-to-video` quando a tarefa é converter gravações existentes numa série de vídeo polida e publicada — não para gerar vídeos do zero. Para essa capacidade mais ampla (incluindo material gerado do zero), consulte o projecto subjacente [OpenMontage](https://github.com/calesthio/OpenMontage), que fornece as ferramentas de rendering que esta skill orquestra.

A skill de `Production` que está a ler é a skill de séries de vídeo. Outros tipos de entrega de produção — documentos editáveis, folhas de cálculo, figuras, pósteres ou apresentações a partir do mesmo conteúdo subjacente — pertencem aos scripts e skills partilhados em `Utils/`. Quando faz sentido, os passos seguintes naturais são:

- tornar qualquer acompanhamento em markdown (por exemplo `YOUTUBE_METADATA.md` ou um ficheiro de notas de produção) num PDF com `Utils/scripts/generate_pdf.py`;
- usar `Utils/Skills/docx` ou `Utils/Skills/xlsx` quando o mesmo material também precisar de um entregável editável no escritório;
- usar `Utils/Skills/markdown-mermaid-writing`, `Utils/Skills/scientific-visualization`, `Utils/Skills/scientific-schematics`, `Utils/Skills/scientific-slides` ou `Utils/Skills/pptx-posters` quando o resultado de produção deva incluir figuras, diagramas ou vizuais de apresentação em vez de apenas vídeo.

Para saber onde cabe cada ajudante e quais são locais a uma skill, consulte `Utils/skills-integration.md`.

## Estrutura da pasta

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
