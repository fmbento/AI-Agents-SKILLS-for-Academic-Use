# Learning Skills

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

The `Learning` collection helps an AI agent make difficult subjects understandable, visual, practical and memorable. All four skills are designed for European Portuguese by default, while preserving technical terminology and adapting to the learner's level.

## Skills

### [arquiteto-mermaid](arquiteto-mermaid/SKILL.md)

**Mermaid diagram architect.** Converts structured text, notes, taxonomies, course programmes, processes and conceptual relationships into valid, copyable Mermaid.js diagrams.

Use it for:

- mind maps and hierarchies (`mindmap`);
- directed processes, sequences and decisions (`flowchart TD`);
- relationship graphs and cross-links;
- code intended for Mermaid Live or compatible editors.

The skill extracts the central topic and relationships, keeps the source meaning, creates safe identifiers and labels, avoids incompatible syntax, checks referenced nodes and keeps large diagrams focused. It returns the Mermaid code first and does not add unsupported concepts or treat inferences as facts.

### [eli14](eli14/SKILL.md)

**Accessible explanation mentor.** Explains a complex subject to a curious person of approximately 14 years old without becoming childish or condescending.

Its default structure is:

1. a hook;
2. a high-level mental model;
3. a step-by-step explanation;
4. recognisable real-world examples;
5. why it matters and what may come next;
6. a mini-check with questions or a small challenge.

Every response also includes a complete, standalone HTML visual artefact. The HTML must work without a build step, server or external dependencies, support light and dark themes, represent the central mental model, and remain accessible without relying only on colour.

### [simulador-pbl](simulador-pbl/SKILL.md)

**Problem-Based Learning simulator.** Turns a study topic, chapter, set of notes or professional area into an interactive problem-solving challenge rather than a worksheet that reveals the answer immediately.

A challenge includes a learning objective, plausible scenario, coherent data, guiding questions, a final task, success criteria and optional hints in levels. The agent acts as a tutor: it waits for the learner's first hypothesis or next step, encourages evidence-based reasoning, gives progressive feedback and only reveals a full solution when requested.

For clinical topics, the skill requires an explicitly fictional case, avoids individual diagnosis or treatment instructions, and includes appropriate safety guidance.

### [tradutor-feynman](tradutor-feynman/SKILL.md)

**Feynman technique translator.** Makes technical, scientific, medical, academic or abstract concepts understandable by replacing unnecessary jargon with clear language and everyday analogies while preserving causal accuracy.

It identifies the learner's level, splits the concept into small parts, explains the mechanism, defines essential technical terms, and points out where an analogy stops being exact. Long inputs are summarised before the concepts that need explanation are selected. The skill distinguishes facts, hypotheses, exceptions and uncertainty, and avoids inventing missing information.

## Choosing a skill

| Need | Recommended skill | Result |
| --- | --- | --- |
| See structure or relationships | `arquiteto-mermaid` | A focused Mermaid diagram. |
| Get a friendly but rigorous overview | `eli14` | An age-appropriate explanation plus standalone HTML visual. |
| Learn by investigating a realistic case | `simulador-pbl` | An interactive PBL scenario with staged support. |
| Decode jargon or a difficult passage | `tradutor-feynman` | A plain-language explanation with precise analogies. |

Skills can be combined. For example, use `tradutor-feynman` to clarify a concept, `arquiteto-mermaid` to map it, and `simulador-pbl` to test whether it can be applied. Use `eli14` when the final result should also be a polished visual learning resource.

## Folder structure

```text
Learning/
├── README.md
├── README_PT.md
├── arquiteto-mermaid/
│   └── SKILL.md
├── eli14/
│   └── SKILL.md
├── simulador-pbl/
│   └── SKILL.md
└── tradutor-feynman/
    └── SKILL.md
```

Read each linked `SKILL.md` for the complete activation criteria, output format, safety rules and verification checklist.
