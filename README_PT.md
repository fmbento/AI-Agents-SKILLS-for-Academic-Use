# SKILLS (habilidades) para Agentes de IA, uso Académico

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

Uma colecção de skills reutilizáveis para agentes de IA. Cada skill é um `SKILL.md` autónomo que define quando deve ser usado, como o agente deve raciocinar e que resultado deve produzir.

A colecção está organizada por finalidade:

- **[Learning](Learning/README_PT.md)** — explicações, modelos visuais e simulações de aprendizagem activa.
- **[Production](Production/README_PT.md)** — backoffice, criação de conteúdos e produção automatizada de novos materiais (séries de vídeo, conteúdos de aprendizagem e afins).
- **[Research](Research/README_PT.md)** — fluxos de trabalho reproduzíveis para investigação bibliográfica e artefactos de investigação.

## Skills em resumo

| Área | Skill | Finalidade |
| --- | --- | --- |
| Learning | [arquiteto-mermaid](Learning/arquiteto-mermaid/SKILL.md) | Converte texto estruturado, processos e relações em diagramas Mermaid claros (mapas mentais, fluxogramas, etc.). |
| Learning | [eli14](Learning/eli14/SKILL.md) | Explica temas complexos a um adolescente curioso e produz um visual HTML autónomo completo. |
| Learning | [simulador-pbl](Learning/simulador-pbl/SKILL.md) | Cria desafios interactivos de Problem-Based Learning com dados progressivos e pistas opcionais. |
| Learning | [tradutor-feynman](Learning/tradutor-feynman/SKILL.md) | Traduz conceitos técnicos ou abstractos para explicações claras sem perder a precisão. |
| Production | [webinar-to-video](Production/webinar-to-video/SKILL.md) | Transforma gravações de webinars em séries de vídeo profissionais com overlays, legendas bilingues, SFX e metadata YouTube. Corre dentro do [OpenMontage](https://github.com/calesthio/OpenMontage). |
| Research | [scopus-research](Research/scopus-research/SKILL.md) | Executa uma pesquisa Scopus completa, controlada pelo navegador, com exportação, análise e subconjunto focado. |

## Como utilizar as skills

1. Copie a pasta da skill relevante para o directório de skills analisado pelo seu agente (por exemplo, `.agents/skills/`).
2. Mantenha a pasta e o respectivo `SKILL.md` juntos.
3. Peça ao agente uma tarefa correspondente à descrição da skill. O frontmatter e as instruções da skill orientam a activação e o resultado.
4. Leia o `SKILL.md` individual antes de adaptar uma skill a outro sistema de agentes.

As skills são complementares: use `tradutor-feynman` ou `eli14` para explicar, `arquiteto-mermaid` para visualizar, `simulador-pbl` para praticar, `scopus-research` para investigar literatura académica e `webinar-to-video` para transformar gravações existentes em materiais de aprendizagem publicados.

## Estrutura do repositório

```text
AI-Agents-SKILLS/
├── Learning/
│   ├── README.md
│   ├── README_PT.md
│   ├── arquiteto-mermaid/SKILL.md
│   ├── eli14/SKILL.md
│   ├── simulador-pbl/SKILL.md
│   └── tradutor-feynman/SKILL.md
├── Production/
│   ├── README.md
│   ├── README_PT.md
│   └── webinar-to-video/
│       ├── SKILL.md
│       ├── INDEX.md
│       ├── README.md
│       ├── README_PT.md
│       └── templates/
├── Research/
│   ├── README.md
│   ├── README_PT.md
│   └── scopus-research/
│       ├── SKILL.md
│       ├── README.md
│       └── examples/
└── README.md
```

## Idioma e convenções

Este é o ficheiro em português europeu. Consulte o [README.md](README.md) para a versão inglesa. Cada pasta disponibiliza `README.md` (inglês) e `README_PT.md` (português) com um switch de idioma no topo. As skills de aprendizagem respondem por defeito em português europeu, salvo indicação do utilizador. As skills devem preservar a terminologia do utilizador, declarar pressupostos, distinguir factos de inferências e não inventar fontes ou dados.

## Licença

Consulte [LICENSE](LICENSE).
