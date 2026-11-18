# Pescaria Tranquila Tycoon — Explicação do Projeto

## 1. Ideia do jogo

Jogo de pescaria 2D feito em Python com Pygame, com cara de **tycoon** (jogo de administrar um negócio).
O jogador escolhe um pescador, lança a linha do pier e espera um peixe morder. Quando morde, aparece um
minigame de timing: é preciso apertar ESPAÇO no momento certo. O peixe pescado vai para a **mochila** e
precisa ser **vendido a fornecedores**, que pagam preços diferentes. Com o dinheiro, o jogador compra
melhorias, **contrata funcionários** que pescam sozinhos, libera novos locais de pesca e, no fim,
compra o **Barco Pesqueiro** (meta final: 8000 moedas).

Tudo é desenhado com código (retângulos, círculos, polígonos e texto). Não há imagens nem sons,
então o jogo roda só com o arquivo `jogo.py`.

## 2. Instalação e execução

```bash
pip install pygame
python jogo.py
```

(Python 3.8 ou mais novo. No Windows, se `pip` não funcionar, use `python -m pip install pygame`.)

O progresso é salvo em `save.json`, na mesma pasta do `jogo.py`: ao fechar o jogo e também
automaticamente no fim de cada dia. Para começar do zero, aperte **N** no menu ou apague o `save.json`.

## 3. Como jogar (controles)

| Tela | Tecla | Ação |
|---|---|---|
| Menu | ENTER / N / ESC | Jogar-continuar / novo jogo / sair |
| Escolha | SETAS ou 1, 2, 3 + ENTER | Escolher o pescador |
| Pesca | ESPAÇO | Lançar linha / acertar o minigame / continuar |
| Pesca | L | Loja de pesca (melhorias) |
| Pesca | M | Mercado, aba **VENDER** (vender peixes) |
| Pesca | O | Mercado, aba **ENCOMENDAS** (pedidos dos fornecedores) |
| Pesca | E | Empresa (funcionários e expansões) |
| Pesca | C | Coleção de peixes |
| Pesca | Q | Conquistas |
| Pesca | T | Trocar de local de pesca |
| Pesca | ESC | Voltar ao menu |
| Loja | 1 a 9 | Encomendar melhoria |
| Loja | B | Comprar 10 iscas |
| Mercado | TAB | Alterna entre as abas VENDER e ENCOMENDAS |
| Aba Vender | ← → | Trocam de fornecedor |
| Aba Vender | ↑ ↓ | Escolhem o peixe da mochila |
| Aba Vender | ESPAÇO | Vender 1 peixe do tipo selecionado |
| Aba Vender | V | Vender tudo que o fornecedor aceita |
| Aba Encomendas | ↑ ↓ | Escolhem o fornecedor |
| Aba Encomendas | E | Entregar a encomenda |
| Empresa | TAB | Alterna entre as abas PESCA e VENDAS |
| Empresa (PESCA) | 1, 2, 3 | Contratar Aprendiz, Pescador, Mestre |
| Empresa (VENDAS) | 1, 2, 3 | Contratar Ambulante, Representante, Gerente de Vendas |
| Empresa | D | Demitir o último contratado da aba aberta |
| Empresa (PESCA) | 4, 5, 6 | Comprar Licença do Lago, Licença do Mar, Barco |
| Todas as telas | ESC (ou a tecla da própria tela) | Voltar |

As telas (loja, mercado, empresa...) só abrem com a linha recolhida.

**Pescadores:** Zé Ligeiro (peixes mordem 40% mais rápido), Dona Sortuda (mais peixes raros),
Capitão Firme (zona verde maior).

## 4. As regras do jogo

### 4.1 Pescaria e peixes
- **34 itens sorteáveis:** 30 espécies na coleção (8 comuns, 7 incomuns, 7 raros, 5 lendários, 3 míticos)
  mais 4 itens de "lixo": Bota Velha, Lata Enferrujada, Alga Pegajosa e o **Peixe-Bomba**.
- Cada espécie vive em um ou mais **locais**: Rio, Lago e Mar.
- **Isca:** cada lançamento gasta 1 isca. Pacote com 10 custa 20 moedas. Sem isca, não pesca.
  (Se o jogador ficar sem iscas, sem moedas e sem peixes, um vizinho dá 3 iscas, para o jogo nunca travar.)
- **Minigame variado por raridade:**

| Raridade | Peso | Zona verde | Velocidade | Extra |
|---|---|---|---|---|
| Lixo | 6 | 34% | 0,60 | — |
| Comum | 55 | 26% | 0,70 | — |
| Incomum | 25 | 19% | 0,90 | — |
| Raro | 12 | 13% | 1,15 | zona balança |
| Lendário | 3 | 9% | 1,40 | zona balança mais |
| Mítico | 0,5 | 8% | 1,55 | zona balança + **2 acertos seguidos**, 9 s |

- **Lixo:** vale 1 ou 2 moedas na hora. **Peixe-Bomba:** se o jogador *acertar* o minigame, perde 25 moedas
  e o combo. Quem tem Sonar nível 2 vê o nome do peixe antes de fisgar e pode recolher a linha.
- **Combo:** acertos seguidos dão bônus em moedas (10% do valor × acertos seguidos, até 50%). Errar zera.
- **Linha quebra:** errar um peixe raro, lendário ou mítico pode quebrar a linha (30%, 50% ou 70%),
  o que custa moedas. A melhoria "Linha reforçada" reduz a chance em 15% por nível.

### 4.2 Horário e clima
O dia dura 120 s e é dividido em manhã, tarde e noite. O clima é sorteado a cada dia.

| Condição | Efeito |
|---|---|
| Noite | +0,5 de sorte, mordida 20% mais lenta (escurece a tela e aparecem estrelas) |
| Tarde | mordida 10% mais rápida (tom alaranjado) |
| Chuva | mordida 25% mais rápida, zona verde -3% (gotas caem) |
| Neblina | +0,4 de sorte, mordida 10% mais lenta |

### 4.3 Mochila e frescor
O peixe pescado vai para a **mochila** (10 espaços, +5 por nível da melhoria, **até 200 peixes**). Cheia = não lança mais a linha.
Cada peixe tem **frescor**: começa em 100% e cai até 0% em 240 s (a Geladeira aumenta esse tempo em 50% por nível).
Peixe fresco vale mais: o fator de preço vai de 0,4 (estragado) a 1,0 (fresco).

### 4.4 Fornecedores (o coração da lógica)
O preço que cada fornecedor paga por **um** peixe é:

```
preço = valor x multiplicador da raridade x (0,4 + 0,6 x frescor) x (1 + 0,04 x nível de reputação) x demanda
```

| Fornecedor | Especialidade | Compra por dia | Frescor mínimo |
|---|---|---|---|
| Peixaria do Zé | comuns x1,3 / incomuns x1,1 / raros x0,9 / lendários x0,7 | 8 | — |
| Mercado Central | tudo x1,0 | 14 | — |
| Restaurante Chique | raros x1,5 / lendários x1,7 / míticos x1,6 | 5 | 60% |
| Exportadora | só raro (x1,35), lendário (x1,5) e mítico (x1,8) | 4 | 30% |

- **Demanda:** cada venda do mesmo peixe ao mesmo fornecedor derruba o preço em 8% (mínimo 30%).
  O preço se recupera 1% por segundo. Vender tudo de uma vez é mau negócio: é melhor espalhar entre fornecedores.
- **Limite por dia:** cada fornecedor só compra uma quantidade por dia (quem compra mais é o Mercado Central).
  O limite **cresce** com a melhoria **Contratos** (+3 por nível, em todos os fornecedores) e com a reputação
  (+1 por nível): `limite = base + 3 × Contratos + nível de reputação`.
- **Venda inteligente (tecla V):** vende primeiro os peixes que o fornecedor paga *mais*, para usar o limite do dia
  nos melhores negócios. Entre peixes iguais, vende o mais velho que ele aceita.
- **Encomendas** (aba própria no Mercado, tecla O): de tempos em tempos um fornecedor pede de 1 a 2 tipos de peixe ("3 Tilápias + 1 Dourado").
  O prazo é de `100 + 40 × quantidade` segundos e a recompensa é **1,8× o valor** dos peixes. Cumprir dá +1 ponto de
  reputação; deixar o prazo acabar tira 1 ponto. A cada 3 pontos de reputação o fornecedor paga +4% (até o nível 5).

### 4.5 Loja de pesca (9 melhorias)
Preço de cada nível = `preço base × 1,6^nível` (crescimento exponencial). O pedido é pago na hora, mas a loja
**demora `10 s × nível novo` para entregar** (no máximo 60 s) (você "envia o dinheiro" e a vara chega depois).

| Melhoria | Efeito por nível | Níveis |
|---|---|---|
| Vara melhor | zona verde +2,5% | 6 |
| Carretilha | espera da mordida -9% | 6 |
| Amuleto | +0,3 de sorte | 5 |
| Mochila maior | +5 espaços (até 200 peixes). Preço sobe 12% por nível, não 60% | 38 |
| Linha reforçada | -15% de chance de quebrar | 5 |
| Rede | +8% de chance de pegar um peixe extra | 5 |
| Sonar | 1: vê a raridade, 2: vê o nome, 3: recolher a linha devolve a isca | 3 |
| Geladeira | peixe estraga 50% mais devagar | 4 |
| Contratos | +3 vendas por dia em cada fornecedor (preço sobe 50% por nível) | 10 |

### 4.6 Empresa: funcionários e expansões
Funcionários pescam sozinhos e colocam o peixe na mochila (se houver espaço). **O salário é pago todo fim de dia**;
se faltar dinheiro, o funcionário pede demissão (a "derrota" do tycoon). O jogador vê o lucro do dia:
`lucro = vendas - salários`.

| Tipo | Contratar | Salário/dia | Pesca a cada | Acerta | Sorte |
|---|---|---|---|---|---|
| Aprendiz | 80 | 12 | 20 s | 55% | 0 |
| Pescador | 250 | 30 | 14 s | 70% | 0,3 |
| Mestre | 700 | 70 | 9 s | 85% | 0,8 |

Máximo de 6 funcionários. Eles aparecem no pier, cada um com a sua boia.
Os funcionários também completam a coleção. Mas a mochila e o limite dos fornecedores são um gargalo:
contratar demais sem vender bem dá prejuízo.

**Vendedores (aba VENDAS):** esvaziam a mochila sozinhos, para os pescadores nunca pararem por falta de espaço.
A cada intervalo, o vendedor percorre os 4 fornecedores e todos os peixes da mochila, calcula o preço de cada
combinação e vende **um** peixe da melhor (maior preço). Ele fica com uma **comissão**, então o jogador recebe
`preço × (1 - comissão)`.

| Tipo | Contratar | Salário/dia | 1 venda a cada | Comissão | Vende até | Extra |
|---|---|---|---|---|---|---|
| Ambulante | 150 | 15 | 8 s | 20% | incomum | — |
| Representante | 500 | 40 | 5 s | 12% | raro | — |
| Gerente de Vendas | 1500 | 100 | 3 s | 8% | mítico | entrega encomendas prontas |

Regras: máximo de 3 vendedores; respeitam o limite diário e a demanda dos fornecedores; **nunca vendem peixes
pedidos em uma encomenda ativa** (esses ficam reservados); salário pago no fim do dia junto com os pescadores.
Os vendedores aparecem numa banca à direita, e um "+12" sobe quando fazem uma venda.
Vale a pena? Depende: a comissão é um custo, mas sem vendedor a mochila enche e os pescadores param.

**Expansões:** Licença do Lago (400), Licença do Mar (1500, exige o Lago) e **Barco Pesqueiro** (8000, exige o Mar).
Comprar o barco encerra o jogo com uma tela de vitória, mas o jogador pode continuar em "modo livre".

### 4.7 Conquistas
20 conquistas (primeiro peixe, combos, coleção, equipe, encomendas, explodir uma bomba...). Cada uma é um
dicionário com uma função `lambda` que o jogo testa a cada quadro.

## 5. Estrutura do código (seção por seção)

1. **IMPORTAÇÕES** — `json`, `math`, `os`, `random`, `sys` e `pygame`.
2. **CONFIGURAÇÕES E CONSTANTES** — tamanho da janela, tempos, preços e cores no topo, para ajustar o jogo
   sem caçar números pelo código.
3. **RARIDADES, LOCAIS E PEIXES** — dicionário `RARIDADES`, dicionário `LOCAIS` e a lista `DADOS_PEIXES`
   (uma lista de dicionários, um por peixe). Para adicionar um peixe novo basta incluir uma linha.
4. **CLASSE PEIXE** — nome, raridade, valor, cor, tamanho, locais e efeito. A lista `PEIXES` é criada a partir
   dos dados com `Peixe(**dados)`.
5. **CLASSE PERSONAGEM** — os 3 pescadores.
6. **HORÁRIO E CLIMA** — dicionários `HORARIOS` e `CLIMAS` com os modificadores.
7. **SORTEIO DO PEIXE** — `calcular_pesos` aplica a sorte; `sortear_peixe` usa `random.choices` (raridade) e
   `random.choice` (peixe do local atual); `sortear_tempo_mordida` usa `random.uniform`.
8. **MINIGAME** — classe `MinigameCaptura`, com zona móvel (seno) e vários acertos.
9. **LOJA, EXPANSÕES, FUNCIONÁRIOS, FORNECEDORES** — dicionários e as classes `Funcionario` e `Fornecedor`,
   mais as funções puras `preco_venda`, `nivel_reputacao` e `gerar_encomenda`.
10. **COLEÇÃO, ESTATÍSTICAS E CONQUISTAS** — contagens e a lista `CONQUISTAS`.
11. **SALVAR E CARREGAR** — `json.dump` / `json.load` com `try/except` e valores padrão com `.get`.
12. **DESENHO DA TELA** — funções para texto, painéis, peixe, pescador, funcionário e a classe `Cenario`
    (céu, sol/lua, nuvens, ondas, chuva, estrelas e a película de horário/clima).
13. **CLASSE JOGO (MÁQUINA DE ESTADOS)** — guarda o progresso. Cada tela tem uma função `teclas_...` e uma
    `desenhar_...`, ligadas por dois dicionários (`funcoes_teclas` e `funcoes_desenho`).
14. **LOOP PRINCIPAL** — `tratar_eventos` → `atualizar(dt)` → `desenhar`, 60 vezes por segundo.

### As duas máquinas de estados

```
Telas (self.estado):
  menu -> escolha_personagem -> jogando <-> loja / mercado / empresa / colecao / conquistas
                                    \-> vitoria (ao comprar o barco)

Pescaria (self.estado_pesca), dentro de "jogando":
  esperando --ESPAÇO--> isca_na_agua --tempo acabou--> fisgou --ESPAÇO ou tempo--> resultado
      ^                      |                                                        |
      +------ESPAÇO----------+                                                        |
      +--------------------------- ESPAÇO ou 3,5 s ------------------------------------+
```

O "mundo" (relógio do dia, frescor, funcionários, encomendas) continua andando em todas as telas de jogo,
mas não no menu. Por isso a função `atualizar_mundo` é separada de `atualizar_pesca`.

## 6. Conceitos de programação usados

- **Máquina de estados**: variável de texto que decide qual tela é desenhada e recebe o teclado.
- **Dicionário de funções**: `self.funcoes_teclas[self.estado](tecla)` substitui um `if/elif` gigante.
- **Loop de jogo**: eventos → atualização → desenho, a 60 FPS, com `pygame.time.Clock`.
- **Programação orientada a objetos**: classes `Peixe`, `Personagem`, `Funcionario`, `Vendedor`, `Fornecedor`,
  `MinigameCaptura`, `Cenario` e `Jogo`.
- **Estruturas de dados**: listas, dicionários (inclusive aninhados, como `demanda[fornecedor][peixe]`), conjuntos
  (`set`) e list/dict/set comprehensions.
- **Funções `lambda`**: nas conquistas e em `sorted(..., key=...)` / `max(..., key=...)`.
- **Aleatoriedade**: `random.choices` com pesos (sorteio ponderado), `random.choice`, `random.uniform`,
  `random.sample`.
- **Controle de tempo sem travar**: contadores que diminuem `dt` a cada quadro, em vez de `time.sleep`.
- **Movimento independente do FPS**: velocidade multiplicada por `dt`.
- **Arquivos e JSON**: `json.dump` e `json.load`, com `try/except` e compatibilidade com saves antigos.
- **Matemática**: seno (ondas, boia, zona móvel), crescimento exponencial (preço das melhorias),
  porcentagens compostas (demanda, preço de venda), divisão inteira e resto (`//` e `%`).
- **Lógica de economia**: oferta e demanda, limite diário, reputação, lucro = receitas - despesas.

## 7. Perguntas que o professor pode fazer

**1. Como funciona o sorteio do peixe? Por que os raros aparecem menos?**
Em duas etapas. Primeiro `random.choices(ORDEM_RARIDADES, weights=pesos)` sorteia a raridade: os pesos são
6, 55, 25, 12, 3 e 0,5, e a chance de cada uma é o peso dividido pela soma. Depois `random.choice` escolhe um
peixe daquela raridade que viva no local atual. A sorte (personagem, amuleto, noite, neblina) multiplica só
os pesos de raro, lendário e mítico por `(1 + sorte)`.

**2. O que é a máquina de estados e por que usá-la?**
É uma variável que guarda "em que situação o jogo está" (`menu`, `jogando`, `mercado`...). Um dicionário liga
cada estado à sua função de teclas e de desenho. Assim cada tela tem sua lógica separada, e a mesma tecla pode
fazer coisas diferentes em cada uma (ESPAÇO lança a linha, acerta o minigame ou vende um peixe).

**3. Como o jogo espera o peixe morder (e o dia passar) sem usar `sleep`?**
Guardamos um tempo restante e, a cada quadro, subtraímos `dt` (o tempo desde o último quadro). Quando chega a
zero, a ação acontece. O mesmo vale para o fim do dia, a entrega da loja, as encomendas e os funcionários.
Com `sleep`, a janela congelaria.

**4. Como o minigame sabe se o jogador acertou?**
Marcador e zona usam valores de 0.0 a 1.0. Acerta se `abs(posicao - centro_zona) <= largura_zona / 2`.
Em raros e acima, o centro da zona oscila com `math.sin`. No mítico, `apertar()` devolve `"continua"`
no primeiro acerto e sorteia uma nova zona.

**5. Como é calculado o preço de venda?**
`preço = valor × multiplicador × (0,4 + 0,6 × frescor) × (1 + 0,04 × reputação) × demanda`. A função
`preco_venda` devolve 0 se o fornecedor não compra aquela raridade ou se o peixe não está fresco o bastante.
A demanda é multiplicada por 0,92 a cada venda e volta 1% por segundo.

**6. Como funcionam os funcionários e o salário?**
Cada `Funcionario` tem um cronômetro. Quando zera, o jogo sorteia se ele acertou (chance do tipo) e, se sim,
sorteia um peixe e o coloca na mochila. No fim do dia, `fim_do_dia` percorre a lista paga os salários na ordem
da contratação. Quem não puder ser pago é removido da lista (pede demissão).

**7. Como o progresso é salvo? E se o arquivo estiver estragado ou for de uma versão antiga?**
`dados_para_salvar` monta um dicionário só com tipos simples (o personagem vira índice, os funcionários viram
`{"tipo", "nome"}`) e `json.dump` grava. Ao abrir, `carregar_jogo` usa `try/except` e, se o arquivo estiver
corrompido, o jogo começa do zero. Todo campo é lido com `.get(chave, padrão)`, então um save antigo, sem os
campos novos, continua funcionando.

**8. Como o vendedor decide o que vender?**
Em `vendedor_trabalhar`: dois `for` aninhados (fornecedores × espécies na mochila) calculam o preço de cada
combinação com `preco_para`, e guardamos a de maior preço (padrão "achar o máximo"). Peixes pedidos em
encomendas (`especies_reservadas`, um `set`) e raridades fora do alcance dele são ignorados. A venda usa
`tentar_venda(..., comissao)`, a mesma função do jogador, só que com desconto.

**Extra — por que multiplicar a velocidade por `dt`?**
O número de quadros por segundo varia entre computadores. Multiplicando por `dt` (segundos por quadro), o
marcador anda a mesma distância por segundo em qualquer máquina.

**Extra — como evitar que o jogador fique travado sem dinheiro?**
Em `lancar_linha`, se não há iscas, nem moedas para um pacote, nem peixes para vender, o jogo dá 3 iscas.
