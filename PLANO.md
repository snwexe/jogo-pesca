# Plano de melhorias — Pescaria Tranquila

Status: **tudo implementado de uma vez** (não foi dividido em fases). Detalhes das regras em `EXPLICACAO.md`.

## Decisões do usuário

- Implementar o pacote de gameplay: minigame variado por raridade, combo, peixes ruins, clima/horário, conquistas.
- Mecânica de perder: **sem** vidas/fôlego. Mantidos: linha que quebra, custo por lançamento (isca) e prazos
  (encomendas). Perder agora também é: salário sem dinheiro (demissão), encomenda expirada, peixe estragado, bomba.
- Gráfico em primeira pessoa: descartado (muito trabalho, difícil de explicar). Mantida a vista lateral,
  com ciclo dia/noite, chuva, neblina e funcionários no pier.
- Foco em lógica e contas: fornecedores, demanda, reputação, encomendas, salários e lucro do dia.
- Estilo tycoon: contratar funcionários, mandar dinheiro à loja (entrega demora), comprar licenças e o barco.
- Muito mais peixes (30 espécies) e mais melhorias (8, com mais níveis).

## Implementado

- 30 espécies + 4 itens de lixo, em 3 locais (Rio, Lago, Mar) e nova raridade "mítico".
- Mochila com frescor, 4 fornecedores, demanda, limite diário, reputação e encomendas.
- Loja com 8 melhorias e entrega com atraso. Isca como consumível.
- Empresa: 3 tipos de funcionário, salários diários, relatório de lucro, licenças e Barco (meta final).
- Combo, linha que quebra, Peixe-Bomba, lixo, sonar, rede, horário, clima e 18 conquistas.

## Ajustes depois dos testes do usuário

- Mercado separado em duas abas: **VENDER** (com a conta do preço na tela) e **ENCOMENDAS** (um cartão por fornecedor).
- Limite de venda dos fornecedores agora sobe (melhoria Contratos + reputação).
- Mochila vai até 200 peixes (38 níveis, preço mais suave).

- Vendedores contratáveis (Ambulante, Representante, Gerente de Vendas): vendem sozinhos, cobram comissão, reservam peixes de encomendas.

## Ideias futuras (não feitas)

- Corte submarino durante o minigame, respingos de água e efeitos sonoros (`pygame.mixer`).
- Empréstimo com juros com o fornecedor.
- Preço dos fornecedores variando por dia.
