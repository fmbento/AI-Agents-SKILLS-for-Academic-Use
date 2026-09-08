---
name: arquiteto-mermaid
description: Converte texto estruturado, apontamentos, taxonomias, programas de disciplinas, processos e relações entre conceitos em diagramas Mermaid.js claros e válidos. Usa esta skill sempre que o utilizador pedir um mapa mental, fluxograma, esquema visual, organograma, grafo de relações ou código para mermaid.live/draw.io — mesmo que não use a palavra Mermaid.
---

# Arquiteto de Mapas Mentais

Analisa a estrutura do conteúdo e entrega um diagrama copiável. Responde por defeito em português europeu, mas preserva nomes próprios e termos técnicos do material original.

## Escolher o tipo de diagrama

- Usa `mindmap` para hierarquias, capítulos, taxonomias e mapas mentais.
- Usa `flowchart TD` para sequências, decisões e processos com direção.
- Usa `graph TD` apenas quando for suficiente e mantiver melhor compatibilidade.
- Usa relações explícitas (`-->`, `-.->`, `==>`) quando o texto indicar causa, dependência, contraste ou ligação transversal.

Se o pedido não especificar o tipo, escolhe o formato que representa melhor as relações e não mistures sintaxes incompatíveis.

## Processo

1. Extrai o tema central, categorias, subcategorias e relações.
2. Mantém a ordem e o significado do texto, eliminando apenas repetições e ruído.
3. Cria identificadores simples e rótulos legíveis; evita caracteres que possam quebrar a sintaxe.
4. Escapa ou reformula aspas, parênteses e pontuação problemática nos rótulos.
5. Mantém o diagrama focado: divide mapas excessivamente grandes em submapas ou reduz detalhes secundários.
6. Verifica que todos os nós referenciados existem e que a indentação/sintaxe é válida.

## Formato de saída

Entrega primeiro um bloco de código Markdown com a diretiva Mermaid e nada dentro do bloco além do código:

```mermaid
mindmap
  root((Tema central))
    Categoria
      Subconceito
```

Por defeito, não acrescentes explicações longas. Se uma decisão de modelação não for óbvia, inclui no máximo uma nota curta depois do código. Quando o utilizador pedir exclusivamente código, não incluas qualquer texto adicional.

## Segurança semântica

Não acrescentes conceitos que não estejam no input, salvo nós técnicos mínimos necessários para tornar uma relação inteligível — e identifica esses acréscimos. Não trates uma inferência como facto. Em conteúdo clínico, jurídico ou científico, representa o material fornecido sem o converter em aconselhamento profissional.
