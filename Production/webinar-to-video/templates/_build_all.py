#!/usr/bin/env python3
"""Build HyperFrames episodes for a webinar-to-video project.

TEMPLATE — Customize the sections marked with 🔧 for each project:
  🔧 EPISODES  — (label, abs_start_s, abs_end_s, title, subtitle)
  🔧 OVERLAYS  — content cards per episode, anchored to the transcript

The data below is SAMPLE data from the DUnAs project (13 episodes) — replace
it entirely with your project's episodes and overlays. Overlay timestamps are
NOT set manually: they are computed automatically by find_anchor() against
the word/segment timestamps in _audio_source.json (lesson #57). Each anchor is
delayed by two seconds so the card appears shortly after the speaker
introduces the concept, never before it.

Run order:
  1. python _verify_anchors.py   # must print Problems: 0
  2. python _build_all.py        # generates index.html + SFX + verify SRTs + PT captions
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

BASE = Path(__file__).resolve().parent
SFX_DIR = BASE / "assets_sfx"
SFX_POP = "overlay-pop.wav"
SFX_CHIME = "overlay-chime.wav"

# 🔧 CUSTOMIZE: Episode list (SAMPLE from DUnAs — replace with your own)
EPISODES = [
    ("ep01", 0.0, 327.0, "Dados de investigação: conceitos essenciais", "O que são dados e porque depositá-los num repositório"),
    ("ep02", 327.0, 594.0, "Ciclo de vida e níveis de processamento dos dados", "Fases, dados brutos e dados processados"),
    ("ep03", 594.0, 816.0, "Requisitos dos financiadores: Comissão Europeia e FCT", "Obrigações para a gestão de dados de investigação"),
    ("ep04", 816.0, 1069.0, "O repositório institucional DUnAs", "Apresentação e objetivos do repositório de dados da UA"),
    ("ep05", 1069.0, 1383.0, "Estrutura do DUnAs: coleções, datasets e metadados", "Como o Dataverse organiza a informação"),
    ("ep06", 1383.0, 1799.0, "Papéis, permissões, licenças e níveis de acesso", "Quem faz o quê e como se define o acesso aos dados"),
    ("ep07", 1799.0, 2155.0, "Funcionalidades: guestbook, templates, estatísticas e harvesting", "Ferramentas que facilitam a gestão e a descoberta"),
    ("ep08", 2155.0, 2634.0, "Curadoria e fluxo de publicação", "Do rascunho à publicação, com revisão da biblioteca"),
    ("ep09", 2634.0, 3073.0, "Depósito no DUnAs: pré-requisitos e criação de datasets", "Termos, guias de apoio e primeiros passos"),
    ("ep10", 3073.0, 3740.0, "Demonstração: página inicial, coleções e login", "Visita guiada ao repositório"),
    ("ep11", 3740.0, 4435.0, "Criar um dataset: campos de metadados", "Preencher título, autores, palavras-chave e mais"),
    ("ep12", 4435.0, 4910.0, "Formatos, licenças, versões e submissão", "Boas práticas finais antes de publicar"),
    ("ep13", 4910.0, 5143.0, "Perguntas e respostas e encerramento", "Preservação, contas de teste e contactos de apoio"),
]

# 🔧 CUSTOMIZE: Overlay definitions per episode (SAMPLE from DUnAs — replace)
# (id, kind, tag, title, body, anchor terms, fullscreen)
OVERLAYS = {
    "ep01": [
        ("f1", "concept", "CONCEITO", "Dados de investigação", "Todos os dados produzidos, obtidos ou usados no decurso de uma investigação científica.", ["dados de investigação", "dados de investiga"], True),
        ("f2", "concept", "CONCEITO", "Dados que acompanham as publicações", "Os dados são depositados para validar os resultados descritos nas publicações científicas.", ["acompanhar essas publica", "validam os resultados"], False),
        ("f3", "example", "EXEMPLO", "Exemplos de dados", "Entrevistas, inquéritos, resultados de laboratório, registos numéricos, imagens e vídeos.", ["entrevistas", "inquéritos"], False),
        ("f4", "concept", "CONCEITO", "Dados em vários formatos", "Os dados podem ter variados formatos e origens, consoante a área científica.", ["instrumentos de medição", "dependendo do contexto"], False),
        ("f5", "tip", "DICA", "Repositórios para partilhar", "O depósito em repositório faz sentido para conjuntos de dados já partilháveis.", ["repositório serve", "partilha"], False),
    ],
    "ep02": [
        ("f1", "structure", "ESTRUTURA", "Ciclo de vida dos dados", "Ao longo da investigação, os dados passam por várias fases de gestão.", ["ciclo de vida", "várias fases"], True),
        ("f2", "concept", "CONCEITO", "Várias fases de gestão", "Planear, recolher, processar, analisar, preservar, partilhar e reutilizar.", ["várias fases", "processo de investiga"], False),
        ("f3", "concept", "CONCEITO", "Dados brutos", "Os dados como são recolhidos em bruto, antes de qualquer tratamento.", ["dados brutos"], False),
        ("f4", "concept", "CONCEITO", "Dados processados", "Dados já tratados e estruturados, prontos para partilha em acesso aberto.", ["processados"], False),
        ("f5", "concept", "CONCEITO", "Acesso aberto a dados processados", "A partilha e a abertura de dados ocorrem após o processamento e o depósito.", ["dados abertos", "abertura dos dados"], True),
        ("f6", "concept", "CONCEITO", "Plano de Gestão de Dados", "Documento que descreve como os dados serão geridos ao longo do projeto.", ["plano de gestão de dados"], False),
    ],
    "ep03": [
        ("f1", "structure", "ESTRUTURA", "Requisitos dos financiadores", "CE e FCT impõem requisitos de acesso aberto para dados de investigação.", ["comissão europeia", "requisitos"], True),
        ("f2", "important", "IMPORTANTE", "Comissão Europeia: gestão adequada", "O Grant Agreement do Horizonte Europa exige uma gestão adequada dos dados.", ["grant agreement", "horizonte europa"], False),
        ("f3", "concept", "CONCEITO", "Princípios FAIR", "Findable, Accessible, Interoperable, Reusable: dados localizáveis, acessíveis, interoperáveis e reutilizáveis.", ["princípios fer", "principios fer", "fer"], True),
        ("f4", "important", "IMPORTANTE", "PGD obrigatório nos primeiros 6 meses", "O plano de gestão de dados deve ser entregue nos primeiros seis meses.", ["6 meses", "primeiros seis meses"], False),
        ("f5", "tool", "FERRAMENTA", "FCT: política de dados", "A FCT promove o acesso aberto e a disponibilização dos dados de investigação.", ["fct"], False),
        ("f6", "concept", "CONCEITO", "Licenças de reutilização", "CC0 e CC BY definem como os dados podem ser reutilizados.", ["cc0", "licença"], False),
    ],
    "ep04": [
        ("f1", "concept", "CONCEITO", "Repositório institucional DUnAs", "Repositório institucional de dados de investigação da Universidade de Aveiro.", ["dunas"], True),
        ("f2", "tool", "FERRAMENTA", "Baseado no software Dataverse", "Plataforma open source desenvolvida pela Universidade de Harvard.", ["dataverse"], False),
        ("f3", "concept", "CONCEITO", "Visibilidade e reprodutibilidade", "Depositar dados aumenta a visibilidade e permite reproduzir resultados.", ["visibilidade"], False),
        ("f4", "concept", "CONCEITO", "Citação de datasets", "Os dados podem ser citados e referenciados como publicações.", ["citação", "citar"], False),
        ("f5", "concept", "CONCEITO", "Fonte de informação", "O repositório institucional é uma fonte confiável de dados da comunidade UA.", ["repositório", "fonte"], False),
    ],
    "ep05": [
        ("f1", "structure", "ESTRUTURA", "Estrutura do Dataverse", "O software organiza-se em coleções, sub-coleções e datasets.", ["estruturado", "coleções"], True),
        ("f2", "concept", "CONCEITO", "Coleções e sub-coleções", "As coleções podem ter sub-coleções, seguindo a estrutura orgânica da universidade.", ["sub-cole", "coleções"], False),
        ("f3", "concept", "CONCEITO", "Datasets", "Dentro das coleções organizam-se os datasets com metadados e ficheiros.", ["datasets", "dataset"], False),
        ("f4", "concept", "CONCEITO", "Metadados de citação", "Campos que geram a citação do dataset e descrevem a informação.", ["metadados"], False),
        ("f5", "concept", "CONCEITO", "Esquemas disciplinares", "Geospatial, Ciências Sociais, Astronomia e Astrofísica, Ciências da Vida.", ["astronomia", "disciplinares"], False),
        ("f6", "concept", "CONCEITO", "Papéis e permissões", "O sistema permite atribuir papéis e permissões em vários níveis.", ["administrador", "permissões"], False),
    ],
    "ep06": [
        ("f1", "structure", "ESTRUTURA", "Papéis no repositório", "Administrador, contribuidor e curador definem quem pode fazer o quê.", ["administrador"], True),
        ("f2", "concept", "CONCEITO", "Permissões em vários níveis", "Permissões ao nível da coleção, do dataset e do ficheiro.", ["nível da coleç", "permissões"], False),
        ("f3", "concept", "CONCEITO", "Licenças Creative Commons", "Licenças CC disponíveis no repositório para definir a reutilização.", ["creative commons", "licenças"], False),
        ("f4", "concept", "CONCEITO", "Acesso aberto", "Ficheiros abertos e visualizáveis por qualquer pessoa, sem restrições.", ["acesso aberto", "aberto"], False),
        ("f5", "important", "IMPORTANTE", "Embargo", "Ficheiros fechados até uma data, com justificação válida.", ["embargad"], True),
        ("f6", "concept", "CONCEITO", "Acesso restrito", "Ficheiros fechados, mas com possibilidade de pedido de acesso.", ["restrito"], False),
        ("f7", "concept", "CONCEITO", "Versões automáticas", "Cada alteração gera uma nova versão, preservando o histórico.", ["versões", "versão"], False),
        ("f8", "concept", "CONCEITO", "URL privada", "Partilha de datasets para revisão por pares através de link privado.", ["url privad"], False),
    ],
    "ep07": [
        ("f1", "concept", "CONCEITO", "Guestbook", "Registo personalizado do que se pretende saber sobre quem descarrega os ficheiros.", ["guestbook"], False),
        ("f2", "concept", "CONCEITO", "Templates de datasets", "Modelos de datasets com campos pré-definidos para depósitos recorrentes.", ["template"], False),
        ("f3", "concept", "CONCEITO", "Estatísticas de uso", "Métricas de visualizações, downloads e citações por dataset.", ["estatísticas"], False),
        ("f4", "concept", "CONCEITO", "Harvesting e apontadores", "Datasets podem ser colhidos de repositórios externos, como o Zenodo, com um apontador.", ["apontador", "zenodo"], True),
        ("f5", "tip", "DICA", "Página inicial e destaques", "A página inicial destaca coleções de primeiro nível e datasets recentes.", ["página inicial", "destaque"], False),
    ],
    "ep08": [
        ("f1", "concept", "CONCEITO", "Curadoria de dados", "Boas práticas e checklist de curadoria antes do depósito.", ["curadoria"], True),
        ("f2", "tip", "DICA", "Checklist de curadoria", "Lista de boas práticas essenciais para preparar os dados.", ["checklist"], False),
        ("f3", "structure", "ESTRUTURA", "Fluxo de publicação", "Criação do dataset, submissão, revisão e publicação pela biblioteca.", ["criação de dataset", "criar um dataset"], True),
        ("f4", "concept", "CONCEITO", "Submissão para revisão", "Após submissão, o dataset fica em revisão e deixa de poder ser editado.", ["revisão"], False),
        ("f5", "important", "IMPORTANTE", "Devolução para correção", "A biblioteca pode devolver o dataset ao depositante para ajustes.", ["devolv"], False),
        ("f6", "concept", "CONCEITO", "Publicação e DOI", "A biblioteca publica, ativa o DOI e torna os metadados públicos.", ["publica", "doi"], False),
        ("f7", "concept", "CONCEITO", "Pivô de dados", "Cada unidade de investigação tem um pivô de dados que administra a coleção.", ["pivô"], False),
        ("f8", "concept", "CONCEITO", "Papel da biblioteca", "A biblioteca faz curadoria dos metadados e tem a palavra final na publicação.", ["biblioteca"], False),
    ],
    "ep09": [
        ("f1", "structure", "ESTRUTURA", "Depósito de dados no DUnAs", "A parte prática: criação de datasets e publicação de dados.", ["criação de dataset", "depósito de dados"], True),
        ("f2", "important", "IMPORTANTE", "Termos e critérios de depósito", "Ler os termos para garantir direitos, copyright e anonimização dos dados.", ["termos e critérios", "termos e criterios"], False),
        ("f3", "important", "IMPORTANTE", "Direitos e anonimização", "Garantir que os dados não violam direitos de terceiros nem identificam pessoas.", ["anonimiza"], False),
        ("f4", "tool", "FERRAMENTA", "Guias de apoio", "Guia de preenchimento de metadados e guia temático do DUnAs.", ["guia"], False),
        ("f5", "concept", "CONCEITO", "Autenticação institucional", "Acesso com as credenciais da Universidade de Aveiro; primeira entrada cria a conta.", ["autenticaç", "login"], False),
        ("f6", "concept", "CONCEITO", "Criar novo dataset", "Clicar em novo dataset para começar o depósito.", ["novo dataset"], False),
        ("f7", "concept", "CONCEITO", "Campos mínimos", "A primeira vista mostra o mínimo de campos obrigatórios e recomendados.", ["mínimo", "conjunto de dados"], False),
    ],
    "ep10": [
        ("f1", "structure", "ESTRUTURA", "Página inicial do DUnAs", "Coleções de primeiro nível e datasets recentes em destaque.", ["página inicial"], True),
        ("f2", "concept", "CONCEITO", "Coleções de primeiro nível", "As coleções das unidades de investigação, ainda em criação.", ["primeiro nível", "coleções"], False),
        ("f3", "concept", "CONCEITO", "Página do dataset", "Citação, DOI, metadados essenciais, ficheiros e estatísticas de uso.", ["doi", "citação"], False),
        ("f4", "concept", "CONCEITO", "Harvesting de repositórios externos", "Datasets do Zenodo aparecem com ícone e ligação para a origem.", ["zenodo"], True),
        ("f5", "concept", "CONCEITO", "Login institucional", "Autenticação com as credenciais universais da Universidade de Aveiro.", ["autenticaç", "login"], False),
        ("f6", "concept", "CONCEITO", "Permissões do utilizador", "As funcionalidades visíveis dependem dos papéis e permissões atribuídos.", ["permissões", "papéis"], False),
    ],
    "ep11": [
        ("f1", "structure", "ESTRUTURA", "Campos obrigatórios e recomendados", "Os campos com asterisco são obrigatórios; os restantes devem ser preenchidos quando aplicável.", ["asterisco"], True),
        ("f2", "concept", "CONCEITO", "Título do dataset", "O título deve identificar claramente o conteúdo dos dados.", ["título"], False),
        ("f3", "concept", "CONCEITO", "Autores e afiliações", "O utilizador entra como autor por defeito; é possível adicionar mais autores e afiliações.", ["afilia", "autores"], False),
        ("f4", "concept", "CONCEITO", "Palavras-chave", "Termos que descrevem o dataset, com opção de vocabulários controlados.", ["palavras-chave", "keywords"], False),
        ("f5", "concept", "CONCEITO", "Publicação relacionada e DOI", "Referência bibliográfica do artigo associado, com DOI e ligação.", ["doi", "publicação"], False),
        ("f6", "concept", "CONCEITO", "Produtor e projeto", "O campo produtor identifica o projeto e funciona como filtro de descoberta.", ["produtor", "projeto"], False),
        ("f7", "concept", "CONCEITO", "Financiamento", "Indicar se o dataset é financiado, com número de grant e financiador.", ["financiamento", "financiad"], False),
        ("f8", "tip", "DICA", "README", "Ficheiro que explica a estrutura, as condições de acesso e o software necessário.", ["readme"], True),
        ("f9", "concept", "CONCEITO", "Guardar em rascunho", "O primeiro save guarda o dataset em formato draft, ainda não publicado.", ["guardar", "draft"], False),
    ],
    "ep12": [
        ("f1", "concept", "CONCEITO", "Formatos preferenciais", "Preferir formatos abertos e normalizados reconhecidos pela comunidade científica.", ["formatos preferenciais", "formatos abertos"], True),
        ("f2", "important", "IMPORTANTE", "Ficheiros grandes", "Para ficheiros acima de 5 GB, contactar o helpdesk para depósito mediado.", ["5 gb", "cinco gb"], False),
        ("f3", "important", "IMPORTANTE", "Sem dados pessoais", "O investigador é responsável por não depositar dados privados, confidenciais ou pessoais.", ["confidenciais", "pessoais"], False),
        ("f4", "concept", "CONCEITO", "Licença CC0 por defeito", "Domínio público para dados sem copyright; atribuição opcional com CC BY.", ["cc0", "cc by"], False),
        ("f5", "concept", "CONCEITO", "Termos de uso personalizados", "É possível definir termos de uso específicos com formulários ou licenças.", ["termos de uso", "licenças"], False),
        ("f6", "concept", "CONCEITO", "Versões automáticas", "Alterações ao dataset geram novas versões e preservam o histórico.", ["versões", "versão"], False),
        ("f7", "concept", "CONCEITO", "Publicação pela biblioteca", "A biblioteca revê os metadados e publica o dataset.", ["biblioteca", "publica"], False),
    ],
    "ep13": [
        ("f1", "structure", "ESTRUTURA", "Perguntas e respostas", "Dúvidas da audiência sobre preservação, contas e funcionamento do DUnAs.", ["pergunta", "questões"], True),
        ("f2", "concept", "CONCEITO", "Preservação a longo prazo", "Os datasets são preservados por tempo indeterminado até existir política formal.", ["indeterminado", "preserva"], False),
        ("f3", "tip", "DICA", "Criar conta para testar", "É possível criar conta com o login universal da UA, embora o acesso seja por coleção.", ["conta", "login"], False),
        ("f4", "concept", "CONCEITO", "Contactos de apoio", "Apoio das Bibliotecas UA e do Aveiro RDM Center para questões e depósitos.", ["contato", "contacto", "bibliotecas"], False),
        ("f5", "concept", "CONCEITO", "Obrigado por assistir", "Mais informação nos guias das Bibliotecas UA e no repositório DUnAs.", ["obrigada", "obrigado"], False),
    ],
}

COLORS = {
    "concept": ("#FFFFFF", "#14B8A6"), "structure": ("#FFFFFF", "#8B5CF6"),
    "tool": ("#0B1120", "#F97316"), "tip": ("#0B1120", "#FACC15"),
    "important": ("#FFFFFF", "#EF4444"), "example": ("#FFFFFF", "#0EA5E9"),
}

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;overflow:hidden;background:#000;font-family:Inter,Arial,sans-serif}video.full-bg{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}.overlay-bottom{position:absolute;bottom:80px;left:80px;right:80px;z-index:10;display:flex;flex-direction:column;gap:14px;background:rgba(11,17,32,.95);padding:28px 36px}.overlay-center{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:10;display:flex;flex-direction:column;align-items:center;gap:20px;text-align:center}.overlay-title{font-size:44px;font-weight:700;color:#fff;line-height:1.2}.overlay-body{font-size:24px;font-weight:500;color:#e2e8f0;max-width:1050px;line-height:1.5}.concept-tag{display:inline-block;padding:8px 22px;font-size:18px;font-weight:700;letter-spacing:.08em}.hl{color:#f97316}.tl{color:#14b8a6}.pl{color:#8b5cf6}"""


def norm(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def load_segments() -> list[dict]:
    data = json.loads((BASE / "_audio_source.json").read_text(encoding="utf-8-sig"))
    return data.get("segments", [])


def find_anchor(segments: list[dict], start: float, end: float, terms: list[str], after: float, fallback_index: int = 0, fallback_total: int = 1) -> float:
    """Find the earliest word-level match for a topic inside an episode.

    The word-level matcher requires the FULL normalized phrase to appear in
    the joined word sequence of a segment (lesson: single-word substring
    matches like "de" inside "dados de investiga" pull anchors to the first
    segment past the boundary and cascade every later card to the episode
    end).
    """
    candidates = []
    for seg in segments:
        if not (start <= seg.get("start", 0) < end):
            continue
        text = norm(seg.get("text", ""))
        words = seg.get("words") or []
        for term in terms:
            wanted = norm(term)
            if wanted not in text:
                continue
            matched_at = float(seg.get("start", 0))
            if words:
                word_texts = [norm(str(w.get("word", ""))) for w in words]
                joined = " ".join(word_texts)
                idx = joined.find(wanted)
                if idx >= 0:
                    prefix = joined[:idx].strip()
                    pos = len(prefix.split()) if prefix else 0
                    if pos < len(words):
                        matched_at = float(words[pos].get("start", matched_at))
            candidates.append(matched_at)
            break
    candidates = [x for x in candidates if x >= after]
    if candidates:
        return min(candidates)
    # Safe deterministic fallback: distribute unmatched topics through the
    # episode instead of collapsing several cards onto the same final second.
    span = max(30.0, (end - start) - 24.0)
    distributed = start + 12.0 + span * ((fallback_index + 1) / (fallback_total + 1))
    return max(after, distributed)


def overlay_html(oid, tag, title, body, fullscreen, tag_fg, tag_bg, ts):
    cls = "overlay-center" if fullscreen else "overlay-bottom"
    style = "background:rgba(11,17,32,.95);inset:0;transform:none;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px" if fullscreen else ""
    title_size = "56px" if fullscreen else "44px"
    return f'''      <div id="{oid}" class="clip {cls}" data-start="{ts:.2f}" data-duration="9" data-track-index="3" style="{style}">
        <div class="concept-tag" id="{oid}b" style="background:{tag_bg};color:{tag_fg};font-size:{"22px" if fullscreen else "18px"};padding:10px 24px">{escape(tag)}</div>
        <div class="overlay-title" id="{oid}t" style="font-size:{title_size}">{title}</div>
        {f'<div class="overlay-body" id="{oid}s">{body}</div>' if fullscreen else ''}
      </div>'''


def build_index(ep, duration, title, subtitle, ep_number, next_title, next_subtitle, overlays, sfx):
    outro_start = max(0, duration - 5)
    return f'''<!doctype html><html lang="pt"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{CSS}</style></head><body><div id="root" data-composition-id="{ep}" data-start="0" data-duration="{duration:.0f}" data-width="1920" data-height="1080">
      <video id="main-video" class="clip full-bg" data-start="0" data-duration="{duration:.0f}" data-track-index="0" src="{ep}_video.mp4" muted playsinline></video>
      <audio id="main-audio" data-start="0" data-duration="{duration:.0f}" data-track-index="1" src="{ep}_video.mp4" data-volume="1"></audio>
      <div id="ov-intro" class="clip overlay-center" data-start="0" data-duration="5" data-track-index="2" style="background:rgba(11,17,32,.95);inset:0;transform:none;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px"><div class="concept-tag" id="t0b" style="font-size:24px;padding:12px 28px">EPISÓDIO {ep_number}</div><div class="overlay-title" id="t0t" style="font-size:68px">{title}</div><div class="overlay-body" id="t0s">{subtitle}</div></div>
      <div id="ov-outro" class="clip overlay-center" data-start="{outro_start:.2f}" data-duration="5" data-track-index="2" style="background:rgba(11,17,32,.95);inset:0;transform:none;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px"><div class="concept-tag" id="t9b" style="background:#8B5CF6;color:#fff;font-size:22px;padding:10px 24px">PRÓXIMO EPISÓDIO</div><div class="overlay-title" id="t9t" style="font-size:56px">{next_title}</div><div class="overlay-body" id="t9s">{next_subtitle}</div></div>
{overlays}
{sfx}
    </div><script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});tl.from("#main-video",{{opacity:0,duration:.8,ease:"power2.in"}},0);tl.from("#t0b",{{y:-30,opacity:0,duration:.4,ease:"expo.out"}},.2);tl.from("#t0t",{{y:40,opacity:0,duration:.5,ease:"power3.out"}},.4);tl.from("#t0s",{{y:20,opacity:0,duration:.4,ease:"power2.out"}},.6);tl.to("#ov-intro",{{opacity:0,duration:.3,ease:"power2.in"}},4.7);tl.set("#ov-intro",{{opacity:0}},5);tl.from("#t9b",{{y:-30,opacity:0,duration:.5,ease:"expo.out"}},{outro_start:.2}+.3);tl.from("#t9t",{{y:40,opacity:0,duration:.6,ease:"power3.out"}},{outro_start:.2}+.5);tl.from("#t9s",{{y:20,opacity:0,duration:.5,ease:"power2.out"}},{outro_start:.2}+.8);
{''.join(f'tl.from("#{o[0]}b",{{x:-20,opacity:0,duration:.3,ease:"expo.out"}},{o[6]:.2f}+.1);tl.from("#{o[0]}t",{{scale:.9,opacity:0,duration:.45,ease:"back.out(1.4)"}},{o[6]:.2f}+.3);' + (f'tl.from("#{o[0]}s",{{y:15,opacity:0,duration:.35,ease:"power2.out"}},{o[6]:.2f}+.7);' if o[4] else '') for o in overlays_data_current)}window.__timelines["{ep}"]=tl;</script></body></html>'''

# Global used only while composing one index; keeps template compact.
overlays_data_current = []


def main() -> int:
    global overlays_data_current
    segments = load_segments()
    total = 0
    for idx, (ep, start, end, title, subtitle) in enumerate(EPISODES, 1):
        ep_dir = BASE / ep
        ep_dir.mkdir(exist_ok=True)
        for name in (SFX_POP, SFX_CHIME):
            src = SFX_DIR / name
            if src.exists(): shutil.copy2(src, ep_dir / name)
        if idx < len(EPISODES):
            next_title = EPISODES[idx][3]
            next_sub = EPISODES[idx][4]
        else:
            next_title = "Obrigado por assistir"
            next_sub = "Bibliotecas da Universidade de Aveiro"
        blocks=[]; sfx=[]; overlays_data_current=[]
        episode_overlays = OVERLAYS[ep]
        max_ts = max(30.0, end - start - 10)
        # ── Pass 1: independent anchors — each card is placed at its OWN
        # earliest mention (after the 6s intro), NOT deferred 12s past the
        # previous placement (lesson: greedy deferral pushed later cards to
        # the episode end when mentions cluster).
        anchors = []
        for overlay_index, (oid, kind, tag, ov_title, body, terms, fullscreen) in enumerate(episode_overlays):
            anchors.append(find_anchor(segments, start, end, terms, start + 6.0, overlay_index, len(episode_overlays)))
        # ── Pass 2: no-overlap clamp — 9s = card duration. Only push a card
        # forward when it would overlap the previous card; otherwise keep its
        # own anchor so it appears right after the topic is mentioned.
        # IMPORTANT: process cards in chronological ANCHOR order, not list
        # order (lesson: ep07 listed "documento vivo" before "vantagens" even
        # though "vantagens" is mentioned 150s earlier — clamping in list
        # order pushed both to the episode end).
        order = sorted(range(len(episode_overlays)), key=lambda i: anchors[i])
        sorted_ts: dict[int, float] = {}
        prev_ts = 0.0
        for pos, i in enumerate(order):
            ts = anchors[i] - start + 2.0
            if pos == 0:
                ts = max(8.0, ts)
            else:
                ts = max(ts, prev_ts + 9.0)
            sorted_ts[i] = min(max_ts, ts)
            prev_ts = sorted_ts[i]
        placements = [sorted_ts[i] for i in range(len(episode_overlays))]
        # ── Pass 3: backward re-spacing — never collapse cards onto the same
        # second near the end (lesson: duplicate overlay timestamps). Also
        # operates in CHRONOLOGICAL (sorted) order, like Pass 2, so a card
        # whose mention is early is never pulled toward a later card that just
        # happens to follow it in the OVERLAYS list. If the final card overruns
        # the cap, shift the whole tail and re-enforce gaps.
        ordered_ts = [sorted_ts[i] for i in order]
        for pos in range(len(ordered_ts) - 2, -1, -1):
            ordered_ts[pos] = min(ordered_ts[pos], ordered_ts[pos + 1] - 9.0)
        if ordered_ts and ordered_ts[-1] > max_ts:
            shift = ordered_ts[-1] - max_ts
            ordered_ts = [max(8.0, x - shift) for x in ordered_ts]
            for pos in range(len(ordered_ts) - 2, -1, -1):
                ordered_ts[pos] = min(ordered_ts[pos], ordered_ts[pos + 1] - 9.0)
        for pos, i in enumerate(order):
            sorted_ts[i] = ordered_ts[pos]
        placements = [sorted_ts[i] for i in range(len(episode_overlays))]
        for overlay_index, (oid, kind, tag, ov_title, body, terms, fullscreen) in enumerate(episode_overlays):
            ts = placements[overlay_index]
            fg,bg=COLORS[kind]
            blocks.append(overlay_html(oid,tag,ov_title,body,fullscreen,fg,bg,ts))
            overlays_data_current.append((oid,tag,ov_title,body,fullscreen,terms,ts))
            source=SFX_CHIME if fullscreen else SFX_POP
            dur="2.1" if fullscreen else "0.5"
            vol="1.0" if fullscreen else "0.75"
            sfx.append(f'<audio id="sfx-{oid}" data-start="{ts:.2f}" data-duration="{dur}" data-track-index="{4+len(sfx)}" src="{source}" data-volume="{vol}"></audio>')
        # build_index reads overlays_data_current for GSAP timing snippets
        html=build_index(ep,end-start,title,subtitle,idx,next_title,next_sub,"\n".join(blocks),"\n".join(sfx))
        (ep_dir/'index.html').write_text(html,encoding='utf-8')
        print(f"{ep}: {len(OVERLAYS[ep])} content overlays")
        total += len(OVERLAYS[ep])
    print(f"Built {len(EPISODES)} episodes and {total} overlays.")
    print("Generating overlay verification SRTs...")
    from _generate_srt import hyperframes_to_srt
    for ep,*_ in EPISODES: hyperframes_to_srt(BASE/ep/'index.html')
    captions=BASE/'_generate_captions.py'
    if captions.exists(): subprocess.run([sys.executable,str(captions),'--skip-translate'],cwd=BASE,check=False)
    return 0

if __name__ == '__main__': raise SystemExit(main())
