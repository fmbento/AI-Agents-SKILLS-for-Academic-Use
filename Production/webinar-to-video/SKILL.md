---
name: webinar-to-video
description: Transforma gravações de webinars em séries de vídeos profissionais (YouTube/LinkedIn) com overlays HyperFrames, legendas bilingues PT+EN, SFX e thumbnails. Use quando o utilizador fornecer um vídeo de webinar/formação (mp4) e quiser uma série de episódios com separadores, callouts sincronizados com o discurso, legendas corrigidas por terminologia e metadata YouTube.
---

# Webinar-to-Video Series — Pipeline Completa

Transforma gravações de webinars em séries de vídeos profissionais para YouTube,
com overlays HyperFrames, legendas bilingues (PT+EN), SFX, e thumbnails.

---

## Índice

1. [Visão Geral da Pipeline](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Fase 1 — Transcrição (Faster-Whisper)](#fase-1--transcrição)
4. [Fase 2 — Split + Áudio + Keyframes](#fase-2--split--áudio--keyframes)
5. [Fase 3 — Build (Overlays + index.html)](#fase-3--build)
6. [Fase 4 — Legendas Bilingues (PT + EN)](#fase-4--legendas-bilingues)
7. [Fase 5 — Render (HyperFrames)](#fase-5--render)
8. [Fase 6 — Otimização YouTube (ffmpeg)](#fase-6--otimização-youtube)
9. [Fase 7 — Thumbnails](#fase-7--thumbnails)
10. [Fase 8 — Metadata YouTube](#fase-8--metadata-youtube)
11. [Fase 9 — Upload e Publicação](#fase-9--upload-e-publicação)
12. [Lições Aprendidas (0-61)](#lições-aprendidas)
13. [Templates e Scripts Base](#templates-e-scripts-base)

---

## Visão Geral

### Pré-requisitos

- **OpenMontage** (**obrigatório**) — <https://github.com/calesthio/OpenMontage>.
  Esta skill NÃO é autónoma: deve ser executada DENTRO do OpenMontage, o
  sistema open-source de produção vídeo agéntica que fornece o ambiente,
  o HyperFrames e o motor de rendering usados na Fase 5.
- **Ficheiro vídeo fonte** (gravação do webinar, `.mp4`)
- **PDF da apresentação** (opcional mas fortemente recomendado — para corrigir
  transcrições e extrair terminologia)
- **Node.js** + HyperFrames CLI (`npx hyperframes`)
- **Python 3.10+** com `openai`, `deep-translator`, `faster-whisper`, `beautifulsoup4`
- **ffmpeg** no PATH

### Pipeline (8 fases)

```
Fase 1: Transcrição     → _audio_source.json (Faster-Whisper, word-level)
Fase 2: Split + Áudio   → epXX/epXX_video.mp4 (com audio_enhance + keyframes)
Fase 3: Build           → epXX/index.html (overlays HyperFrames)
Fase 4: Legendas        → epXX_video.pt.srt + epXX_video.en.srt
Fase 5: Render          → renders/epXX-*.mp4 (HyperFrames)
Fase 6: Otimização      → renders/youtube/epXX-*-yt.mp4 (CRF 18, preset slow)
Fase 7: Thumbnails      → renders/youtube/thumbnails/*.jpg
Fase 8: Metadata        → YOUTUBE_METADATA.md
```

### Comando rápido (projeto novo)

```bash
# 1. Criar estrutura
mkdir videos/meu-webinar && cd videos/meu-webinar
mkdir ep01 ep02 ... ep10 assets_sfx renders

# 2. Copiar video fonte e PDF
cp /caminho/para/webinar.mp4 ./
cp /caminho/para/apresentacao.pdf ./

# 3. Copiar templates (do skill)
cp .agents/skills/webinar-to-video/templates/* ./

# 4. Fase 1 — Transcrever
python _transcribe.py  # → _audio_source.json

# 5. Fase 2 — Split
python _split_video.py  # → epXX/epXX_video.mp4

# 6. Fase 3 — Build
python _build_all.py    # → epXX/index.html

# 7. Fase 4 — Legendas
python _generate_captions.py    # → legendas PT + EN (por defeito via deeptrans)

# 8. Fase 5 — Render (draft primeiro!)
01_render-all.bat

# 9. Rever overlays no VLC (os .srt são carregados automaticamente)

# 10. Ajustar timestamps em _build_all.py → re-correr _build_all.py

# 11. Render final
# Editar 01_render-all.bat: QUALITY=high → correr de novo

# 12. Fase 6 — Otimizar
02_optimize-youtube.bat

# 13. Fase 7 — Thumbnails
03_generate-thumbnails.bat

# 14. Fase 8 — Preencher YOUTUBE_METADATA.md
```

---

## Estrutura do Projeto

```
videos/<nome-do-webinar>/
├── _audio_source.json          # Transcrição word-level (Faster-Whisper)
├── _audio_source.srt           # Transcrição SRT (fallback)
├── _build_all.py               # ⭐ Script principal: gera todos os index.html
├── _generate_captions.py       # Legendas bilingues PT+EN
├── _generate_srt.py            # SRT de verificação dos overlays (VLC)
├── _fix_capitalization.py      # Regra platinum de capitalização
├── _split_video.py             # Split do vídeo fonte em episódios
├── _transcribe.py              # Transcrição Faster-Whisper
├── generate-thumbnails.py      # Geração de thumbnails com ffmpeg
├── 01_render-all.bat           # Render de todos os episódios
├── 02_optimize-youtube.bat     # Otimização CRF 18 + cleanup drafts
├── 03_generate-thumbnails.bat  # Wrapper para generate-thumbnails.py
├── YOUTUBE_METADATA.md         # Títulos, descrições, tags SEO
├── DESIGN.md                   # Notas de design visual (opcional)
├── assets_sfx/
│   ├── overlay-pop.wav         # Som de popup (bottom overlays)
│   └── overlay-chime.wav       # Som de entrada (fullscreen overlays)
├── renders/
│   ├── ep01-*.mp4              # Renders finais
│   ├── ep01-*.pt.srt           # Legendas PT
│   ├── ep01-*.en.srt           # Legendas EN
│   └── youtube/
│       ├── ep01-*-yt.mp4       # Versões YouTube
│       └── thumbnails/
│           └── ep01-*-thumb.jpg
├── ep01/
│   ├── index.html              # Composição HyperFrames
│   ├── ep01_video.mp4          # Segmento de vídeo
│   ├── ep01_video.mp4.srt      # SRT de verificação (overlays)
│   ├── ep01_video.pt.srt       # Legendas PT
│   ├── ep01_video.en.srt       # Legendas EN
│   ├── overlay-pop.wav         # SFX local (copiado na build)
│   └── overlay-chime.wav       # SFX local
├── ep02/ ... ep10/
```

---

## Fase 1 — Transcrição

### 1.1 Faster-Whisper → _audio_source.json

Usar Faster-Whisper (modelo `large-v3`) para transcrição word-level:

```bash
python _transcribe.py --model large-v3 --language pt
```

**Output:** `_audio_source.json` com estrutura:
```json
{
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.2,
      "text": "texto da transcrição...",
      "words": [
        {"word": "texto", "start": 0.0, "end": 0.5, "probability": 0.98}
      ]
    }
  ]
}
```

### 1.2 Fallback: _audio_source.srt

Se Faster-Whisper não estiver disponível, usar `_audio_source.srt`
(transcrição do webinar original, se existir).

---

## Fase 2 — Split + Áudio + Keyframes

### 2.1 Split do vídeo fonte

```bash
python _split_video.py
```

**O que faz:**
1. Lê `_audio_source.json` para determinar timestamps
2. Corta o vídeo fonte em segmentos `epXX/epXX_video.mp4`
3. Aplica `audio_enhance` (ver abaixo)
4. Re-encode com keyframes a cada 1s (`-g 30 -keyint_min 30`)

### 2.2 Cadeia de filtros de áudio

**OBRIGATÓRIO** — remove eco fantasma, ruído de fundo, normaliza para -16 LUFS:

```
adeclick,highpass=f=80,lowpass=f=13000,agate=threshold=-30dB:ratio=2:attack=5:release=50,acompressor=threshold=-20dB:ratio=3:attack=10:release=100,loudnorm=I=-16:LRA=11:TP=-1.5
```

**⚠️ `adeclick` DEVE ser o primeiro filtro** — sem ele, os cortes de silêncio
produzem cliques audíveis.

### 2.3 Keyframes

HyperFrames precisa de keyframes densos para seeking. Sempre re-encode:

```bash
ffmpeg -i input.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 \
  -movflags +faststart -c:a aac -b:a 192k output.mp4
```

---

## Fase 3 — Build (Overlays + index.html)

### 3.1 Script principal: `_build_all.py`

Este é o coração da pipeline. Deve ser personalizado para cada projeto:

```bash
python _build_all.py
```

**O que gera:**
- `epXX/index.html` para cada episódio (composição HyperFrames)
- Copia SFX (`overlay-pop.wav`, `overlay-chime.wav`) para cada `epXX/`
- Gera SRT de verificação (`epXX/epXX_video.mp4.srt`) via `_generate_srt.py`
- Chama `_generate_captions.py --skip-translate` para legendas PT

### 3.2 Estrutura do index.html

Cada `index.html` contém:

1. **`<video>` + `<audio>`** (track 0+1, full timeline)
2. **Intro** (0-5s, track 2, fullscreen) — título do episódio
3. **Outro** (últimos 5s, track 2, fullscreen) — "Próximo Episódio" ou "Obrigado"
4. **Content overlays** (track 3, timestamps variáveis) — dicas, conceitos, notas
5. **SFX audio elements** (tracks 4+, um por overlay) — popup/fullscreen sounds

### 3.3 Tipos de Overlay

| Tipo | Posição | Uso | Duração |
|------|---------|-----|---------|
| `overlay-bottom` | Bottom 80px, full width | Dicas rápidas, notas | 9s |
| `overlay-center` | Centro do ecrã, fullscreen | Conceitos importantes, secções | 9s |

### 3.4 Cores dos Overlays

| Tag | Cor | Uso |
|-----|-----|-----|
| `CONCEITO` | `#14B8A6` (teal) | Definições e conceitos |
| `DICA` | `#FACC15` (amarelo) com texto `#0B1120` | 💡 Dicas práticas |
| `ESTRUTURA` | `#8B5CF6` (roxo) | Estrutura/roadmap do episódio |
| `FERRAMENTA` | `#F97316` (laranja) | Ferramentas e serviços |
| `IMPORTANTE` | `#EF4444` (vermelho) | ⚠ Avisos e cuidados |
| `EXEMPLO` | `#F97316` (laranja) | Exemplos práticos |

### 3.5 Overlay Timing

**Regra de ouro:** overlay aparece 2-3 segundos **DEPOIS** de o orador começar
a falar sobre o tópico, NUNCA antes.

Usar `_generate_srt.py` para gerar ficheiros `.srt` de verificação — abrir o
`epXX_video.mp4` no VLC e verificar visualmente que cada overlay coincide com
o discurso.

### 3.6 SFX nos Overlays

Cada overlay tem um som associado:
- `overlay-bottom` → `overlay-pop.wav` (volume 0.75, 0.5s)
- `overlay-center` → `overlay-chime.wav` (volume 1.0, 2.1s)

**O SFX toca APENAS quando o overlay aparece** (fade-in), não no fade-out.
Isto permite que o "aluno" que está só a ouvir saiba que algo novo apareceu.

---

## Fase 4 — Legendas Bilingues

### 4.1 Script: `_generate_captions.py`

```bash
# Por defeito (recomendado — deeptrans, rápido e sem chave de API):
python _generate_captions.py

# Via OpenAI-compat local:
python _generate_captions.py --provider openai-compat --base-url http://127.0.0.1:10531/v1 --model gpt-5.4-mini

# Via DeepSeek:
python _generate_captions.py --provider deepseek

# Via OpenAI oficial:
python _generate_captions.py --provider openai
```

**⚠️ LIÇÃO #43: nunca usar `freebuff`/tradução manual por índice para o EN final.**
A tradução manual por índice tem risco elevado de desalinhamento PT↔EN.
Usar um provider automático: `deeptrans` (por defeito) ou, quando for necessário maior controlo terminológico, `openai-compat`, `deepseek` ou `openai`. Falhas de tradução devem interromper a geração; nunca copiar silenciosamente o texto PT para o SRT EN.

### 4.2 Correções de terminologia

O script inclui `TERM_CORRECTIONS` — um dicionário de correções baseadas
no PDF da apresentação:

```python
TERM_CORRECTIONS: dict[str, str] = {
    "compiler": "Claude",     # Corrige erro de transcrição do Whisper
    "groc": "Grok",
    "deepseq": "DeepSeek",
    "eric tesouros": "ERIC Thesaurus",
    "mesh tesouros": "MeSH Thesaurus",
    # ...
}
```

### 4.3 Servidor OpenAI-compatible local

Para usar `gpt-5.4-mini` ou outro modelo local:

```bash
npx --yes openai-oauth --detach --port 10531
# Esperar que http://127.0.0.1:10531/v1/models esteja disponível
```

### 4.4 Output

- `epXX/epXX_video.pt.srt` — legendas PT (corrigidas)
- `epXX/epXX_video.en.srt` — legendas EN (traduzidas)
- Cópias em `renders/epXX-*.pt.srt` e `renders/epXX-*.en.srt`

---

## Fase 5 — Render

### 5.1 Batch file: `01_render-all.bat`

```batch
@echo off
setlocal enabledelayedexpansion
set QUALITY=draft       # draft para teste, high para final
set WORKERS=12          # Ajustar ao hardware (RTX 3060 = 4-12)
set PRODUCER_BROWSER_GPU_MODE=hardware

npx --yes hyperframes render "ep01" --quality %QUALITY% --workers %WORKERS% --gpu --output "renders\ep01-*.mp4"
```

### 5.2 Qualidade

| Modo | Uso | Velocidade |
|------|-----|------------|
| `draft` | Teste de timestamps e overlays | Rápido |
| `high` | Versão final YouTube | Lento (CRF 18 equivalente) |

**SEMPRE testar com `draft` primeiro.** Só fazer `high` depois de verificar
todos os overlays no VLC e corrigir timestamps.

### 5.3 GPU

Para forçar GPU NVIDIA (RTX 3060):
```batch
set PRODUCER_BROWSER_GPU_MODE=hardware
```
E passar `--gpu` ao comando `hyperframes render`.

### 5.4 Espaço em disco

O HyperFrames pode consumir 20-50GB temporários durante o render.
O `01_render-all.bat` inclui cleanup automático:
```batch
rmdir /s /q "%RENDERS%\.hf-transaction-*" 2>nul
```

### 5.5 Modo automático (sem perguntas)

Adicionar ao batch:
```batch
set HYPERFRAMES_NO_PROMPT=1
```
Ou usar `echo y | npx --yes hyperframes ...` para bypass do "Ok to proceed?".

---

## Fase 6 — Otimização YouTube

### 6.1 Batch file: `02_optimize-youtube.bat`

```batch
ffmpeg -i "renders\ep01-*.mp4" \
  -c:v libx264 -preset slow -crf 18 \
  -profile:v high -level 4.0 -bf 2 -g 30 \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "renders\youtube\ep01-*-yt.mp4"
```

### 6.2 Cleanup de drafts

O batch OTIMIZA e DEPOIS remove os drafts:
```batch
del "%RENDERS%\ep01-*.mp4"
```

**Importante:** Só remover depois de confirmar que o `-yt.mp4` foi criado com
sucesso (`if exist`).

---

## Fase 7 — Thumbnails

### 7.1 Script: `generate-thumbnails.py`

Extrai um frame de cada vídeo YouTube e adiciona overlay de texto:

```python
EPISODES = [
    ("ep01-info-cientifica-yt", "Título do\nEpisódio 1", 90),  # 90s = timestamp do frame
    # ...
]
```

### 7.2 Batch file: `03_generate-thumbnails.bat`

```batch
@echo off
cd /d <PROJECT_DIR>
python generate-thumbnails.py
pause
```

### 7.3 ⚠️ Lição #28: Acentos nos thumbnails

No Windows, o ffmpeg pode falhar com texto acentuado via `drawtext`.
**Solução:** usar um script Python em vez de batch puro, que faz o encoding
corretamente via `subprocess.run(..., encoding='utf-8')`.

---

## Fase 8 — Metadata YouTube

### 8.1 Ficheiro: `YOUTUBE_METADATA.md`

Template:

```markdown
# YouTube Metadata — Nome da Série (N Episódios)

## Playlist
**Título:** Nome da Série | Curso Completo (2025)
**Descrição:** ...

## Episódio 1 — Título
**Título SEO:** 🔑 Título com Keywords (Ep. 1/N)
**Descrição:** ...
**Timestamps:**
00:00 — Introdução
...
**Tags:** tag1, tag2, ...
**Hashtags:** #Tag1 #Tag2
```

---

## Fase 9 — Upload e Publicação

1. Criar playlist no YouTube
2. Upload dos ficheiros `renders/youtube/*-yt.mp4`
3. Adicionar thumbnails personalizados
4. Colar títulos, descrições e tags do `YOUTUBE_METADATA.md`
5. Adicionar legendas PT (upload do `.pt.srt`)
6. Adicionar legendas EN (upload do `.en.srt`)
7. Publicar como "Não listado" primeiro → verificar → "Público"

---

## Lições Aprendidas

### #0 — Pipeline de 8 fases
A pipeline completa tem 8 fases sequenciais. Não saltar fases.
Fase 5 (Render) deve ser feita em `draft` primeiro, SEMPRE.

### #1 — Áudio profissional no split
Usar preset `clean_speech` com cadeia de filtros ffmpeg:
`adeclip,highpass,lowpass,agate,acompressor,loudnorm`.
Isto remove eco fantasma, ruído de fundo e normaliza para -16 LUFS.

### #2 — Keyframes densos no split
Re-encode sempre com `-g 30 -keyint_min 30`. HyperFrames falha com
keyframes esparsos (>8s entre keyframes).

### #3 — Batch files com ASCII simples
NO WINDOWS, batch files NÃO podem ter caracteres Unicode (acentos, emojis).
Usar sempre ASCII: `Episodio` em vez de `Episódio`, `Conclusao` em vez de `Conclusão`.

### #4 — SFX nos overlays
Cada overlay tem som: popup (0.5s) para bottom, chime (2.1s) para fullscreen.
SFX toca no fade-in, não no fade-out. Permite "ouvir" o vídeo.

### #5 — `data-duration` >= duração real do WAV
O `data-duration` do elemento `<audio>` do SFX deve ser >= duração real do
ficheiro WAV (verificar com `ffprobe`), não um valor fixo arbitrário.

### #6 — `data-volume` do chime
Se o `overlay-chime.wav` já tem 50% de volume baked-in, usar `data-volume="1.0"`.
Caso contrário, `data-volume="0.5"`. O popup mantém `data-volume="0.75"`.

### #7 — Overlay de outro precisa de `transform:none`
O overlay do próximo episódio (track 2) DEVE ter `transform:none` no inline style.
Sem isto, aparece deslocado para o canto superior esquerdo (1/4 do ecrã).

### #8 — Outro sem fade-out
O overlay de outro NÃO deve ter `tl.to("#ov-outro", {opacity:0})`.
Deve ficar visível até o vídeo terminar. O fade-out é do vídeo, não do overlay.

### #9 — Vídeo com fade-in na abertura
O vídeo principal deve ter `tl.from("#main-video", {opacity:0, duration:0.8})`
para um fade-in suave por trás do card de introdução.

### #10 — Intro (0-5s) com fade-out
A intro aparece nos primeiros 5s e faz fade-out:
```javascript
tl.to("#ov-intro", {opacity:0, duration:0.3}, 4.7);
tl.set("#ov-intro", {opacity:0}, 5.0);
```

### #11 — Overlays NUNCA antes do tópico
Overlay aparece 2-3s DEPOIS do orador mencionar o tópico. NUNCA antes.
Se o orador fala de "overfitting" ao minuto 1:00, o overlay aparece a 1:02,
não aos 0:48.

### #12 — Verificação com VLC + SRT
Gerar `epXX_video.mp4.srt` via `_generate_srt.py` e abrir o vídeo no VLC.
O SRT é carregado automaticamente → cada overlay aparece como legenda no
timestamp exato → verificar visualmente.

### #13 — Timestamps do SRT fonte
Se os overlays estão sistematicamente adiantados/atrasados, verificar se
os timestamps no `_audio_source.json`/.srt estão alinhados com o vídeo
pós-split (o áudio enhanced pode ter offsets diferentes).

### #14 — Keyword search no JSON transcript
Para timestamps precisos, pesquisar keywords no `_audio_source.json`:
```python
for seg in segments:
    if "overfitting" in seg["text"].lower():
        overlay_start = seg["start"] - episode_offset + 2  # +2s delay
```

### #15 — Capitalização platinum rule
**REGRA PLATINUM:** Só a primeira letra da primeira palavra da frase em
maiúscula. Exceção: termos-chave (nomes próprios, acrónimos, serviços).
- ✅ "Leitura crítica: não ler tudo"
- ❌ "Leitura Crítica: Não Ler Tudo"

### #16 — `_fix_capitalization.py` como template
O script de capitalização deve ser um template reutilizável que:
1. Lê `_build_all.py`
2. Aplica a regra platinum a todos os overlays
3. Regenera `index.html`

### #17 — Overlays fullscreen vs bottom
- Fullscreen (`overlay-center`): conceitos importantes, secções. Substitui o vídeo.
- Bottom (`overlay-bottom`): dicas rápidas, notas. Sobreposto com fundo preto.

### #18 — Fundo preto nos overlays
Todos os overlays devem ter `background:rgba(11,17,32,0.94)` para garantir
legibilidade sobre o vídeo.

### #19 — Duração reduzida dos overlays
Overlays duram 9s (ajustável). Funcionam como "popup de resumo" do segmento.
Não devem ficar muito tempo no ecrã.

### #20 — Overlays no início do segmento
Aparecem no início do segmento (2-3s após menção), nunca antes.

### #21 — Próximo episódio nos últimos 5s
O overlay "Próximo Episódio" aparece nos últimos 5s do vídeo. Se o overlay
está a aparecer 15-20s antes do fim, reduzir `outro_dur` para 5.

### #22 — Projetos com timestamps relativos (OVERLAYS dict)
Em projetos onde overlays são definidos no `_build_all.py` (OVERLAYS dict),
os timestamps são calculados automaticamente via `find_anchor` (lição #57) —
não existem `SRT_KEYWORDS` manuais. A verificação é feita por `_verify_anchors.py`
(âncoras dentro da janela do episódio) + SRT de verificação no VLC.

### #23 — Generate-thumbnails.py com Python (não batch)
No Windows, usar script Python para thumbnails (evita problemas de encoding).
O batch wrapper (`03_generate-thumbnails.bat`) apenas chama o script.

### #24 — Acentos nos thumbnails (lição #28)
ffmpeg `drawtext` no Windows falha com texto acentuado. O script Python
resolve isto fazendo encoding correto via `subprocess`.

### #25 — Cleanup depois do render
O `01_render-all.bat` DEVE incluir cleanup de:
- Transações HyperFrames (`.hf-transaction-*`)
- Vídeos duplicados em `assets/`
- Ficheiros temporários
- **`%TEMP%\hf-render-*` (⚠️ CRÍTICO — o "ladrão" de espaço).** Cada render
  do HyperFrames cria uma pasta `hf-render-<id>` no TEMP com ~5GB (frames +
  assembly). O padrão `%TEMP%\hyperframes*` NÃO apanha `hf-render-*` — renders
  interrompidos (Ctrl+C no bat) deixam essas pastas para trás e o disco enche.
  O cleanup DEVE ter:
  ```batch
  for /d %%D in ("%TEMP%\hf-render-*") do rmdir /s /q "%%~fD" 2>nul
  ```
  Verificar com `dir %TEMP%\hf-render-*` depois de cada render.

### #26 — Cleanup no optimize-youtube.bat
Depois de gerar `-yt.mp4`, remover o draft original para libertar espaço.

### #27 — YOUTUBE_METADATA.md com timestamps
As descrições dos episódios devem incluir timestamps (00:00, 01:30, etc.)
para melhor UX e SEO no YouTube.

### #28 — Formatação dos títulos YouTube
Estrutura: `🔑 Título Descritivo com Keywords (Ep. X/N)`

### #29 — Overlays OBRIGATÓRIOS em todos os episódios
Cada episódio DEVE ter 5-12 overlays de conteúdo (não apenas intro/outro).
Analisar o SRT e identificar: conceitos-chave, dicas práticas, avisos,
ferramentas mencionadas, estrutura do episódio.

### #30 — Dupla verificação de timestamps
Depois de definir overlays, SEMPRE:
1. Correr `_verify_anchors.py` (confirmar que cada termo de âncora existe na janela do episódio)
2. Gerar SRT de verificação (`_generate_srt.py`)
3. Abrir no VLC
4. Confirmar que cada overlay está no momento certo
5. Se um overlay aparecer cedo/tarde: ajustar os TERMOS DE ÂNCORA (ou a janela) no
   `_build_all.py` e re-correr `_build_all.py` + `_verify_anchors.py` + `_generate_srt.py`

### #31 — Overlay SRT ignora intro, outro e SFX
O `_generate_srt.py` ignora:
- `ov-intro` (0-5s, não é conteúdo)
- `ov-outro` (últimos 5s, não é conteúdo)
- Elementos `<audio>` SFX (não são visuais)
- O elemento `<video>` principal

### #32 — `data-duration` do SFX >= duração WAV
Verificar com:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 overlay-chime.wav
```

### #33 — `data-track-index` para SFX
Cada SFX precisa do seu próprio track index:
- Track 0: vídeo
- Track 1: áudio principal
- Track 2: intro + outro
- Track 3: overlays visuais
- Track 4+: SFX (um por overlay)

### #34 — Ordem dos scripts no projeto
Nomear com prefixos numéricos para indicar ordem de execução:
- `01_render-all.bat`
- `02_optimize-youtube.bat`
- `03_generate-thumbnails.bat`

### #35 — Silêncio e hesitações
O `.srt` NÃO serve para detectar hesitações/hums — a transcrição do Whisper
já é "corrigida" pelo modelo. Para corte de silêncio real, usar
`tools/analysis/beat_analyzer.py` ou análise de waveform.

### #36 — Term corrections do PDF
As correções `TERM_CORRECTIONS` devem vir do PDF da apresentação.
Nomes de serviços (ChatGPT, Claude, Grok, DeepSeek, etc.) são frequentemente
mal transcritos pelo Whisper.

### #37 — Acentos nos vídeos fonte
O HyperFrames precisa de encontrar o ficheiro de vídeo exatamente como
referenciado no `src`. Usar sempre paths relativos ao episódio:
`src="ep01_video.mp4"`, NUNCA `../assets/ep01_video.mp4`.

### #38 — Template `_fix_capitalization.py`
O script deve ser um template reutilizável que processa `_build_all.py`.
Deve preservar a estrutura de tuplos dos overlays e apenas alterar os
campos de título e subtítulo.

### #39 — Geração automática de SRT por episódio
`_generate_srt.py` faz parse dos `index.html` e produz `epXX_video.mp4.srt`
para verificação no VLC. Deve ser chamado automaticamente no final do
`_build_all.py`.

### #40 — Projetos devem ter batch files nomeados com prefixo
`01_render-all.bat`, `02_optimize-youtube.bat`, `03_generate-thumbnails.bat`
— a ordem numérica indica a sequência de execução.

### #41 — Script de legendas usa _audio_source.json como fonte primária
O `_generate_captions.py` deve usar `_audio_source.json` (word-level timestamps
do Faster-Whisper) como fonte primária, com fallback para `_audio_source.srt`.

### #42 — Correções aplicadas a todos os vídeos
As `TERM_CORRECTIONS` devem ser aplicadas a TODOS os projetos deste tipo
(via `_generate_captions.py`), cobrindo: AI services, academic tools,
databases, concepts, e erros fonéticos do Whisper (tesouros→Thesaurus, etc.).

### #43 — Legendas EN via API, NUNCA via freebuff/manual
**⚠️ CRÍTICO:** A tradução manual por índice (`--provider freebuff`) produz
erros de alinhamento PT↔EN — blocos traduzidos aparecem no timestamp errado.
Usar SEMPRE API (`openai-compat`, `deepseek`, ou `openai`) que traduz cada
bloco pelo texto real, garantindo alinhamento perfeito.

### #44 — OpenAI OAuth e Modelos de Raciocínio (gpt-5.4-mini)
Ao usar o servidor local OpenAI-compatible via `npx openai-oauth` (`http://127.0.0.1:10531/v1`),
modelos de raciocínio como `gpt-5.4-mini` **NÃO suportam o parâmetro `temperature`**.
Passar `temperature=0.1` causa o aviso `temperature is not supported for reasoning models` ou erro.
Omitir o parâmetro `temperature` nas chamadas ao endpoint local.

### #45 — Nomes de Ficheiro YouTube sem Sufixo `-yt`
Nos vídeos otimizados em `renders/youtube/`, os ficheiros MP4 **NÃO devem ter o sufixo `-yt`**
no nome (ex.: `ep01-introducao-ciencia-aberta.mp4` e NÃO `ep01-introducao-ciencia-aberta-yt.mp4`).
O sufixo `-yt` impede que o VLC e players de media leiam e associem automaticamente as legendas `.srt` / `.pt.srt` / `.en.srt`.

### #46 — Tradução por Defeito via `deep-translator` (`deeptrans`)
A configuração base de `_generate_captions.py` deve usar `deeptrans` quando não é indicado outro provider:

```bash
python _generate_captions.py
# equivalente explícito:
python _generate_captions.py --provider deeptrans
```

O provider usa o pacote `deep-translator` com o motor Google Translate: é rápido, gratuito e não requer chave de API. Deve ser o caminho automático para gerar rapidamente legendas PT+EN em novos projetos. Instalar a dependência com `pip install deep-translator`. Tratar falhas de rede ou respostas vazias de forma explícita e interromper a geração; “sem quota de API” não significa que o serviço público tenha disponibilidade garantida nem que possa ser usado em grandes lotes sem validação.

Quando a tradução exigir controlo terminológico, estilo académico ou estabilidade operacional, usar explicitamente `openai-compat`, `deepseek` ou `openai`, mantendo a regra da Lição #43: nunca usar tradução manual por índice para EN.

### #47 — Tratamento de Erros de Quotas de API (Sem Falhas Silenciosas)
Em fornecedores de API comerciais (`openai`, `openai-compat`, `deepseek`), se ocorrer um erro de limite de quota (ex.: `429 credit_balance_exhausted` ou `usage limit has been reached`), o script DEVE lançar uma exceção de imediato. NUNCA copiar o texto original em Português para o ficheiro `.en.srt` como salvaguarda silenciosa.

### #48 — Formatação de Texto nos Thumbnails ffmpeg (Sem `\n` no Windows)
Ao gerar miniaturas com `drawtext` do ffmpeg no Windows, NÃO utilizar caracteres de quebra de linha `\n` na string de texto do parâmetro `text=...`, pois causam erros de sintaxe ou a impressão literal de artefactos como `don...`. Manter o título numa única linha em texto amarelo (`fontcolor=yellow`) sobre caixas de contraste com opacidade (`boxcolor=black@0.80`).

### #49 — Utilitários de Processos em Background (tmux, pmux, psmux)
O ambiente local dispõe dos utilitários de multiplexagem/gestão de processos `tmux`, `pmux` e `psmux`. Podem ser utilizados para orquestrar ou manter execuções persistentes em background se necessário.

### #50 — ⚠️ HARD RULE: Renderização HyperFrames com 12 Workers
**REGRA OBRIGATÓRIA (HARD RULE):** Em todos os projetos futuros, ao configurar a renderização HyperFrames (`01_render-all.bat` ou no comando `npx hyperframes render`), usar SEMPRE **12 workers** (`set WORKERS=12` ou `--workers 12`), em vez de valores conservadores (como 4). Isto aproveita ao máximo a capacidade do sistema para aceleração do paralelismo de frames.

### #51 — SFX em `assets_sfx/` (bug silencioso no copy de templates)
Ao copiar os templates para um projeto novo, os ficheiros `overlay-pop.wav` / `overlay-chime.wav` ficam na **raiz do projeto**, mas o `_build_all.py` espera-os em **`assets_sfx/`**. Se não forem movidos, os SFX NÃO são copiados para os `epXX/` e o render fica sem sons de overlay — sem qualquer erro. **SEMPRE após copiar templates:**
```bash
mkdir -p assets_sfx
cp overlay-pop.wav overlay-chime.wav popup.mp3 chime.mp3 assets_sfx/
```
Verificar com `ls ep01/*.wav` depois de correr o `_build_all.py`.

### #52 — Remover caracteres de caixa (`├ └ │`) da transcrição JSON
As transcrições Whisper de webinars com slides mantêm caracteres de caixa/desenho no início de alguns segmentos (ex.: `├Planos de Gestão Dados...`). Estes caracteres poluem as legendas PT/EN. No `_generate_captions.py`, em `parse_json_transcript`, limpar com:
```python
box_prefix = re.compile(r'^[\u2500-\u257F\u2580-\u259F\s]+')
text = box_prefix.sub('', seg.get('text', '').strip())
```
Aplicar ANTES da correção de termos e da tradução, para que PT e EN fiquem limpos.

### #53 — Launcher com guarda para processos longos (split/legendas)
Ao lançar tarefas longas em background (split, tradução EN), usar um launcher Python com `DETACHED_PROCESS` + ficheiro de PID + **guarda anti-duplicado** (recusar arrancar se o PID anterior ainda estiver vivo). Sem a guarda, lançamentos repetidos criam splits concorrentes que escrevem os mesmos ficheiros e desperdiçam CPU/disco. Nunca confiar em `nohup ... &` via shell do Windows/git-bash: o processo é morto quando o terminal do agente fecha.

### #54 — Tradução EN: openai-oauth pode falhar com token invalidado
O servidor local `openai-oauth` pode devolver `500 Encountered invalidated oauth token` a meio de uma tradução longa. Nesse caso: reiniciar o servidor ou, de forma mais robusta, cair para `--provider deeptrans` (que agora tem retry por bloco no template). O `deeptrans` é o default e funciona sem servidor; falhas esporádicas do endpoint público são resolvidas com retry (4 tentativas com backoff).

### #55 — Verificar credenciais openai-oauth existentes ANTES de fazer novo login
Antes de tentar `npx openai-oauth login` (que é interativo e exige login manual no browser), **tenta primeiro apenas arrancar o servidor** — as credenciais de uma sessão anterior podem continuar válidas:

```bash
npx --yes openai-oauth --detach --port 10531
# Depois verificar se o endpoint responde e listar os modelos disponíveis:
curl http://127.0.0.1:10531/v1/models
```

- Se o endpoint responder com uma lista de modelos → **não é preciso login**; avança direto para a tradução.
- Só se o servidor não arrancar, devolver erro de token invalidado, ou exigir autenticação é que se deve correr `npx --yes openai-oauth login` e pedir ao utilizador a URL para login manual.
- **Nunca** procurar/ler credenciais no disco — basta a tentativa de arranque do servidor.
- Depois da tradução terminar, parar o servidor (`npx --yes openai-oauth stop`) e confirmar que a porta ficou livre.
- O `deeptrans` continua a ser o default sem dependência de servidor; o openai-oauth é a rota alternativa quando se quer tradução por modelo.

### #56 — Verificar se o PDF tem texto extraível ANTES de decidir OCR
Nem todos os PDFs de apresentações são imagens. ANTES de planear OCR, testar com:
```bash
pdftotext -enc UTF-8 apresentacao.pdf - | head -50
```
- **Se devolver texto** → usar `pdftotext -enc UTF-8 apresentacao.pdf _pdf_text.txt` como fonte de terminologia (mais rápido e mais preciso que OCR). Sempre usar `-enc UTF-8` (o default pode sair em Latin-1 com `��`).
- **Se devolver vazio** (slides são imagens) → aí sim fazer OCR (caso Scopus).
O `_pdf_text.txt` serve para: (1) extrair `TERM_CORRECTIONS` com `grep -oiE`, (2) confirmar nomes próprios e siglas (ex.: DUnAs, Dataverse, POLEN, CC0) e (3) escolher termos de âncora para os overlays.

### #57 — Verificar TODAS as âncoras dentro da janela do episódio ANTES do build
Antes de correr o `_build_all.py` final, correr um verificador (`_verify_anchors.py`) que confirma que cada termo de âncora existe DENTRO da janela [start, end) do respetivo episódio na transcrição:
```python
window_text[ep] = " ".join(norm(seg.text) for seg in segments if start <= seg.start < end)
# para cada overlay: any(norm(term) in window_text[ep] for term in terms)
```
Apanhou 1 erro real no DUnAs (termo falava no limite da janela → overlay aparecia no episódio errado). **Usar variações fonéticas reais da transcrição** — o Whisper escreve de forma diferente do esperado:
- `embargad` (não `embargo`) · `5 gb` (não `cinco gb`) · `autenticaç` (não `credenciais`) · `indeterminado` (não `indefinidamente`) · `palavras-chave` (não `keywords`) · `url privad` (não `URL privada`) · `sub-coleç` (não `sub-coleções`)
A forma mais rápida de descobrir variações: `grep` na `_transcript_readable.txt` com prefixos parciais (`embarg`, `autentica`, `indeter`, `palavras`).

### #58 — Colisão de overlays: passe de compressão (backward re-spacing) NUNCA colapsar no mesmo segundo
O posicionamento greedy (`max(8, prev+12, anchor-start+2)`) com clamp `min(end-10, ...)` colapsa os últimos cartões de episódios curtos no MESMO segundo quando as âncoras são tardias (ex.: 2 overlays aos 5:17 de um episódio de 5:27). **Correção — duas passadas:**
```python
# Pass 1: greedy forward (como antes)
placements = [...]
# Pass 2: backward re-spacing — puxa cada cartão para trás mantendo gap de 12s
for i in range(len(placements) - 2, -1, -1):
    placements[i] = min(placements[i], placements[i + 1] - 12.0)
# Se o último ainda ultrapassar o cap, desloca a cauda toda e re-aplica gaps
if placements[-1] > max_ts:
    shift = placements[-1] - max_ts
    placements = [max(8.0, x - shift) for x in placements]
    for i in range(len(placements) - 2, -1, -1):
        placements[i] = min(placements[i], placements[i + 1] - 12.0)
```
Depois de cada build, correr o check de colisões (mesmos `data-start` no SRT de verificação) e exigir `0` duplicados.

### #59 — TERM_CORRECTIONS específicos de repositórios institucionais (DUnAs/Dataverse)
Webinars sobre gestão de dados e repositórios têm terminologia própria que o Whisper raramente acerta:
- `dunas` → `DUnAs` · `dataverse` → `Dataverse` · `zenodo` → `Zenodo` · `polen` → `POLEN`
- `fer` → `FAIR` (e variantes: `princípios fer`, `dados fed`) · `mesh` → `MeSH` · `isni` → `ISNI` · `orcid`/`ursido` → `ORCID`
- `cc0` → `CC0` · `cc by` → `CC BY` · `creative commons` → `Creative Commons` · `doi`/`dois` → `DOI`/`DOIs`
- `readme`/`fecheiro readme` → `README` · `helpdesk` → `helpdesk` · `pivô de dados` (não é palavra mal transcrita, mas manter) · `estandardos` → `standards`
- Projetos de exemplo: `epiboost` → `EpiBoost`, `supralife` → `SUPRALIFE`, `nanotbtec` → `nanoTBTec`
Fazer o scan do PDF com `grep -oiE` e construir o dicionário a partir daí (lição #56).

### #60 — Nº de episódios definido pelos tópicos naturais, NUNCA um número fixo
O número de episódios é determinado pela divisão do vídeo fonte em tópicos principais, não por convenção (12, 10, etc.). Episódios podem ser curtos (~3 min) ou longos (~11 min). No DUnAs (1h25): 13 episódios com durações de 3:42 a 11:35. Processo: ler o índice do PDF → mapear transições na transcrição (keywords como `vamos agora`, `entramos na parte`, `passar`) → cortar em transições naturais → validar que cada janela tem âncoras próprias (lição #57).

### #61 — "Não traduzidos" no validador podem ser texto de UI/nomes próprios idênticos em PT/EN
No `_validate_captions.py`, um bloco PT igual ao EN **não é sempre erro**: pode ser texto de interface do software (ex.: `Add Data, New Dataset.`) ou nomes próprios (ex.: `R3Data.`, `Login.`) que são idênticos nos dois idiomas. Antes de corrigir, inspecionar o bloco; se for UI/nome próprio, é correto — não regenerar.

### #62 — Registar um skill para invocação `/skill:<nome>` (frontmatter obrigatório)
Para que um skill em `.agents/skills/` seja invocável pelo cliente (ex.: `/skill:webinar-to-video`), tem de cumprir 3 requisitos — falhando qualquer um, o skill tool devolve `Skill not found`:

1. **Frontmatter YAML no topo do `SKILL.md`** com `name` (que define o nome de invocação) e `description`:
   ```yaml
   ---
   name: webinar-to-video
   description: Transforma gravações de webinars em séries de vídeos profissionais...
   ---
   ```
   Sem frontmatter, o skill não é listado nem carregável (não basta o `# título` do Markdown).

2. **Nome da pasta == nome de invocação** (`npx skills list` e o skill tool resolvem pelo nome da pasta).

3. **Cópia registada em `.claude/skills/<nome>/`** — onde o cliente descobre os skills instalados (os restantes vivem lá por cópia real, não symlink, no Windows).

**⚠️ Descrição NÃO pode ser demasiado longa numa linha.** Com ~600 caracteres o parser do skill tool rejeita o skill inteiro (`Skill not found`) mesmo com frontmatter e pasta corretos. Manter a `description` ≤ ~400 caracteres numa única linha — os detalhes ficam no corpo do documento. Diagnóstico comprovado: copiar o skill para um nome de teste com descrição curta → carrega; com descrição longa → falha.

**Manutenção:** ao editar o `SKILL.md`, sincronizar também `.claude/skills/<nome>/SKILL.md` (`cp`) para não haver divergência. Depois de qualquer alteração estrutural, confirmar que o skill carrega:
```bash
# via skill tool / cliente: /skill:<nome>  ou  pedir ao agente para carregar o skill
```


---

### #63 — Colocação de overlays por âncora (fix `find_anchor` + ordenação cronológica)

Diagnosticado no projeto `boas-praticas-gdi` (16 ep, 91 overlays): o algoritmo antigo
colocava os últimos 6 overlays do ep01 todos no mesmo segundo final. Duas causas +
o fix completo, já aplicado no template `_build_all.py`:

1. **`find_anchor` word-level casava palavras isoladas.** O matcher antigo aceitava
   `norm(word) in wanted` — ou seja, a palavra "de" casa dentro de "dados de
   investiga". Qualquer overlay depois do primeiro ancorava no primeiro segmento
   após o boundary e empurrava todos os seguintes para o fim. **Fix:** exigir a
   FRASE COMPLETA normalizada dentro da sequência de palavras unidas do segmento
   (`joined.find(wanted)` + posição da palavra correspondente).

2. **Clamp greedy de 12s após a colocação anterior.** Se dois conceitos são
   mencionados em sequência rápida (ex.: "dados de observa" aos 27s logo a seguir
   ao card anterior), o greedy `after = prev + 12` saltava a menção real e ia
   buscar a seguinte (às vezes 4 min depois). **Fix:** âncoras independentes
   (`after = start + 6`, cada card na SUA menção) + clamp de não-sobreposição de
   9s (= duração do card) apenas quando necessário.

3. **Backward pass em ordem da lista, não cronológica.** No ep07, "documento vivo"
   estava listado antes de "vantagens" mas é mencionado 150s depois; o backward
   pass puxava cards anteriores para trás para manter o gap. **Fix:** Pass 2 e Pass 3
   operam em ordem cronológica (sorted por âncora), mapeando de volta para os slots
   da lista no final. Verificar sempre com `python _verify_anchors.py` (Problems: 0)
   E conferir os `data-start` no HTML (grep `data-start=`) contra as menções reais no
   transcript — não basta o verifier passar.

### #64 — ⚠️ CRÍTICO: `.bat` DEVE ter line endings CRLF (Windows), nunca LF-only
Diagnosticado no `boas-praticas-gdi` (ep02 renderizou bem mas o bat reportou
`ERROR: ep02 failed` falso): todos os `.bat` gerados tinham line endings **LF-only**
(Unix) — `CRLF count: 0` — porque o template foi gravado com `\n` em vez de `\r\n`.
O `cmd.exe` do Windows interpreta ficheiros LF-only de forma imprevisível:

- Blocos `if errorlevel 1 ( ... ) else ( ... )` partem-se — o `echo OK: %RENDERS%\%NAME%.mp4`
  cola fragmentos (`'RKERSRENDERSNAME.mp4"'` = `WORKERS`+`RENDERS`+`NAME.mp4`).
- Os `call :render` saltam episódios de forma errática (só renderizou 15/16; na 2ª
  execução "começou pelo 02").
- O render em si funciona (o `npx` corre bem) mas o controlo de fluxo do batch fica corrupto.

**Sintoma típico:** o MP4 é gerado com sucesso, mas o batch imprime `is not recognized
as an internal or external command` com fragmentos de variáveis colados e reporta
`ERROR: <ep> failed` falso.

**Verificação (fazer SEMPRE após criar/editar qualquer `.bat`):**
```bash
python -c "d=open('01_render-all.bat','rb').read(); print('CRLF' if b'\r\n' in d else 'LF-only')"
```

**Correção:**
```bash
python -c "d=open('f.bat','rb').read().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'); open('f.bat','wb').write(d)"
```

**Regra:** todos os ficheiros `.bat` dos templates E de cada projeto (01/02/03_*.bat,
`_split_*.bat`, etc.) devem ser gravados com CRLF. Aplicar a todos os projetos da série
quando se corrigir um template. Adicionar esta verificação ao checklist final de cada
projeto novo (antes do `01_render-all.bat`).

### #65 — Âncoras de listas sequenciais: usar a FRASE DE INTRODUÇÃO da etapa, nunca a keyword genérica
Diagnosticado no `boas-praticas-gdi` ep02 (ciclo de vida dos dados, 7 etapas): os cartões
"5. Preservação" e "7. Reutilização" apareciam fora de ordem (aos 32s e 65s em vez de
~182s e ~268s) porque os termos de âncora genéricos casavam com menções EARLIER ditas
noutras secções:

- `"preserva"` casou com "quanto à sua **preservação**" dita durante a etapa 1
  (Planeamento, ~30s) em vez de "a etapa da **preservação**" (~180s).
- `"reutiliza"` casou com "dados de outros para **reutilização**" dita durante a etapa 2
  (Recolha, ~61s) em vez de "**fase final**" (~266s).

**Regra platinum para listas sequenciais (1→N):** quando os overlays são passos de uma
lista, os termos de âncora devem ser a frase que INTRODUZ cada passo (a transição do
orador), não a keyword do conceito. Exemplo:

| Etapa | Âncora errada (casa cedo) | Âncora correta (introdução) |
|-------|---------------------------|------------------------------|
| 5. Preservação | `["preserva"]` | `["etapa da preserva"]` |
| 7. Reutilização | `["reutiliza"]` | `["fase final", "processo de reutiliza"]` |

Depois de corrigir, verificar a ORDEM CRONOLÓGICA dos `data-start` no HTML
(`grep data-start=`) — para listas sequenciais, os timestamps devem estar ordenados
1→N. Se dois cartões ficarem trocados, procurar no transcript as frases de transição
reais ("Depois, numa segunda fase…", "A fase seguinte é…", "Depois numa fase final…").

### #66 — `--model` NÃO era passado ao `_resolve_provider` (bug ignorava o modelo pedido)
Diagnosticado no `boas-praticas-gdi` (16 ep): ao correr
`python _generate_captions.py --provider openai-compat --model gpt-5.6-luna`,
**o log mostrava `Translating via openai-compat (gpt-5.4-mini)`** — o `--model` era
ignorado e o script usava sempre o `TRANSLATION_MODEL` fixo. Causa: `_resolve_provider()`
recebia `(provider, api_key, base_url)` mas nunca recebia `args.model`, e
`main()` chamava-o sem o passar. Resultado prático: o modelo pedido não era usado
(e.g. `gpt-5.4-mini` atingia "The usage limit has been reached" enquanto o
`gpt-5.6-luna` pedido ficava por usar).

**Fix (aplicado no projeto e no template):**
```python
def _resolve_provider(provider, api_key, base_url, model_override: str | None = None):
    ...
    elif provider == 'openai-compat':
        ...
        model = model_override or TRANSLATION_MODEL   # ← usa o --model

# main():
provider_name, key, url, model = _resolve_provider(
    args.provider, None, args.base_url, args.model   # ← passar SEMPRE args.model
)
```

**Verificação:** o log da tradução deve mostrar o modelo pedido:
`Translating via openai-compat (gpt-5.6-luna)...` — se mostrar outro modelo,
procurar o bug no `_resolve_provider` / chamada em `main()`.

### #67 — Lançar tarefas longas no Windows: `Start-Process` com caminho absoluto do python
Para traduções EN longas (16 ep ≈ 15-20 min via deeptrans) NÃO usar
`nohup ... &` do git-bash (o processo morre quando a sessão do agente fecha).
**Preferir o launcher do template `_launch_captions.py`** (lição #53: `DETACHED_PROCESS`
+ ficheiro de PID + guarda anti-duplicado) quando existir. Alternativa direta:
usar PowerShell `Start-Process` com o caminho ABSOLUTO do interpretador Python
e verificar por PIDs:
```bash
powershell -NoProfile -Command "Start-Process -FilePath 'C:\\Users\\<user>\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe' -ArgumentList '_generate_captions.py','--provider','deeptrans' -WindowStyle Hidden"
```

**⚠️ Não confundir pai/filho com duplicados:** o `python.exe` de uma venv (uv/hermes)
é um *shim* que invoca o interpretador real (ex.: `uv\python\cpython-3.11...\python.exe`).
`wmic` mostra 2 processos `_generate_captions.py` (pai+filho) — é UMA execução só,
não uma corrida. NUNCA matar um dos dois à toa; verificar primeiro se é mesmo
uma segunda execução (`--provider` e argumentos idênticos + PIDs pai/filho).
Monitorizar progresso pela contagem de ficheiros gerados (`ls ep*/ep*_video.en.srt | wc -l`)
em vez de depender do stdout (o Python bufferiza quando redirecionado).

## Templates e Scripts Base

Os templates estão disponíveis em:
```
.agents/skills/webinar-to-video/templates/
```

### Lista de templates:

| Ficheiro | Descrição |
|----------|-----------|
| `_build_all.py` | ⭐ Script principal — gera index.html para todos os episódios |
| `_generate_captions.py` | Legendas bilingues PT+EN via API |
| `_generate_srt.py` | SRT de verificação para VLC |
| `_fix_capitalization.py` | Regra platinum de capitalização |
| `_split_video.py` | Split do vídeo fonte com audio_enhance |
| `_transcribe.py` | Transcrição Faster-Whisper |
| `_verify_anchors.py` | Verifica âncoras dos overlays dentro da janela de cada episódio (lição #57) |
| `_launch_split.py` | Launcher destacado do split com guarda anti-duplicado (lição #53) |
| `_launch_captions.py` | Launcher destacado da tradução EN (lição #53) |
| `_validate_captions.py` | Valida alinhamento PT/EN (timestamps iguais, blocos não traduzidos) |
| `generate-thumbnails.py` | Geração de thumbnails com ffmpeg |
| `01_render-all.bat` | Render de todos os episódios |
| `02_optimize-youtube.bat` | Otimização CRF 18 + cleanup |
| `03_generate-thumbnails.bat` | Wrapper para thumbnails |
| `YOUTUBE_METADATA.md` | Template de metadata YouTube |
| `DESIGN.md` | Template de notas de design |

### Como usar para um projeto novo:

```bash
# 1. Criar diretório do projeto
mkdir videos/meu-webinar && cd videos/meu-webinar

# 2. Copiar templates
cp -r .agents/skills/webinar-to-video/templates/* ./

# 3. Criar estrutura de episódios
mkdir ep01 ep02 ... ep10 assets_sfx renders

# 4. Copiar SFX
cp videos/pesquisa-info-cientifica/assets_sfx/* assets_sfx/

# 5. Personalizar _build_all.py (formato moderno com âncoras):
#    - EPISODES (títulos, durações, subtítulos)
#    - OVERLAYS (conteúdo de cada episódio)
#      Formato: ("f1", kind, "TAG", "Title", "Body", ["anchor terms"], True|False)
#      Os timestamps são calculados automaticamente via find_anchor na
#      transcrição (lição #57) — NÃO definir timestamps manuais.

# 5b. Verificar âncoras ANTES de gerar:
#    python _verify_anchors.py   # deve dar Problems: 0

# 6. Personalizar _generate_captions.py:
#    - EPISODE_BOUNDARIES (iguais às do _split_video.py)
#    - TERM_CORRECTIONS
#    - RENDER_NAMES

# 7. Seguir a pipeline (Fase 1 → Fase 8)
```
