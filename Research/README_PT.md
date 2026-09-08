# Research — Skills de Investigação

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

A colecção `Research` contém skills para investigação académica estruturada e reproduzível. Actualmente inclui um fluxo de trabalho completo e os respectivos artefactos de exemplo.

## Skills

### [scopus-research](scopus-research/SKILL.md)

**Investigação bibliográfica completa no Scopus.** Recebe um tema de investigação em qualquer idioma e orienta o agente através de uma sessão institucional do Scopus com controlo do navegador.

O fluxo de trabalho:

1. cria uma pasta de saída com data e hora;
2. enriquece o tema, incluindo tradução português-inglês, sinónimos, variantes e blocos conceptuais;
3. mostra a equação de pesquisa avançada proposta e permite ao utilizador ajustá-la antes da pesquisa;
4. executa a consulta no Scopus e ordena os resultados por relevância;
5. exporta até 2.000 registos em CSV com resumos, palavras-chave dos autores, palavras-chave indexadas e referências;
6. analisa os artigos mais relevantes e mais citados, revistas, anos, palavras-chave, tipos de documento e acesso aberto;
7. ordena as referências mais mencionadas, com ligações para resolução e limitações de análise declaradas;
8. filtra um subconjunto focado pelo título/resumo e apresenta as respectivas estatísticas.

Os resultados esperados são `scopus_export_full.csv`, um CSV de subconjunto focado, `query.txt` e um resumo da análise na conversa, guardados em `./pesquisas/scopus/<data-hora> - <tema>/`.

## Entradas

| Entrada | Obrigatória | Descrição |
| --- | --- | --- |
| `TOPIC` | Sim | A pergunta ou o tema de investigação, em qualquer idioma. |
| `FOCUS_TERMS` | Não | Termos usados para filtrar o subconjunto focado por título/resumo; caso contrário, são derivados e confirmados. |
| `MAX_EXPORT` | Não | Limite da exportação, por defeito 2.000. |
| `OUT_ROOT` | Não | Raiz de saída, por defeito `./pesquisas/scopus/`. |

## Requisitos e limites

- Uma sessão Chrome com remote debugging activo e a sessão Scopus/institucional autenticada do utilizador.
- `browser-harness` para controlar o navegador e Python 3, apenas com a biblioteca padrão, para analisar CSV.
- O agente tem de mostrar a equação antes da pesquisa e comunicar honestamente o limite de exportação de 2.000 registos.
- O fluxo não usa um perfil de navegador novo sem o utilizador aceitar perder a sessão existente.
- A pesquisa é feita no Scopus, não através de uma pesquisa geral na Web.

O [README](scopus-research/README.md) da própria skill contém um guia de utilização conciso, requisitos, notas de sintaxe, limitações e o mapa dos ficheiros de exemplo. O [SKILL.md](scopus-research/SKILL.md) completo contém o procedimento no navegador, os detalhes da exportação, as regras de análise e os problemas conhecidos da interface.

## Exemplos aninhados

A pasta [examples](scopus-research/examples/README.md) documenta uma execução validada do Scopus sobre inteligência artificial aplicada ao cuidado de idosos. Contém uma consulta, exportações CSV representativas e os relatórios de análise completa e do subconjunto. Estes ficheiros exemplificam o formato e a proveniência dos resultados; não substituem uma pesquisa nova.

## Estrutura da pasta

```text
Research/
├── README.md
├── README_PT.md
└── scopus-research/
    ├── SKILL.md
    ├── README.md
    └── examples/
        ├── README.md
        ├── query.txt
        ├── scopus_export_full_HEADER_ONLY.csv
        ├── scopus_eldercare_subset_SAMPLE.csv
        ├── analysis_full_export.md
        └── analysis_subset.md
```

## Quando escolher esta skill

Use `scopus-research` quando a tarefa precisar de uma pesquisa Scopus documentada, uma exportação ordenada por relevância, resumos bibliométricos, análise da frequência de referências ou um subconjunto focado. Não se destina a inventar resultados bibliográficos, contornar o acesso institucional ou tratar uma fatia de 2.000 registos ordenada por relevância como se fosse todo o corpus do Scopus.
