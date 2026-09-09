# Learning — Skills de Aprendizagem

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

A colecção `Learning` ajuda um agente de IA a tornar temas difíceis compreensíveis, visuais, práticos e memoráveis. As quatro skills foram concebidas para responder por defeito em português europeu, preservando a terminologia técnica e adaptando-se ao nível do aluno.

## Skills

### [arquiteto-mermaid](arquiteto-mermaid/SKILL.md)

**Arquiteto de diagramas Mermaid.** Converte texto estruturado, apontamentos, taxonomias, programas de disciplinas, processos e relações entre conceitos em diagramas Mermaid.js válidos e fáceis de copiar.

Use-o para:

- mapas mentais e hierarquias (`mindmap`);
- processos, sequências e decisões com direcção (`flowchart TD`);
- grafos de relações e ligações transversais;
- código destinado ao Mermaid Live ou a editores compatíveis.

A skill extrai o tema central e as relações, mantém o significado da fonte, cria identificadores e rótulos seguros, evita sintaxes incompatíveis, verifica os nós referenciados e mantém os diagramas grandes focados. Entrega primeiro o código Mermaid e não acrescenta conceitos sem suporte nem trata inferências como factos.

### [eli14](eli14/SKILL.md)

**Mentor de explicações acessíveis.** Explica um tema complexo a uma pessoa curiosa com cerca de 14 anos, sem ser infantil ou condescendente.

A estrutura habitual é:

1. um gancho;
2. um modelo mental geral;
3. uma explicação passo a passo;
4. exemplos do mundo real reconhecíveis;
5. a importância do tema e possíveis desenvolvimentos;
6. um mini-check com perguntas ou um pequeno desafio.

Cada resposta inclui também um artefacto visual HTML completo e autónomo. O HTML deve funcionar sem build step, servidor ou dependências externas, suportar temas claro e escuro, representar o modelo mental central e continuar acessível sem depender apenas da cor.

### [simulador-pbl](simulador-pbl/SKILL.md)

**Simulador de Problem-Based Learning.** Transforma um tópico de estudo, capítulo, conjunto de apontamentos ou área profissional num desafio interactivo de resolução de problemas, em vez de numa ficha que revela imediatamente a resposta.

O desafio inclui um objectivo de aprendizagem, um cenário plausível, dados coerentes, perguntas orientadoras, uma tarefa final, critérios de sucesso e pistas opcionais por níveis. O agente actua como tutor: espera pela primeira hipótese ou passo do aluno, incentiva o raciocínio baseado em evidência, dá feedback progressivo e só revela uma solução completa quando tal é pedido.

Em temas clínicos, a skill exige um caso explicitamente fictício, não dá diagnósticos individuais nem instruções de tratamento e inclui orientações de segurança adequadas.

### [tradutor-feynman](tradutor-feynman/SKILL.md)

**Tradutor pela Técnica de Feynman.** Torna conceitos técnicos, científicos, médicos, académicos ou abstractos compreensíveis, substituindo jargão desnecessário por linguagem clara e analogias do quotidiano sem perder a precisão causal.

Identifica o nível do aluno, divide o conceito em partes pequenas, explica o mecanismo, define os termos técnicos essenciais e indica onde uma analogia deixa de ser exacta. Em textos longos, resume primeiro e selecciona depois os conceitos que precisam realmente de explicação. A skill distingue factos, hipóteses, excepções e incerteza, e não inventa informação em falta.

## Escolher uma skill

| Necessidade | Skill recomendada | Resultado |
| --- | --- | --- |
| Ver estrutura ou relações | `arquiteto-mermaid` | Um diagrama Mermaid focado. |
| Obter uma visão geral amigável mas rigorosa | `eli14` | Uma explicação adequada à idade e um visual HTML autónomo. |
| Aprender através de um caso realista | `simulador-pbl` | Um cenário PBL interactivo com apoio faseado. |
| Descodificar jargão ou um texto difícil | `tradutor-feynman` | Uma explicação em linguagem corrente com analogias precisas. |

As skills podem ser combinadas. Por exemplo, use `tradutor-feynman` para esclarecer um conceito, `arquiteto-mermaid` para o mapear e `simulador-pbl` para testar a sua aplicação. Use `eli14` quando o resultado final também deva ser um recurso visual de aprendizagem cuidado.

## Estrutura da pasta

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

Leia cada `SKILL.md` ligado acima para conhecer os critérios completos de activação, o formato de saída, as regras de segurança e a lista de verificação final.

Para ajudantes partilhados de documento, escritório, figura e apresentação que possam ser anexados a entregáveis de Learning, consulte os scripts e skills em `Utils/` — nomeadamente `Utils/scripts/generate_pdf.py` quando um recurso de aprendizagem em markdown também deva ser entregue como PDF, e `Utils/skills-integration.md` para saber onde cabe cada ajudante. As skills de Learning não são substituídas por esses ajudantes; explicam apenas o que mais pode ser feito com um resultado de Learning já escrito.
