# AI-Agents-SKILLS

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

A curated collection of reusable skills for AI agents. Each skill is a self-contained `SKILL.md` that defines when the agent should use it, how it should reason, and what output it should produce.

The collection is organised by purpose:

- **[Learning](Learning/README.md)** — explanations, visual models and active-learning simulations.
- **[Production](Production/README.md)** — backoffice, content creation and automated production of new materials (video series, learning content and alike).
- **[Research](Research/README.md)** — reproducible literature-research workflows and research artefacts.

## Skills at a glance

| Area | Skill | Purpose |
| --- | --- | --- |
| Learning | [arquiteto-mermaid](Learning/arquiteto-mermaid/SKILL.md) | Turns structured text, processes and relationships into clear Mermaid diagrams. |
| Learning | [eli14](Learning/eli14/SKILL.md) | Explains complex subjects to a curious teenager and produces a complete standalone HTML visual. |
| Learning | [simulador-pbl](Learning/simulador-pbl/SKILL.md) | Creates interactive Problem-Based Learning challenges with progressive data and optional hints. |
| Learning | [tradutor-feynman](Learning/tradutor-feynman/SKILL.md) | Translates technical or abstract concepts into clear explanations while preserving precision. |
| Production | [webinar-to-video](Production/webinar-to-video/SKILL.md) | Turns webinar recordings into professional video series with overlays, bilingual subtitles, SFX and YouTube metadata. Runs inside [OpenMontage](https://github.com/calesthio/OpenMontage). |
| Research | [scopus-research](Research/scopus-research/SKILL.md) | Runs an end-to-end, browser-controlled Scopus search, export, analysis and focused-subset workflow. |

## How to use the skills

1. Copy the relevant skill folder into the skills directory scanned by your agent harness (for example, `.agents/skills/`).
2. Keep the folder name and `SKILL.md` together.
3. Ask the agent for a task that matches the skill description. The skill's frontmatter and instructions guide activation and output.
4. Read the individual `SKILL.md` before adapting a skill to a new agent harness.

The skills are intentionally complementary: use `tradutor-feynman` or `eli14` to explain, `arquiteto-mermaid` to visualise, `simulador-pbl` to practise, `scopus-research` to investigate academic literature, and `webinar-to-video` to turn existing recordings into published learning material.

## Repository structure

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

## Language and conventions

This file is the English version. See [README_PT.md](README_PT.md) for European Portuguese. Every folder provides `README.md` (English) and `README_PT.md` (Portuguese) with a language switch at the top. The learning skills respond in European Portuguese by default unless the user requests another language. Skills should preserve the user's terminology, state assumptions, distinguish facts from inferences, and avoid inventing sources or data.

## Licence

See [LICENSE](LICENSE).
