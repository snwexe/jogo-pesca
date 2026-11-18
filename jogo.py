# ===== IMPORTAÇÕES =====
# json   -> salvar e carregar o progresso em arquivo
# math   -> função seno, usada para animar ondas, boia e funcionários
# os     -> verificar se o arquivo de save existe e montar o caminho dele
# random -> sortear peixes, tempo da mordida, clima e encomendas
# sys    -> encerrar o programa de forma limpa
# pygame -> biblioteca que cria a janela, lê o teclado e desenha na tela
import json
import math
import os
import random
import sys

import pygame


# ===== CONFIGURAÇÕES E CONSTANTES =====
# Valores fixos ficam aqui no topo para ficar fácil de ajustar o jogo
# sem precisar procurar números "perdidos" no meio do código.
LARGURA = 800
ALTURA = 600
FPS = 60
TITULO = "Pescaria Tranquila - Tycoon"

# O save fica na mesma pasta do jogo.py, não importa de onde o jogo foi aberto.
ARQUIVO_SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save.json")

# Posições do cenário (em pixels)
NIVEL_AGUA = 330          # altura onde começa a água
ALTURA_PIER = NIVEL_AGUA - 25   # altura do chão do pier
POSICAO_PESCADOR = 200    # posição x do pescador em cima do pier
POSICAO_BOIA = 560        # posição x onde a boia cai na água

# Tempos (em segundos)
TEMPO_MINIMO_MORDIDA = 2.0
TEMPO_MAXIMO_MORDIDA = 6.0
TEMPO_TELA_RESULTADO = 3.5
TEMPO_DIA = 120.0               # duração de um "dia" do jogo (salários e vendas fecham no fim dele)
TEMPO_FRESCOR_BASE = 240.0      # em quantos segundos um peixe fica 100% estragado
TEMPO_ENTREGA_POR_NIVEL = 10.0  # a loja demora 10s x (nível novo) para entregar a melhoria

# Economia
ISCAS_INICIAIS = 10
PACOTE_ISCAS = 10               # quantas iscas vêm em cada pacote
PRECO_PACOTE_ISCAS = 20
CAPACIDADE_BASE_MOCHILA = 10
CAPACIDADE_POR_NIVEL = 5
DANO_BOMBA = 25                 # moedas perdidas ao pescar um Peixe-Bomba
MAX_FUNCIONARIOS = 6
CUSTO_BARCO = 8000              # meta final do jogo

# Fornecedores
QUEDA_DEMANDA = 0.92            # cada venda do mesmo peixe derruba o preço em 8%
RECUPERACAO_DEMANDA = 0.01      # o preço volta 1% por segundo
DEMANDA_MINIMA = 0.30           # o preço nunca cai abaixo de 30%
PONTOS_POR_NIVEL_REP = 3        # cada 3 pontos de reputação = 1 nível
NIVEL_MAX_REP = 5
BONUS_PRECO_POR_REP = 0.04      # +4% no preço por nível de reputação
MULT_ENCOMENDA = 1.8            # encomenda paga 1,8x o valor dos peixes

# Cores no formato (vermelho, verde, azul), cada uma de 0 a 255
BRANCO = (255, 255, 255)
PRETO = (25, 25, 35)
CINZA = (120, 120, 130)
CINZA_CLARO = (200, 200, 210)
AMARELO = (255, 215, 70)
VERDE = (70, 200, 90)
VERMELHO = (220, 70, 70)
AZUL_CLARO = (110, 200, 255)
MARROM = (120, 80, 45)
MARROM_ESCURO = (85, 55, 30)
AZUL_AGUA = (45, 125, 195)
AZUL_ESCURO = (25, 80, 140)
CEU_TOPO = (120, 185, 245)
CEU_HORIZONTE = (255, 220, 180)
PELE = (240, 200, 160)
COR_CARD = (40, 55, 85)


# ===== DADOS DAS RARIDADES =====
# Cada raridade tem:
#   peso       -> chance relativa de aparecer (quanto maior, mais comum)
#   cor        -> cor usada nos textos e bordas daquela raridade
#   zona       -> largura da zona verde (fração da barra: 0.25 = 25% da barra)
#   velocidade -> quantas "barras inteiras" o marcador anda por segundo
#   acertos    -> quantas vezes o jogador precisa acertar a zona (mítico = 2)
#   movimento  -> quanto a zona verde balança de um lado para o outro (0 = parada)
#   tempo      -> segundos que o jogador tem para acertar
# Quanto mais raro, menor a zona e mais rápido o marcador = mais difícil.
# "lixo" não é um peixe de verdade: é o grupo de botas velhas, latas e do Peixe-Bomba.
RARIDADES = {
    "lixo":     {"peso": 6,   "cor": (150, 150, 150), "zona": 0.34, "velocidade": 0.60, "acertos": 1, "movimento": 0.00, "tempo": 6.0},
    "comum":    {"peso": 55,  "cor": (230, 230, 230), "zona": 0.26, "velocidade": 0.70, "acertos": 1, "movimento": 0.00, "tempo": 6.0},
    "incomum":  {"peso": 25,  "cor": (110, 220, 110), "zona": 0.19, "velocidade": 0.90, "acertos": 1, "movimento": 0.00, "tempo": 6.0},
    "raro":     {"peso": 12,  "cor": (90, 160, 255),  "zona": 0.13, "velocidade": 1.15, "acertos": 1, "movimento": 0.10, "tempo": 6.0},
    "lendário": {"peso": 3,   "cor": (255, 190, 40),  "zona": 0.09, "velocidade": 1.40, "acertos": 1, "movimento": 0.18, "tempo": 6.0},
    "mítico":   {"peso": 0.5, "cor": (255, 90, 200),  "zona": 0.08, "velocidade": 1.55, "acertos": 2, "movimento": 0.22, "tempo": 9.0},
}

# Lista com a ordem das raridades. Usamos uma lista separada para garantir
# que os pesos e as raridades fiquem sempre na mesma posição no sorteio.
ORDEM_RARIDADES = ["lixo", "comum", "incomum", "raro", "lendário", "mítico"]

# A sorte (personagem, amuleto, noite...) só aumenta o peso destas raridades.
RARIDADES_COM_SORTE = ("raro", "lendário", "mítico")

# Se o jogador ERRAR um peixe valioso, a linha pode quebrar (e custa moedas).
CHANCE_QUEBRA = {"raro": 0.30, "lendário": 0.50, "mítico": 0.70}
CUSTO_QUEBRA = {"raro": 15, "lendário": 40, "mítico": 90}


# ===== LOCAIS DE PESCA =====
# Cada local tem um custo de licença e cores de água próprias.
LOCAIS = {
    "rio":  {"nome": "Rio",  "agua": (70, 140, 125), "fundo": (35, 90, 80)},
    "lago": {"nome": "Lago", "agua": AZUL_AGUA,      "fundo": AZUL_ESCURO},
    "mar":  {"nome": "Mar",  "agua": (30, 100, 175), "fundo": (12, 50, 115)},
}
ORDEM_LOCAIS = ["rio", "lago", "mar"]


# ===== DADOS DOS PEIXES =====
# Lista de dicionários: cada dicionário descreve um peixe do jogo.
#   locais -> em quais locais de pesca ele aparece
#   efeito -> None = peixe normal; "lixo" = vale poucas moedas na hora; "bomba" = causa prejuízo
# Estão em ordem de raridade para a coleção ficar organizada.
DADOS_PEIXES = [
    # --- comuns ---
    {"nome": "Lambari",          "raridade": "comum",    "valor": 5,    "cor": (190, 200, 210), "tamanho": 20, "locais": ("rio", "lago")},
    {"nome": "Piaba",            "raridade": "comum",    "valor": 4,    "cor": (200, 170, 150), "tamanho": 16, "locais": ("rio",)},
    {"nome": "Tilápia",          "raridade": "comum",    "valor": 8,    "cor": (150, 165, 120), "tamanho": 26, "locais": ("rio", "lago")},
    {"nome": "Bagre",            "raridade": "comum",    "valor": 7,    "cor": (110, 100, 90),  "tamanho": 24, "locais": ("rio",)},
    {"nome": "Carpa",            "raridade": "comum",    "valor": 9,    "cor": (210, 150, 90),  "tamanho": 26, "locais": ("lago",)},
    {"nome": "Sardinha",         "raridade": "comum",    "valor": 6,    "cor": (120, 150, 200), "tamanho": 18, "locais": ("mar",)},
    {"nome": "Anchova",          "raridade": "comum",    "valor": 7,    "cor": (140, 170, 180), "tamanho": 20, "locais": ("mar",)},
    {"nome": "Manjuba",          "raridade": "comum",    "valor": 5,    "cor": (170, 190, 215), "tamanho": 16, "locais": ("mar",)},
    # --- incomuns ---
    {"nome": "Pacu",             "raridade": "incomum",  "valor": 18,   "cor": (100, 100, 125), "tamanho": 30, "locais": ("rio",)},
    {"nome": "Traíra",           "raridade": "incomum",  "valor": 22,   "cor": (90, 120, 90),   "tamanho": 32, "locais": ("rio",)},
    {"nome": "Tucunaré",         "raridade": "incomum",  "valor": 25,   "cor": (210, 180, 60),  "tamanho": 34, "locais": ("rio", "lago")},
    {"nome": "Truta",            "raridade": "incomum",  "valor": 24,   "cor": (150, 190, 150), "tamanho": 30, "locais": ("lago",)},
    {"nome": "Robalo",           "raridade": "incomum",  "valor": 20,   "cor": (130, 150, 170), "tamanho": 32, "locais": ("lago", "mar")},
    {"nome": "Tainha",           "raridade": "incomum",  "valor": 19,   "cor": (160, 170, 175), "tamanho": 30, "locais": ("mar",)},
    {"nome": "Atum Jovem",       "raridade": "incomum",  "valor": 28,   "cor": (70, 90, 150),   "tamanho": 34, "locais": ("mar",)},
    # --- raros ---
    {"nome": "Dourado",          "raridade": "raro",     "valor": 60,   "cor": (245, 170, 30),  "tamanho": 38, "locais": ("rio",)},
    {"nome": "Surubim",          "raridade": "raro",     "valor": 75,   "cor": (120, 120, 110), "tamanho": 40, "locais": ("rio",)},
    {"nome": "Salmão",           "raridade": "raro",     "valor": 70,   "cor": (240, 125, 115), "tamanho": 36, "locais": ("lago",)},
    {"nome": "Esturjão",         "raridade": "raro",     "valor": 85,   "cor": (130, 130, 150), "tamanho": 42, "locais": ("lago",)},
    {"nome": "Peixe-Espada",     "raridade": "raro",     "valor": 80,   "cor": (170, 190, 230), "tamanho": 42, "locais": ("mar",)},
    {"nome": "Barracuda",        "raridade": "raro",     "valor": 90,   "cor": (150, 160, 170), "tamanho": 40, "locais": ("mar",)},
    {"nome": "Linguado",         "raridade": "raro",     "valor": 65,   "cor": (190, 160, 120), "tamanho": 36, "locais": ("mar",)},
    # --- lendários ---
    {"nome": "Pirarucu Gigante", "raridade": "lendário", "valor": 250,  "cor": (175, 60, 50),   "tamanho": 46, "locais": ("rio",)},
    {"nome": "Peixe Arco-Íris",  "raridade": "lendário", "valor": 300,  "cor": (200, 100, 225), "tamanho": 40, "locais": ("lago",)},
    {"nome": "Lúcio Dourado",    "raridade": "lendário", "valor": 320,  "cor": (230, 200, 70),  "tamanho": 44, "locais": ("lago",)},
    {"nome": "Tubarão-Branco",   "raridade": "lendário", "valor": 400,  "cor": (200, 205, 215), "tamanho": 48, "locais": ("mar",)},
    {"nome": "Arraia-Manta",     "raridade": "lendário", "valor": 350,  "cor": (60, 70, 110),   "tamanho": 46, "locais": ("mar",)},
    # --- míticos ---
    {"nome": "Dragão-do-Rio",    "raridade": "mítico",   "valor": 1000, "cor": (60, 200, 150),  "tamanho": 50, "locais": ("rio",)},
    {"nome": "Peixe-Lua",        "raridade": "mítico",   "valor": 1200, "cor": (235, 235, 255), "tamanho": 48, "locais": ("lago",)},
    {"nome": "Kraken Bebê",      "raridade": "mítico",   "valor": 1500, "cor": (140, 60, 170),  "tamanho": 50, "locais": ("mar",)},
    # --- lixo e perigo (aparecem em todos os locais) ---
    {"nome": "Bota Velha",       "raridade": "lixo",     "valor": 1,    "cor": (110, 85, 60),   "tamanho": 20, "locais": ORDEM_LOCAIS, "efeito": "lixo"},
    {"nome": "Lata Enferrujada", "raridade": "lixo",     "valor": 2,    "cor": (160, 100, 70),  "tamanho": 18, "locais": ORDEM_LOCAIS, "efeito": "lixo"},
    {"nome": "Alga Pegajosa",    "raridade": "lixo",     "valor": 1,    "cor": (70, 130, 70),   "tamanho": 20, "locais": ORDEM_LOCAIS, "efeito": "lixo"},
    {"nome": "Peixe-Bomba",      "raridade": "lixo",     "valor": 0,    "cor": (40, 40, 50),    "tamanho": 22, "locais": ORDEM_LOCAIS, "efeito": "bomba"},
]


# ===== CLASSE PEIXE =====
class Peixe:
    """Representa um tipo de peixe: nome, raridade, valor em moedas, aparência e onde aparece."""

    def __init__(self, nome, raridade, valor, cor, tamanho, locais, efeito=None):
        self.nome = nome
        self.raridade = raridade
        self.valor = valor
        self.cor = cor
        self.tamanho = tamanho
        self.locais = locais
        self.efeito = efeito


# Transformamos a lista de dicionários em uma lista de objetos Peixe.
# O "**dados" passa cada chave do dicionário como parâmetro do __init__.
PEIXES = [Peixe(**dados) for dados in DADOS_PEIXES]

# Dicionário para achar um peixe pelo nome rapidamente (a mochila guarda só o nome).
PEIXE_POR_NOME = {peixe.nome: peixe for peixe in PEIXES}

# Só os peixes "de verdade" entram na coleção (lixo e bomba ficam de fora).
PEIXES_COLECAO = [peixe for peixe in PEIXES if peixe.efeito is None]


# ===== CLASSE PERSONAGEM =====
class Personagem:
    """
    Um pescador jogável. Cada um tem um atributo especial:
      multiplicador_espera -> menor que 1 = peixe morde mais rápido
      sorte                -> aumenta a chance de peixes raros, lendários e míticos
      bonus_zona           -> deixa a zona verde do minigame maior
    """

    def __init__(self, nome, cor, descricao, multiplicador_espera=1.0, sorte=0.0, bonus_zona=0.0):
        self.nome = nome
        self.cor = cor
        self.descricao = descricao
        self.multiplicador_espera = multiplicador_espera
        self.sorte = sorte
        self.bonus_zona = bonus_zona


# Os 3 pescadores disponíveis. Cada um é bom em uma coisa diferente,
# assim a escolha muda o jeito de jogar.
PERSONAGENS = [
    Personagem("Zé Ligeiro", (220, 70, 60), "Vara rápida: peixes mordem antes",
               multiplicador_espera=0.6),
    Personagem("Dona Sortuda", (60, 170, 80), "Sorte: mais peixes raros",
               sorte=0.6),
    Personagem("Capitão Firme", (60, 100, 210), "Mão firme: zona verde maior",
               bonus_zona=0.06),
]


# ===== HORÁRIO E CLIMA =====
# O dia do jogo (TEMPO_DIA) é dividido em manhã, tarde e noite.
# "ate" é a fração do dia em que o horário termina (0.40 = 40% do dia).
HORARIOS = {
    "manhã": {"ate": 0.40, "sorte": 0.0, "espera": 1.0},
    "tarde": {"ate": 0.75, "sorte": 0.0, "espera": 0.9},
    "noite": {"ate": 1.01, "sorte": 0.5, "espera": 1.2},   # mais raros, mas a mordida demora
}
ORDEM_HORARIOS = ["manhã", "tarde", "noite"]

# O clima é sorteado no começo de cada dia.
CLIMAS = {
    "sol":     {"peso": 50, "sorte": 0.0, "espera": 1.00, "zona": 0.00, "descricao": "Dia normal"},
    "chuva":   {"peso": 30, "sorte": 0.0, "espera": 0.75, "zona": -0.03, "descricao": "Mordem mais rápido, zona menor"},
    "neblina": {"peso": 20, "sorte": 0.4, "espera": 1.10, "zona": 0.00, "descricao": "Mais raros, mordida lenta"},
}


def horario_atual(fracao_do_dia):
    """Recebe um número de 0.0 a 1.0 (quanto do dia já passou) e devolve 'manhã', 'tarde' ou 'noite'."""
    for nome in ORDEM_HORARIOS:
        if fracao_do_dia < HORARIOS[nome]["ate"]:
            return nome
    return "noite"


def sortear_clima():
    """Sorteia o clima do dia usando pesos (sol é mais comum que neblina)."""
    nomes = list(CLIMAS.keys())
    pesos = [CLIMAS[nome]["peso"] for nome in nomes]
    return random.choices(nomes, weights=pesos, k=1)[0]


# ===== SORTEIO DO PEIXE =====
def calcular_pesos(sorte):
    """
    Devolve a lista de pesos de cada raridade, já ajustada pela sorte.
    A sorte multiplica só os pesos de "raro", "lendário" e "mítico": com sorte 0.6,
    por exemplo, o peso do raro vai de 12 para 19.2.
    """
    pesos = []
    for raridade in ORDEM_RARIDADES:
        peso = RARIDADES[raridade]["peso"]
        if raridade in RARIDADES_COM_SORTE:
            peso = peso * (1 + sorte)
        pesos.append(peso)
    return pesos


def sortear_peixe(sorte, local):
    """
    Sorteia um peixe em duas etapas:
      1) sorteia a RARIDADE com random.choices, que respeita os pesos;
      2) sorteia um peixe DENTRO daquela raridade que viva no local de pesca atual.
    """
    pesos = calcular_pesos(sorte)
    # random.choices devolve uma lista; como k=1, pegamos o primeiro item [0]
    raridade_sorteada = random.choices(ORDEM_RARIDADES, weights=pesos, k=1)[0]
    candidatos = [peixe for peixe in PEIXES
                  if peixe.raridade == raridade_sorteada and local in peixe.locais]
    return random.choice(candidatos)


def sortear_tempo_mordida(multiplicador_espera):
    """Tempo aleatório (em segundos) até o peixe morder a isca."""
    return random.uniform(TEMPO_MINIMO_MORDIDA, TEMPO_MAXIMO_MORDIDA) * multiplicador_espera


# ===== MINIGAME DE CAPTURA =====
class MinigameCaptura:
    """
    Barra de timing: um marcador vai e volta e o jogador precisa apertar
    ESPAÇO quando ele estiver dentro da zona verde.
    Todas as posições vão de 0.0 (início da barra) a 1.0 (fim da barra).
    Assim a lógica não depende do tamanho da barra na tela.

    Cada raridade muda o minigame:
      raro/lendário/mítico -> a zona verde balança de um lado para o outro
      mítico               -> é preciso acertar DUAS vezes seguidas
    """

    def __init__(self, peixe, bonus_zona):
        dificuldade = RARIDADES[peixe.raridade]
        # A zona nunca passa de metade da barra (fácil demais) nem fica menor que 6%.
        self.largura_zona = max(0.06, min(dificuldade["zona"] + bonus_zona, 0.5))
        self.velocidade = dificuldade["velocidade"]
        self.amplitude = dificuldade["movimento"]
        self.acertos_necessarios = dificuldade["acertos"]
        self.acertos_feitos = 0
        self.tempo_limite = dificuldade["tempo"]
        self.tempo_restante = self.tempo_limite
        self.posicao = 0.0
        self.direcao = 1  # 1 = indo para a direita, -1 = indo para a esquerda
        self.tempo = 0.0
        self.sortear_zona()

    def sortear_zona(self):
        """Sorteia onde fica a zona verde, sem deixá-la sair da barra."""
        metade = self.largura_zona / 2
        self.centro_base = random.uniform(metade, 1 - metade)
        self.centro_zona = self.centro_base
        self.fase = random.uniform(0, 6.28)   # cada zona começa o balanço em um ponto diferente

    def atualizar(self, dt):
        """Move o marcador. dt = segundos desde o último quadro."""
        self.tempo += dt
        # Multiplicar por dt faz a velocidade ser igual em qualquer computador,
        # mesmo que o FPS varie.
        self.posicao += self.velocidade * self.direcao * dt
        # Quando bate em uma ponta, inverte a direção (efeito "vai e volta").
        if self.posicao >= 1.0:
            self.posicao = 1.0
            self.direcao = -1
        elif self.posicao <= 0.0:
            self.posicao = 0.0
            self.direcao = 1
        # Zona móvel: o centro oscila com seno em volta do ponto base.
        if self.amplitude > 0:
            metade = self.largura_zona / 2
            deslocamento = math.sin(self.tempo * 1.5 + self.fase) * self.amplitude
            # min/max seguram o centro dentro da barra
            self.centro_zona = min(max(self.centro_base + deslocamento, metade), 1 - metade)
        # Contador regressivo: o jogo não trava, só diminuímos um número.
        self.tempo_restante -= dt

    def acabou_tempo(self):
        return self.tempo_restante <= 0

    def verificar_acerto(self):
        """Acertou se a distância do marcador até o centro da zona for no máximo meia zona."""
        return abs(self.posicao - self.centro_zona) <= self.largura_zona / 2

    def apertar(self):
        """
        Chamado quando o jogador aperta ESPAÇO. Devolve:
          "falhou"   -> o marcador estava fora da zona
          "continua" -> acertou, mas ainda faltam acertos (peixe mítico)
          "capturou" -> acertou todas as vezes necessárias
        """
        if not self.verificar_acerto():
            return "falhou"
        self.acertos_feitos += 1
        if self.acertos_feitos >= self.acertos_necessarios:
            return "capturou"
        self.sortear_zona()   # nova zona para o segundo acerto
        return "continua"


# ===== LOJA DE PESCA (MELHORIAS) =====
# Dicionário com as melhorias à venda. A chave ("vara", "carretilha"...)
# é a mesma usada no dicionário de níveis do jogador e no save.
MELHORIAS = {
    "vara":       {"nome": "Vara melhor",    "descricao": "Zona verde maior no minigame",           "preco_base": 30,  "nivel_maximo": 6},
    "carretilha": {"nome": "Carretilha",     "descricao": "Peixes mordem mais rápido",              "preco_base": 25,  "nivel_maximo": 6},
    "amuleto":    {"nome": "Amuleto",        "descricao": "Mais chance de peixes raros",            "preco_base": 40,  "nivel_maximo": 5},
    # A mochila cresce até 200 peixes (10 + 5 x 38 níveis). O preço dela sobe só 12% por nível
    # ("crescimento"), senão os últimos níveis ficariam impossíveis de pagar.
    "mochila":    {"nome": "Mochila maior",  "descricao": "+5 espaços (até 200 peixes)",            "preco_base": 35,  "nivel_maximo": 38, "crescimento": 1.12},
    "linha":      {"nome": "Linha reforçada", "descricao": "A linha quebra com menos frequência",   "preco_base": 30,  "nivel_maximo": 5},
    "rede":       {"nome": "Rede",           "descricao": "Chance de pegar um peixe extra",         "preco_base": 50,  "nivel_maximo": 5},
    "sonar":      {"nome": "Sonar",          "descricao": "Mostra o peixe antes de fisgar",         "preco_base": 100, "nivel_maximo": 3},
    "geladeira":  {"nome": "Geladeira",      "descricao": "Peixes estragam mais devagar",           "preco_base": 45,  "nivel_maximo": 4},
    "contratos":  {"nome": "Contratos",      "descricao": "+3 vendas por dia em cada fornecedor",   "preco_base": 60,  "nivel_maximo": 10, "crescimento": 1.5},
}

# Ordem em que aparecem na loja (teclas 1 a 9)
ORDEM_MELHORIAS = ["vara", "carretilha", "amuleto", "mochila", "linha", "rede", "sonar", "geladeira", "contratos"]

# Quanto cada nível de melhoria acrescenta
BONUS_ZONA_POR_NIVEL = 0.025        # +2,5% de barra verde por nível
REDUCAO_ESPERA_POR_NIVEL = 0.09     # -9% de tempo de espera por nível
SORTE_POR_NIVEL = 0.3               # +0.3 de sorte por nível
REDUCAO_QUEBRA_POR_NIVEL = 0.15     # -15% de chance de a linha quebrar por nível
CHANCE_REDE_POR_NIVEL = 0.08        # +8% de chance de peixe extra por nível
BONUS_FRESCOR_POR_NIVEL = 0.5       # +50% de tempo até estragar por nível
BONUS_LIMITE_POR_NIVEL = 3          # +3 vendas por dia, em cada fornecedor, por nível de Contratos
TEMPO_ENTREGA_MAXIMO = 60.0         # a loja nunca demora mais que 60s para entregar


def preco_melhoria(chave, nivel_atual):
    """
    O preço cresce a cada compra (crescimento exponencial): 60% por nível, a não ser que a
    melhoria tenha o seu próprio "crescimento". Assim as primeiras melhorias são baratas
    e as últimas exigem mais pesca.
    """
    crescimento = MELHORIAS[chave].get("crescimento", 1.6)
    return int(MELHORIAS[chave]["preco_base"] * (crescimento ** nivel_atual))


# ===== EXPANSÕES DO NEGÓCIO =====
# Licenças liberam novos locais de pesca. O barco é a META FINAL.
# "requer" é a expansão que precisa ter sido comprada antes.
EXPANSOES = [
    {"id": "lago",  "nome": "Licença do Lago",  "descricao": "Libera o Lago: peixes novos e raros",  "custo": 400,        "requer": None},
    {"id": "mar",   "nome": "Licença do Mar",   "descricao": "Libera o Mar: os peixes mais valiosos", "custo": 1500,       "requer": "lago"},
    {"id": "barco", "nome": "Barco Pesqueiro",  "descricao": "META FINAL: vença o jogo!",             "custo": CUSTO_BARCO, "requer": "mar"},
]


# ===== FUNCIONÁRIOS =====
# Cada tipo de funcionário pesca sozinho e coloca o peixe na mochila.
#   custo     -> pago uma vez para contratar
#   salario   -> pago TODO FIM DE DIA (se faltar dinheiro, ele pede demissão)
#   intervalo -> a cada quantos segundos ele puxa a linha
#   acerto    -> chance (0 a 1) de ele conseguir pescar cada vez
#   sorte     -> igual à sorte do jogador (mais raros)
TIPOS_FUNCIONARIO = [
    {"nome": "Aprendiz", "custo": 80,  "salario": 12, "intervalo": 20.0, "acerto": 0.55, "sorte": 0.0, "cor": (200, 160, 90)},
    {"nome": "Pescador", "custo": 250, "salario": 30, "intervalo": 14.0, "acerto": 0.70, "sorte": 0.3, "cor": (90, 170, 200)},
    {"nome": "Mestre",   "custo": 700, "salario": 70, "intervalo": 9.0,  "acerto": 0.85, "sorte": 0.8, "cor": (230, 190, 60)},
]
NOMES_FUNCIONARIOS = ["Zeca", "Bia", "Tonho", "Lúcia", "Nando", "Cida", "Beto", "Rita"]


class Funcionario:
    """Um pescador contratado. Guarda o tipo e um cronômetro até a próxima pescaria."""

    def __init__(self, indice_tipo, nome=None):
        self.indice_tipo = indice_tipo
        self.tipo = TIPOS_FUNCIONARIO[indice_tipo]
        self.nome = nome or random.choice(NOMES_FUNCIONARIOS)
        self.tempo = self.sortear_intervalo()
        self.fase = random.uniform(0, 6.28)   # só para a boia de cada um balançar diferente

    def sortear_intervalo(self):
        # Varia 20% para cima ou para baixo, para os funcionários não pescarem todos juntos.
        return self.tipo["intervalo"] * random.uniform(0.8, 1.2)

    def atualizar(self, dt):
        """Diminui o cronômetro. Devolve True quando chegou a hora de puxar a linha."""
        self.tempo -= dt
        if self.tempo <= 0:
            self.tempo = self.sortear_intervalo()
            return True
        return False


# ===== VENDEDORES =====
# Vendedores esvaziam a mochila sozinhos, para os pescadores continuarem pescando.
# Eles ficam com uma COMISSÃO de cada venda e também recebem salário no fim do dia.
#   intervalo -> a cada quantos segundos fazem uma venda
#   comissao  -> fração do preço que fica com o vendedor (0.20 = ele leva 20%)
#   raridades -> só vendem peixes destas raridades (os mais raros ficam para você)
#   entrega   -> True = também cumpre encomendas sozinho
# Os vendedores NUNCA vendem peixes que estão pedidos em uma encomenda ativa.
TIPOS_VENDEDOR = [
    {"nome": "Ambulante",         "custo": 150,  "salario": 15,  "intervalo": 8.0, "comissao": 0.20,
     "raridades": ("comum", "incomum"), "entrega": False, "cor": (240, 130, 90)},
    {"nome": "Representante",     "custo": 500,  "salario": 40,  "intervalo": 5.0, "comissao": 0.12,
     "raridades": ("comum", "incomum", "raro"), "entrega": False, "cor": (150, 110, 220)},
    {"nome": "Gerente de Vendas", "custo": 1500, "salario": 100, "intervalo": 3.0, "comissao": 0.08,
     "raridades": ("comum", "incomum", "raro", "lendário", "mítico"), "entrega": True, "cor": (240, 240, 240)},
]
NOMES_VENDEDORES = ["Marcos", "Tati", "Rogério", "Vera", "Caio", "Dani"]
MAX_VENDEDORES = 3


class Vendedor:
    """Um vendedor contratado. Funciona igual ao Funcionario: um cronômetro que dispara a cada venda."""

    def __init__(self, indice_tipo, nome=None):
        self.indice_tipo = indice_tipo
        self.tipo = TIPOS_VENDEDOR[indice_tipo]
        self.nome = nome or random.choice(NOMES_VENDEDORES)
        self.tempo = self.tipo["intervalo"]
        self.fase = random.uniform(0, 6.28)

    def atualizar(self, dt):
        """Devolve True quando chegou a hora de tentar uma venda."""
        self.tempo -= dt
        if self.tempo <= 0:
            self.tempo = self.tipo["intervalo"]
            return True
        return False


# ===== FORNECEDORES =====
class Fornecedor:
    """
    Um comprador de peixes. Cada um paga um preço diferente por raridade.
      mult_raridade  -> multiplica o valor do peixe (0 = não compra aquela raridade)
      frescor_minimo -> só compra peixe com pelo menos essa frescura (0.6 = 60%)
      limite_dia     -> quantos peixes ele compra por dia
    """

    def __init__(self, nome, descricao, cor, mult_raridade, frescor_minimo, limite_dia):
        self.nome = nome
        self.descricao = descricao
        self.cor = cor
        self.mult_raridade = mult_raridade
        self.frescor_minimo = frescor_minimo
        self.limite_dia = limite_dia


FORNECEDORES = [
    Fornecedor("Peixaria do Zé", "Paga bem por peixe comum", (220, 160, 80),
               {"comum": 1.3, "incomum": 1.1, "raro": 0.9, "lendário": 0.7, "mítico": 0.7}, 0.0, 8),
    Fornecedor("Mercado Central", "Compra de tudo, preço justo", (110, 200, 110),
               {"comum": 1.0, "incomum": 1.0, "raro": 1.0, "lendário": 1.0, "mítico": 1.0}, 0.0, 14),
    Fornecedor("Restaurante Chique", "Só peixe fresco, paga caro por raros", (200, 110, 210),
               {"comum": 0.7, "incomum": 0.9, "raro": 1.5, "lendário": 1.7, "mítico": 1.6}, 0.6, 5),
    Fornecedor("Exportadora", "Só raros ou melhores, preço de exportação", (90, 170, 255),
               {"comum": 0, "incomum": 0, "raro": 1.35, "lendário": 1.5, "mítico": 1.8}, 0.3, 4),
]

# Quantidade (mínimo, máximo) de peixes pedida numa encomenda, por raridade.
QUANTIDADE_ENCOMENDA = {"comum": (2, 4), "incomum": (2, 3), "raro": (1, 2), "lendário": (1, 1)}


def frescor_do_peixe(idade, tempo_estragar):
    """Frescor de 1.0 (acabou de pescar) a 0.0 (estragado). Cai de forma linear com a idade."""
    return max(0.0, 1.0 - idade / tempo_estragar)


def preco_venda(fornecedor, peixe, frescor, nivel_rep, demanda):
    """
    Preço que o fornecedor paga por UM peixe. Devolve 0 se ele não compra.
      preço = valor x multiplicador da raridade x fator de frescor x bônus de reputação x demanda
    O fator de frescor vai de 0.4 (estragado) a 1.0 (fresquinho).
    """
    mult = fornecedor.mult_raridade.get(peixe.raridade, 0)
    if mult == 0 or frescor < fornecedor.frescor_minimo:
        return 0
    fator_frescor = 0.4 + 0.6 * frescor
    bonus_rep = 1 + BONUS_PRECO_POR_REP * nivel_rep
    return max(1, round(peixe.valor * mult * fator_frescor * bonus_rep * demanda))


def nivel_reputacao(pontos):
    """Cada 3 pontos de reputação = 1 nível (máximo 5). // é a divisão inteira."""
    return min(pontos // PONTOS_POR_NIVEL_REP, NIVEL_MAX_REP)


def gerar_encomenda(fornecedor, especies):
    """
    Cria um pedido: de 1 a 2 tipos de peixe que ESTE fornecedor compra.
    O prazo cresce com a quantidade pedida, e a recompensa é MULT_ENCOMENDA x o valor dos peixes.
    """
    possiveis = [p for p in especies if fornecedor.mult_raridade.get(p.raridade, 0) > 0]
    escolhidos = random.sample(possiveis, min(random.randint(1, 2), len(possiveis)))
    pedidos = {}
    valor_total = 0
    for peixe in escolhidos:
        minimo, maximo = QUANTIDADE_ENCOMENDA[peixe.raridade]
        quantidade = random.randint(minimo, maximo)
        pedidos[peixe.nome] = quantidade
        valor_total += peixe.valor * quantidade
    tempo = 100 + 40 * sum(pedidos.values())
    return {"pedidos": pedidos, "tempo": float(tempo), "recompensa": int(valor_total * MULT_ENCOMENDA)}


# ===== COLEÇÃO =====
def criar_colecao_vazia():
    """Dicionário nome do peixe -> quantas vezes foi pescado (começa tudo em 0)."""
    return {peixe.nome: 0 for peixe in PEIXES_COLECAO}


def contar_descobertos(colecao):
    """Conta quantos peixes diferentes já foram pescados pelo menos uma vez."""
    return sum(1 for quantidade in colecao.values() if quantidade > 0)


def colecao_completa(colecao):
    return contar_descobertos(colecao) == len(PEIXES_COLECAO)


# ===== ESTATÍSTICAS E CONQUISTAS =====
def criar_estatisticas():
    """Contadores usados pelas conquistas. Todos começam em zero."""
    return {"pescados": 0, "lendarios": 0, "miticos": 0, "maior_combo": 0, "vendas": 0,
            "encomendas": 0, "bombas": 0, "linhas_quebradas": 0, "fugas": 0, "dias": 0}


# Cada conquista é um dicionário com uma "condicao": uma função lambda (função de uma linha
# sem nome) que recebe o jogo e devolve True quando a conquista foi cumprida.
CONQUISTAS = [
    {"id": "primeiro",   "nome": "Primeira fisgada",  "descricao": "Pesque seu primeiro peixe",
     "condicao": lambda j: j.estat["pescados"] >= 1},
    {"id": "pescador25", "nome": "Pescador dedicado", "descricao": "Pesque 25 peixes",
     "condicao": lambda j: j.estat["pescados"] >= 25},
    {"id": "pescador100", "nome": "Lenda do pier",    "descricao": "Pesque 100 peixes",
     "condicao": lambda j: j.estat["pescados"] >= 100},
    {"id": "lendario",   "nome": "Sorte grande",      "descricao": "Pesque um peixe lendário",
     "condicao": lambda j: j.estat["lendarios"] >= 1},
    {"id": "mitico",     "nome": "Quase impossível",  "descricao": "Pesque um peixe mítico",
     "condicao": lambda j: j.estat["miticos"] >= 1},
    {"id": "combo5",     "nome": "Pegou o ritmo",     "descricao": "Faça um combo de 5",
     "condicao": lambda j: j.estat["maior_combo"] >= 5},
    {"id": "combo10",    "nome": "Imparável",         "descricao": "Faça um combo de 10",
     "condicao": lambda j: j.estat["maior_combo"] >= 10},
    {"id": "colecao15",  "nome": "Colecionador",      "descricao": "Descubra 15 espécies",
     "condicao": lambda j: contar_descobertos(j.colecao) >= 15},
    {"id": "colecao",    "nome": "Mestre da pesca",   "descricao": "Complete a coleção",
     "condicao": lambda j: colecao_completa(j.colecao)},
    {"id": "venda",      "nome": "Primeira venda",    "descricao": "Venda um peixe",
     "condicao": lambda j: j.estat["vendas"] >= 1},
    {"id": "patrao",     "nome": "Patrão",            "descricao": "Contrate um funcionário",
     "condicao": lambda j: len(j.funcionarios) >= 1},
    {"id": "vendedor",   "nome": "Rede de vendas",    "descricao": "Contrate um vendedor",
     "condicao": lambda j: len(j.vendedores) >= 1},
    {"id": "gerente",    "nome": "Império comercial", "descricao": "Contrate um Gerente de Vendas",
     "condicao": lambda j: any(v.indice_tipo == 2 for v in j.vendedores)},
    {"id": "equipe",     "nome": "Empresário",        "descricao": "Tenha 6 funcionários",
     "condicao": lambda j: len(j.funcionarios) >= MAX_FUNCIONARIOS},
    {"id": "enc1",       "nome": "Entregador",        "descricao": "Cumpra uma encomenda",
     "condicao": lambda j: j.estat["encomendas"] >= 1},
    {"id": "enc5",       "nome": "Fornecedor oficial", "descricao": "Cumpra 5 encomendas",
     "condicao": lambda j: j.estat["encomendas"] >= 5},
    {"id": "rico",       "nome": "Ficando rico",      "descricao": "Tenha 1000 moedas",
     "condicao": lambda j: j.moedas >= 1000},
    {"id": "boom",       "nome": "BOOM!",             "descricao": "Exploda um Peixe-Bomba",
     "condicao": lambda j: j.estat["bombas"] >= 1},
    {"id": "quebrou",    "nome": "Linha fraca",       "descricao": "Quebre a linha pescando",
     "condicao": lambda j: j.estat["linhas_quebradas"] >= 1},
    {"id": "explorador", "nome": "Explorador",        "descricao": "Libere todos os locais",
     "condicao": lambda j: len(j.locais_liberados) == len(ORDEM_LOCAIS)},
]


# ===== SALVAR E CARREGAR =====
def salvar_jogo(dados):
    """Escreve o dicionário de progresso no arquivo save.json."""
    try:
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
            # indent=4 deixa o arquivo legível; ensure_ascii=False mantém os acentos
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    except OSError as erro:
        print("Não foi possível salvar o jogo:", erro)


def carregar_jogo():
    """Lê o save.json. Devolve um dicionário, ou None se não existir ou estiver corrompido."""
    if not os.path.exists(ARQUIVO_SAVE):
        return None
    try:
        with open(ARQUIVO_SAVE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        # Se o JSON for válido mas não for um dicionário, também ignoramos.
        return dados if isinstance(dados, dict) else None
    except (OSError, json.JSONDecodeError):
        # Se o arquivo estiver estragado, começamos do zero em vez de travar o jogo.
        print("Save inválido, começando um jogo novo.")
        return None


def formatar_tempo(segundos):
    """Transforma segundos em texto 'minutos:segundos' (ex.: 135 vira '2:15')."""
    segundos = max(0, int(segundos))
    return f"{segundos // 60}:{segundos % 60:02d}"


# ===== DESENHO DA TELA =====
def desenhar_texto(tela, texto, fonte, cor, x, y, centralizado=False):
    """Escreve um texto na tela. Se centralizado=True, (x, y) é o centro do texto."""
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect()
    if centralizado:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    tela.blit(imagem, retangulo)


def desenhar_texto_sombra(tela, texto, fonte, cor, x, y, centralizado=False):
    """Mesmo que desenhar_texto, mas com uma sombra preta atrás para dar leitura sobre o cenário."""
    desenhar_texto(tela, texto, fonte, PRETO, x + 1, y + 1, centralizado)
    desenhar_texto(tela, texto, fonte, cor, x, y, centralizado)


def desenhar_painel(tela, retangulo, cor_borda=BRANCO):
    """Caixa escura semitransparente usada nas telas de loja, coleção, etc."""
    # Uma Surface com SRCALPHA aceita transparência (o 4º número da cor).
    painel = pygame.Surface((retangulo.width, retangulo.height), pygame.SRCALPHA)
    pygame.draw.rect(painel, (20, 30, 50, 225), painel.get_rect(), border_radius=12)
    tela.blit(painel, retangulo.topleft)
    pygame.draw.rect(tela, cor_borda, retangulo, 3, border_radius=12)


def desenhar_peixe(tela, x, y, cor, tamanho):
    """Desenha um peixe simples com formas: corpo (elipse), rabo (triângulo) e olho."""
    corpo = pygame.Rect(0, 0, tamanho * 2, tamanho)
    corpo.center = (x, y)
    rabo = [(corpo.left + 4, y), (corpo.left - tamanho // 2, y - tamanho // 2),
            (corpo.left - tamanho // 2, y + tamanho // 2)]
    pygame.draw.polygon(tela, cor, rabo)
    pygame.draw.ellipse(tela, cor, corpo)
    pygame.draw.ellipse(tela, PRETO, corpo, 2)
    pygame.draw.circle(tela, BRANCO, (corpo.right - tamanho // 2, y - tamanho // 6), max(3, tamanho // 6))
    pygame.draw.circle(tela, PRETO, (corpo.right - tamanho // 2, y - tamanho // 6), max(1, tamanho // 12))


def desenhar_item(tela, x, y, peixe, tamanho):
    """Desenha um peixe, uma bomba (círculo com pavio) ou um lixo (retângulo), conforme o efeito."""
    if peixe.efeito == "bomba":
        raio = tamanho // 2 + 4
        pygame.draw.circle(tela, PRETO, (x, y), raio)
        pygame.draw.circle(tela, CINZA, (x - raio // 3, y - raio // 3), max(2, raio // 4))
        pavio_fim = (x + raio // 2, y - raio - 6)
        pygame.draw.line(tela, MARROM, (x + raio // 3, y - raio // 2), pavio_fim, 3)
        pygame.draw.circle(tela, VERMELHO, pavio_fim, 4)
    elif peixe.efeito == "lixo":
        caixa = pygame.Rect(0, 0, tamanho, tamanho * 2 // 3)
        caixa.center = (x, y)
        pygame.draw.rect(tela, peixe.cor, caixa, border_radius=4)
        pygame.draw.rect(tela, PRETO, caixa, 2, border_radius=4)
    else:
        desenhar_peixe(tela, x, y, peixe.cor, tamanho)


def desenhar_pescador(tela, x, y, cor):
    """
    Desenha o pescador com os pés na posição (x, y) e devolve
    a posição da ponta da vara (onde a linha começa).
    """
    # pernas
    pygame.draw.rect(tela, (50, 60, 90), (x - 10, y - 30, 8, 30))
    pygame.draw.rect(tela, (50, 60, 90), (x + 2, y - 30, 8, 30))
    # tronco com a cor do personagem (é o que diferencia os pescadores)
    pygame.draw.rect(tela, cor, (x - 14, y - 62, 28, 34), border_radius=6)
    # cabeça e olho
    pygame.draw.circle(tela, PELE, (x, y - 74), 12)
    pygame.draw.circle(tela, PRETO, (x + 5, y - 76), 2)
    # chapéu
    pygame.draw.rect(tela, MARROM_ESCURO, (x - 17, y - 86, 34, 5))
    pygame.draw.rect(tela, MARROM_ESCURO, (x - 10, y - 98, 20, 13))
    # braço segurando a vara
    mao = (x + 22, y - 46)
    pygame.draw.line(tela, cor, (x + 8, y - 55), mao, 6)
    # vara
    ponta_vara = (x + 110, y - 140)
    pygame.draw.line(tela, MARROM, mao, ponta_vara, 4)
    return ponta_vara


def desenhar_funcionario(tela, x, y, cor, tempo, fase):
    """Funcionário: uma versão menor do pescador, com a boia balançando na água (usa seno)."""
    pygame.draw.rect(tela, (50, 60, 90), (x - 5, y - 18, 4, 18))
    pygame.draw.rect(tela, (50, 60, 90), (x + 1, y - 18, 4, 18))
    pygame.draw.rect(tela, cor, (x - 7, y - 36, 14, 19), border_radius=3)
    pygame.draw.circle(tela, PELE, (x, y - 43), 7)
    pygame.draw.rect(tela, MARROM_ESCURO, (x - 9, y - 49, 18, 3))
    pygame.draw.rect(tela, MARROM_ESCURO, (x - 5, y - 56, 10, 7))
    mao = (x - 6, y - 28)
    ponta = (x - 18, y - 64)
    pygame.draw.line(tela, MARROM, mao, ponta, 2)
    boia = (ponta[0], int(NIVEL_AGUA + 2 + math.sin(tempo * 2 + fase) * 2))
    pygame.draw.line(tela, BRANCO, ponta, boia, 1)
    pygame.draw.circle(tela, VERMELHO, boia, 3)


def desenhar_banca_de_vendas(tela):
    """Pequeno cais à direita, onde ficam os vendedores, com uma placa."""
    for pilar_x in (690, 770):
        pygame.draw.rect(tela, MARROM_ESCURO, (pilar_x, ALTURA_PIER, 12, 100))
    pygame.draw.rect(tela, MARROM, (672, ALTURA_PIER, 128, 14))
    pygame.draw.line(tela, MARROM_ESCURO, (672, ALTURA_PIER + 14), (800, ALTURA_PIER + 14), 2)
    pygame.draw.line(tela, MARROM_ESCURO, (684, ALTURA_PIER), (684, ALTURA_PIER - 92), 3)
    pygame.draw.line(tela, MARROM_ESCURO, (790, ALTURA_PIER), (790, ALTURA_PIER - 92), 3)
    placa = pygame.Rect(678, ALTURA_PIER - 108, 118, 22)
    pygame.draw.rect(tela, MARROM_ESCURO, placa, border_radius=4)
    pygame.draw.rect(tela, AMARELO, placa, 2, border_radius=4)


def desenhar_vendedor(tela, x, y, cor, tempo, fase):
    """Vendedor: boneco pequeno com boné, segurando uma caixa de peixes que balança de leve."""
    pygame.draw.rect(tela, (50, 60, 90), (x - 5, y - 18, 4, 18))
    pygame.draw.rect(tela, (50, 60, 90), (x + 1, y - 18, 4, 18))
    pygame.draw.rect(tela, cor, (x - 7, y - 36, 14, 19), border_radius=3)
    pygame.draw.circle(tela, PELE, (x, y - 43), 7)
    pygame.draw.rect(tela, VERMELHO, (x - 7, y - 50, 14, 4))           # boné
    pygame.draw.rect(tela, VERMELHO, (x, y - 47, 11, 2))               # aba do boné
    balanco = int(math.sin(tempo * 3 + fase) * 2)
    caixa = pygame.Rect(x + 5, y - 30 + balanco, 16, 11)
    pygame.draw.rect(tela, MARROM, caixa)
    pygame.draw.rect(tela, MARROM_ESCURO, caixa, 1)
    pygame.draw.ellipse(tela, (150, 170, 200), (caixa.x + 3, caixa.y - 3, 10, 5))   # peixinho na caixa


class Cenario:
    """
    Desenha e anima o fundo: céu, sol/lua, nuvens, água com ondas, sombras de peixes e pier.
    Também aplica o efeito do horário (tarde alaranjada, noite escura) e do clima (chuva, neblina).
    """

    def __init__(self):
        # O degradê do céu é desenhado UMA vez numa Surface e reaproveitado
        # em todos os quadros, porque desenhar 330 linhas a cada quadro é desperdício.
        self.fundo_ceu = pygame.Surface((LARGURA, NIVEL_AGUA + 10))
        for linha in range(NIVEL_AGUA + 10):
            proporcao = linha / NIVEL_AGUA
            cor = [int(CEU_TOPO[i] + (CEU_HORIZONTE[i] - CEU_TOPO[i]) * min(proporcao, 1)) for i in range(3)]
            pygame.draw.line(self.fundo_ceu, cor, (0, linha), (LARGURA, linha))

        # Cada nuvem é uma lista [x, y, velocidade]. Listas podem ser alteradas,
        # então conseguimos mover a nuvem mudando o x.
        self.nuvens = [[100, 70, 12], [420, 120, 8], [650, 50, 15]]

        # Sombras de peixes nadando, também [x, y, velocidade]
        self.sombras = [[random.randint(0, LARGURA), random.randint(NIVEL_AGUA + 60, ALTURA - 30),
                         random.choice([-1, 1]) * random.randint(20, 50)] for _ in range(4)]
        self.imagem_sombra = pygame.Surface((44, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(self.imagem_sombra, (10, 40, 80, 90), (0, 0, 44, 16))

        # Gotas de chuva [x, y] e estrelas (x, y, tamanho) para a noite.
        self.gotas = [[random.randint(0, LARGURA), random.randint(0, ALTURA)] for _ in range(80)]
        self.estrelas = [(random.randint(0, LARGURA), random.randint(0, NIVEL_AGUA - 60), random.randint(1, 2))
                         for _ in range(45)]
        # Película semitransparente que escurece/tinge a cena inteira.
        self.pelicula = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    def atualizar(self, dt, clima):
        # Move as nuvens; quando saem pela direita, voltam pela esquerda.
        for nuvem in self.nuvens:
            nuvem[0] += nuvem[2] * dt
            if nuvem[0] > LARGURA + 100:
                nuvem[0] = -100
        # Move as sombras; quando saem da tela, invertem a direção.
        for sombra in self.sombras:
            sombra[0] += sombra[2] * dt
            if sombra[0] < -50 or sombra[0] > LARGURA + 50:
                sombra[2] = -sombra[2]
        # Gotas caem rápido e voltam ao topo quando passam do fim da tela.
        if clima == "chuva":
            for gota in self.gotas:
                gota[1] += 520 * dt
                gota[0] -= 60 * dt
                if gota[1] > ALTURA:
                    gota[1] = -10
                    gota[0] = random.randint(0, LARGURA + 60)

    def desenhar(self, tela, tempo, local, horario, clima):
        cores = LOCAIS[local]
        # céu e sol (ou lua, à noite)
        tela.blit(self.fundo_ceu, (0, 0))
        if horario == "noite":
            pygame.draw.circle(tela, (235, 235, 245), (680, 110), 34)
            pygame.draw.circle(tela, (200, 200, 220), (668, 100), 7)
            pygame.draw.circle(tela, (200, 200, 220), (692, 122), 5)
        else:
            pygame.draw.circle(tela, (255, 240, 150), (680, 110), 48)
            pygame.draw.circle(tela, AMARELO, (680, 110), 40)
        # nuvens: 3 círculos brancos juntos formam uma nuvem
        for x, y, _ in self.nuvens:
            pygame.draw.circle(tela, BRANCO, (int(x), y), 22)
            pygame.draw.circle(tela, BRANCO, (int(x) + 25, y - 10), 28)
            pygame.draw.circle(tela, BRANCO, (int(x) + 52, y), 22)

        # Água: a borda de cima segue uma onda de seno que se move com o tempo.
        pontos = [(0, ALTURA)]
        for x in range(0, LARGURA + 20, 20):
            pontos.append((x, NIVEL_AGUA + math.sin(x * 0.03 + tempo * 2) * 4))
        pontos.append((LARGURA, ALTURA))
        pygame.draw.polygon(tela, cores["agua"], pontos)
        pygame.draw.rect(tela, cores["fundo"], (0, 480, LARGURA, ALTURA - 480))
        # linhas claras de brilho na água
        for profundidade in (25, 60, 110):
            y = NIVEL_AGUA + profundidade
            for x in range(0, LARGURA, 90):
                deslocamento = math.sin(tempo * 1.5 + x + profundidade) * 15
                pygame.draw.line(tela, (110, 180, 235), (x + deslocamento, y), (x + 35 + deslocamento, y), 2)
        # sombras de peixes
        for x, y, _ in self.sombras:
            tela.blit(self.imagem_sombra, (int(x), y))

        # pier: tábua de cima + pilares que entram na água
        for pilar_x in (20, 120, 230):
            pygame.draw.rect(tela, MARROM_ESCURO, (pilar_x, ALTURA_PIER, 14, 110))
        pygame.draw.rect(tela, MARROM, (0, ALTURA_PIER, 270, 14))
        pygame.draw.line(tela, MARROM_ESCURO, (0, ALTURA_PIER + 14), (270, ALTURA_PIER + 14), 2)

        self.aplicar_ambiente(tela, horario, clima)

    def aplicar_ambiente(self, tela, horario, clima):
        """Pinta uma película colorida por cima da cena e desenha as estrelas e a chuva."""
        if horario == "noite":
            self.pelicula.fill((10, 15, 60, 115))
        elif horario == "tarde":
            self.pelicula.fill((255, 140, 60, 38))
        else:
            self.pelicula.fill((0, 0, 0, 0))
        tela.blit(self.pelicula, (0, 0))
        if clima == "neblina":
            self.pelicula.fill((225, 230, 235, 95))
            tela.blit(self.pelicula, (0, 0))
        elif clima == "chuva":
            self.pelicula.fill((70, 80, 100, 70))
            tela.blit(self.pelicula, (0, 0))
            for x, y in self.gotas:
                pygame.draw.line(tela, (170, 200, 235), (x, y), (x - 4, y + 12), 1)
        if horario == "noite":
            for x, y, tamanho in self.estrelas:
                pygame.draw.circle(tela, (255, 255, 230), (x, y), tamanho)


# ===== CLASSE JOGO (MÁQUINA DE ESTADOS) =====
# Telas em que o "mundo" continua andando (relógio do dia, funcionários, encomendas...).
ESTADOS_COM_MUNDO = ("jogando", "loja", "mercado", "empresa", "colecao", "conquistas", "vitoria")


class Jogo:
    """
    Classe principal. Guarda todo o progresso e controla a MÁQUINA DE ESTADOS:
    a variável self.estado diz qual tela está ativa
    ("menu", "escolha_personagem", "jogando", "loja", "mercado", "empresa",
     "colecao", "conquistas", "vitoria").
    Dentro de "jogando" existe uma segunda máquina de estados, self.estado_pesca:
    ("esperando", "isca_na_agua", "fisgou", "resultado").
    """

    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        # O Clock controla o FPS e mede o tempo entre os quadros (dt).
        self.relogio = pygame.time.Clock()
        # Dicionário de fontes, para não criar fontes novas a cada quadro.
        self.fontes = {
            "titulo": pygame.font.Font(None, 72),
            "grande": pygame.font.Font(None, 44),
            "media": pygame.font.Font(None, 30),
            "pequena": pygame.font.Font(None, 22),
            "mini": pygame.font.Font(None, 18),
        }
        self.rodando = True
        self.estado = "menu"
        self.tempo_total = 0.0   # segundos desde que o jogo abriu (usado nas animações)
        self.cenario = Cenario()
        self.indice_escolhido = 0   # qual card está selecionado na escolha de personagem
        self.mensagem_tela = ""     # mensagem curta mostrada nas telas de loja/mercado/empresa
        self.tempo_mensagem = 0.0
        self.mercado_aba = "vender"  # aba aberta no mercado: "vender" ou "encomendas"
        self.encomenda_sel = 0      # fornecedor selecionado na aba de encomendas
        self.mercado_forn = 0       # fornecedor selecionado no mercado
        self.mercado_sel = 0        # linha selecionada na lista da mochila
        self.mercado_scroll = 0     # primeira linha visível da lista
        self.resetar_progresso()
        self.carregar()

        # Dois dicionários que ligam cada estado à sua função de teclas e de desenho.
        # Assim não precisamos de um if/elif enorme: basta procurar pelo nome do estado.
        self.funcoes_teclas = {
            "menu": self.teclas_menu,
            "escolha_personagem": self.teclas_escolha_personagem,
            "jogando": self.teclas_jogando,
            "loja": self.teclas_loja,
            "mercado": self.teclas_mercado,
            "empresa": self.teclas_empresa,
            "colecao": self.teclas_colecao,
            "conquistas": self.teclas_conquistas,
            "vitoria": self.teclas_vitoria,
        }
        self.funcoes_desenho = {
            "menu": self.desenhar_menu,
            "escolha_personagem": self.desenhar_escolha_personagem,
            "jogando": self.desenhar_jogando,
            "loja": self.desenhar_loja,
            "mercado": self.desenhar_mercado,
            "empresa": self.desenhar_empresa,
            "colecao": self.desenhar_colecao,
            "conquistas": self.desenhar_conquistas,
            "vitoria": self.desenhar_vitoria,
        }

    # ---------- progresso ----------
    def resetar_progresso(self):
        """Coloca todas as variáveis de progresso no valor inicial (jogo novo)."""
        self.personagem = None
        self.moedas = 0
        self.iscas = ISCAS_INICIAIS
        self.melhorias = {chave: 0 for chave in ORDEM_MELHORIAS}
        self.entregas = []              # pedidos da loja a caminho: [chave, segundos_restantes]
        self.colecao = criar_colecao_vazia()
        self.mochila = []               # lista de dicionários {"nome": ..., "idade": segundos}
        self.local = "rio"
        self.locais_liberados = ["rio"]
        self.funcionarios = []
        self.vendedores = []
        self.flutuantes = []            # textos que sobem e somem (ex.: "+12"): [texto, x, y, tempo]
        self.empresa_aba = "pesca"      # aba aberta na tela da empresa: "pesca" ou "vendas"
        self.reputacao = {f.nome: 0 for f in FORNECEDORES}
        self.estat = criar_estatisticas()
        self.conquistas_ganhas = []
        self.dia = 1
        self.tempo_dia = 0.0
        self.clima = "sol"
        self.venceu = False
        self.combo = 0
        self.vendas_dia = 0
        self.ultimo_relatorio = None
        self.avisos = []                # mensagens temporárias: [texto, tempo_restante, cor]
        self.reiniciar_mercado()
        self.reiniciar_pesca()

    def reiniciar_mercado(self):
        """Zera a demanda, os limites de venda e as encomendas dos fornecedores."""
        # demanda: fornecedor -> {nome do peixe -> fator de 0.3 a 1.0}. Sem registro = 1.0.
        self.demanda = {f.nome: {} for f in FORNECEDORES}
        self.vendidos_hoje = {f.nome: 0 for f in FORNECEDORES}
        self.encomendas = {f.nome: None for f in FORNECEDORES}
        self.espera_encomenda = {f.nome: random.uniform(10, 25) for f in FORNECEDORES}

    def reiniciar_pesca(self):
        """Volta a pescaria para o começo do ciclo."""
        self.estado_pesca = "esperando"
        self.tempo_ate_mordida = 0.0
        self.peixe_atual = None
        self.minigame = None
        self.resultado_tipo = "escapou"
        self.peixe_novo = False
        self.completou_agora = False
        self.bonus_combo = 0
        self.extra_rede = False
        self.custo_quebra = 0
        self.tempo_resultado = 0.0

    def dados_para_salvar(self):
        """Monta um dicionário só com tipos simples (números, textos, listas), que o JSON entende."""
        indice = PERSONAGENS.index(self.personagem) if self.personagem else None
        return {
            "moedas": self.moedas,
            "iscas": self.iscas,
            "melhorias": self.melhorias,
            "entregas": self.entregas,
            "colecao": self.colecao,
            "mochila": self.mochila,
            "personagem": indice,
            "local": self.local,
            "locais": self.locais_liberados,
            "funcionarios": [{"tipo": f.indice_tipo, "nome": f.nome} for f in self.funcionarios],
            "vendedores": [{"tipo": v.indice_tipo, "nome": v.nome} for v in self.vendedores],
            "reputacao": self.reputacao,
            "estatisticas": self.estat,
            "conquistas": self.conquistas_ganhas,
            "dia": self.dia,
            "venceu": self.venceu,
        }

    def salvar(self):
        salvar_jogo(self.dados_para_salvar())

    def carregar(self):
        """Lê o save (se existir) e copia os valores para o jogo."""
        dados = carregar_jogo()
        if dados is None:
            return
        # .get(chave, padrão) evita erro se alguma informação faltar no arquivo
        # (por exemplo, um save de uma versão antiga do jogo).
        self.moedas = dados.get("moedas", 0)
        self.iscas = dados.get("iscas", ISCAS_INICIAIS)
        melhorias_salvas = dados.get("melhorias", {})
        for chave in ORDEM_MELHORIAS:
            self.melhorias[chave] = melhorias_salvas.get(chave, 0)
        # Só copiamos peixes que existem no jogo, ignorando nomes desconhecidos.
        for nome, quantidade in dados.get("colecao", {}).items():
            if nome in self.colecao:
                self.colecao[nome] = quantidade
        self.mochila = [item for item in dados.get("mochila", [])
                        if isinstance(item, dict) and item.get("nome") in PEIXE_POR_NOME]
        self.entregas = [list(e) for e in dados.get("entregas", [])
                         if len(e) == 2 and e[0] in MELHORIAS]
        liberados = [local for local in dados.get("locais", []) if local in LOCAIS]
        if "rio" not in liberados:
            liberados.insert(0, "rio")
        self.locais_liberados = liberados
        local_salvo = dados.get("local", "rio")
        self.local = local_salvo if local_salvo in self.locais_liberados else "rio"
        for item in dados.get("funcionarios", []):
            if isinstance(item, dict) and 0 <= item.get("tipo", -1) < len(TIPOS_FUNCIONARIO):
                if len(self.funcionarios) < MAX_FUNCIONARIOS:
                    self.funcionarios.append(Funcionario(item["tipo"], item.get("nome")))
        for item in dados.get("vendedores", []):
            if isinstance(item, dict) and 0 <= item.get("tipo", -1) < len(TIPOS_VENDEDOR):
                if len(self.vendedores) < MAX_VENDEDORES:
                    self.vendedores.append(Vendedor(item["tipo"], item.get("nome")))
        for nome in self.reputacao:
            self.reputacao[nome] = dados.get("reputacao", {}).get(nome, 0)
        for chave in self.estat:
            self.estat[chave] = dados.get("estatisticas", {}).get(chave, 0)
        ids_validos = [c["id"] for c in CONQUISTAS]
        self.conquistas_ganhas = [c for c in dados.get("conquistas", []) if c in ids_validos]
        self.dia = dados.get("dia", 1)
        self.venceu = dados.get("venceu", False)
        indice = dados.get("personagem")
        if isinstance(indice, int) and 0 <= indice < len(PERSONAGENS):
            self.personagem = PERSONAGENS[indice]

    # ---------- avisos e mensagens ----------
    def avisar(self, texto, cor=BRANCO):
        """Mensagem temporária que aparece no canto da tela de pesca (some depois de 6 segundos)."""
        self.avisos.append([texto, 6.0, cor])
        if len(self.avisos) > 5:
            self.avisos.pop(0)   # tira o aviso mais antigo

    def msg(self, texto):
        """Mensagem curta mostrada embaixo das telas de loja, mercado e empresa (some em 2 segundos)."""
        self.mensagem_tela = texto
        self.tempo_mensagem = 2.0

    # ---------- atributos combinados (personagem + melhorias + ambiente) ----------
    def horario(self):
        return horario_atual(self.tempo_dia / TEMPO_DIA)

    def sorte_total(self):
        return (self.personagem.sorte
                + self.melhorias["amuleto"] * SORTE_POR_NIVEL
                + HORARIOS[self.horario()]["sorte"]
                + CLIMAS[self.clima]["sorte"])

    def bonus_zona_total(self):
        return (self.personagem.bonus_zona
                + self.melhorias["vara"] * BONUS_ZONA_POR_NIVEL
                + CLIMAS[self.clima]["zona"])

    def multiplicador_espera_total(self):
        return (self.personagem.multiplicador_espera
                * (1 - self.melhorias["carretilha"] * REDUCAO_ESPERA_POR_NIVEL)
                * HORARIOS[self.horario()]["espera"]
                * CLIMAS[self.clima]["espera"])

    def capacidade_mochila(self):
        return CAPACIDADE_BASE_MOCHILA + self.melhorias["mochila"] * CAPACIDADE_POR_NIVEL

    def tempo_estragar(self):
        return TEMPO_FRESCOR_BASE * (1 + self.melhorias["geladeira"] * BONUS_FRESCOR_POR_NIVEL)

    def chance_quebra(self, raridade):
        """Chance de a linha quebrar ao errar um peixe dessa raridade (0 para peixes comuns)."""
        return CHANCE_QUEBRA.get(raridade, 0) * (1 - self.melhorias["linha"] * REDUCAO_QUEBRA_POR_NIVEL)

    def nivel_rep(self, fornecedor):
        return nivel_reputacao(self.reputacao[fornecedor.nome])

    def limite_dia(self, fornecedor):
        """Quantos peixes o fornecedor compra por dia: base + Contratos + 1 por nível de reputação."""
        return (fornecedor.limite_dia
                + self.melhorias["contratos"] * BONUS_LIMITE_POR_NIVEL
                + self.nivel_rep(fornecedor))

    def contar_para_pedido(self, fornecedor, nome_peixe):
        """Quantos peixes desse tipo, frescos o bastante para o fornecedor, existem na mochila."""
        return sum(1 for item in self.mochila
                   if item["nome"] == nome_peixe and self.frescor_item(item) >= fornecedor.frescor_minimo)

    def frescor_item(self, item):
        return frescor_do_peixe(item["idade"], self.tempo_estragar())

    def especies_possiveis(self):
        """Peixes que podem ser pedidos em encomendas: dos locais liberados, sem lixo nem míticos."""
        return [p for p in PEIXES_COLECAO
                if p.raridade != "mítico" and any(local in self.locais_liberados for local in p.locais)]

    # ---------- o MUNDO (continua andando em quase todas as telas) ----------
    def atualizar_mundo(self, dt):
        """Relógio do dia, frescor dos peixes, entregas, demanda, encomendas e funcionários."""
        self.tempo_dia += dt
        if self.tempo_dia >= TEMPO_DIA:
            self.tempo_dia -= TEMPO_DIA
            self.fim_do_dia()
        for item in self.mochila:
            item["idade"] += dt
        self.atualizar_entregas(dt)
        self.atualizar_demanda(dt)
        self.atualizar_encomendas(dt)
        for funcionario in self.funcionarios:
            if funcionario.atualizar(dt):
                self.funcionario_pescar(funcionario)
        for vendedor in self.vendedores:
            if vendedor.atualizar(dt):
                self.vendedor_trabalhar(vendedor)
        # textos flutuantes sobem e vão sumindo
        for texto in self.flutuantes:
            texto[2] -= 25 * dt
            texto[3] -= dt
        self.flutuantes = [texto for texto in self.flutuantes if texto[3] > 0]
        for aviso in self.avisos:
            aviso[1] -= dt
        # list comprehension: mantém só os avisos que ainda têm tempo
        self.avisos = [aviso for aviso in self.avisos if aviso[1] > 0]
        self.verificar_conquistas()

    def fim_do_dia(self):
        """Paga os salários, zera os limites de venda, sorteia o clima e fecha o relatório do dia."""
        pagos = 0
        demitidos = []
        # Pescadores e vendedores recebem salário do mesmo jeito: percorremos as duas listas.
        # [:] faz uma cópia da lista, porque vamos remover itens enquanto percorremos.
        for lista in (self.funcionarios, self.vendedores):
            for pessoa in lista[:]:
                salario = pessoa.tipo["salario"]
                if self.moedas >= salario:
                    self.moedas -= salario
                    pagos += salario
                else:
                    lista.remove(pessoa)
                    demitidos.append(pessoa.nome)
        self.ultimo_relatorio = {"dia": self.dia, "vendas": self.vendas_dia,
                                 "salarios": pagos, "lucro": self.vendas_dia - pagos}
        self.avisar(f"Fim do dia {self.dia}: lucro {self.vendas_dia - pagos} moedas", AMARELO)
        for nome in demitidos:
            self.avisar(f"{nome} pediu demissão (sem salário)!", VERMELHO)
        self.vendas_dia = 0
        self.vendidos_hoje = {f.nome: 0 for f in FORNECEDORES}
        self.estat["dias"] += 1
        self.dia += 1
        self.clima = sortear_clima()
        self.salvar()   # salva automaticamente a cada dia

    def atualizar_entregas(self, dt):
        """Pedidos feitos na loja demoram para chegar. Quando o tempo acaba, a melhoria sobe de nível."""
        for entrega in self.entregas[:]:
            entrega[1] -= dt
            if entrega[1] <= 0:
                self.entregas.remove(entrega)
                self.melhorias[entrega[0]] += 1
                self.avisar(f"Chegou: {MELHORIAS[entrega[0]]['nome']}!", VERDE)

    def atualizar_demanda(self, dt):
        """O preço de cada peixe se recupera aos poucos depois de cair por causa das vendas."""
        for tabela in self.demanda.values():
            for nome in tabela:
                tabela[nome] = min(1.0, tabela[nome] + RECUPERACAO_DEMANDA * dt)

    def atualizar_encomendas(self, dt):
        for fornecedor in FORNECEDORES:
            nome = fornecedor.nome
            encomenda = self.encomendas[nome]
            if encomenda is None:
                # Sem pedido: um cronômetro conta até o fornecedor fazer um novo.
                self.espera_encomenda[nome] -= dt
                if self.espera_encomenda[nome] <= 0:
                    self.encomendas[nome] = gerar_encomenda(fornecedor, self.especies_possiveis())
                    self.avisar(f"Nova encomenda: {nome} (tecla O)", AZUL_CLARO)
            else:
                encomenda["tempo"] -= dt
                if encomenda["tempo"] <= 0:
                    # Prazo estourou: perde 1 ponto de reputação.
                    self.encomendas[nome] = None
                    self.reputacao[nome] = max(0, self.reputacao[nome] - 1)
                    self.espera_encomenda[nome] = random.uniform(20, 40)
                    self.avisar(f"Encomenda expirou: {nome}", VERMELHO)

    def funcionario_pescar(self, funcionario):
        """O funcionário tenta pescar. Pode errar, e não pesca se a mochila estiver cheia."""
        if random.random() > funcionario.tipo["acerto"]:
            return
        if len(self.mochila) >= self.capacidade_mochila():
            return
        peixe = sortear_peixe(funcionario.tipo["sorte"], random.choice(self.locais_liberados))
        if peixe.efeito is not None:
            return   # funcionários ignoram lixo e bombas
        self.mochila.append({"nome": peixe.nome, "idade": 0.0})
        self.registrar_captura(peixe)
        self.avisar(f"{funcionario.nome} pescou {peixe.nome}", CINZA_CLARO)

    def verificar_conquistas(self):
        for conquista in CONQUISTAS:
            if conquista["id"] not in self.conquistas_ganhas and conquista["condicao"](self):
                self.conquistas_ganhas.append(conquista["id"])
                self.avisar(f"Conquista: {conquista['nome']}!", AMARELO)

    def registrar_captura(self, peixe):
        """Anota na coleção e nas estatísticas. Devolve True se o peixe era novo."""
        novo = self.colecao[peixe.nome] == 0
        self.colecao[peixe.nome] += 1
        self.estat["pescados"] += 1
        if peixe.raridade == "lendário":
            self.estat["lendarios"] += 1
        elif peixe.raridade == "mítico":
            self.estat["miticos"] += 1
        return novo

    # ---------- mercado: vender peixes ----------
    def demanda_atual(self, fornecedor, nome_peixe):
        return self.demanda[fornecedor.nome].get(nome_peixe, 1.0)

    def preco_para(self, fornecedor, item):
        """Preço que o fornecedor paga por este item da mochila agora (0 = não compra)."""
        peixe = PEIXE_POR_NOME[item["nome"]]
        return preco_venda(fornecedor, peixe, self.frescor_item(item),
                           self.nivel_rep(fornecedor), self.demanda_atual(fornecedor, peixe.nome))

    def proximo_item_venda(self, fornecedor, nome_peixe):
        """
        Qual peixe da mochila será vendido: o MAIS VELHO que o fornecedor aceita,
        para guardar os mais frescos (que valem mais para o restaurante).
        """
        candidatos = [item for item in self.mochila
                      if item["nome"] == nome_peixe and self.preco_para(fornecedor, item) > 0]
        if not candidatos:
            return None
        return max(candidatos, key=lambda item: item["idade"])

    def tentar_venda(self, fornecedor, nome_peixe, comissao=0.0):
        """
        Vende um peixe se possível. Devolve as moedas recebidas, ou 0 se não vendeu.
        Se um vendedor fez a venda, ele fica com a comissão (ex.: 0.20 = 20% do preço).
        """
        if self.vendidos_hoje[fornecedor.nome] >= self.limite_dia(fornecedor):
            return 0
        item = self.proximo_item_venda(fornecedor, nome_peixe)
        if item is None:
            return 0
        preco = self.preco_para(fornecedor, item)
        ganho = max(1, round(preco * (1 - comissao)))
        self.mochila.remove(item)
        self.moedas += ganho
        self.vendas_dia += ganho
        preco = ganho
        self.vendidos_hoje[fornecedor.nome] += 1
        self.estat["vendas"] += 1
        # Cada venda derruba o preço desse peixe nesse fornecedor em 8% (até no mínimo 30%).
        tabela = self.demanda[fornecedor.nome]
        tabela[nome_peixe] = max(DEMANDA_MINIMA, tabela.get(nome_peixe, 1.0) * QUEDA_DEMANDA)
        return preco

    def vender_um(self, fornecedor, nome_peixe):
        preco = self.tentar_venda(fornecedor, nome_peixe)
        if preco > 0:
            self.msg(f"Vendeu {nome_peixe} por {preco} moedas")
        elif self.vendidos_hoje[fornecedor.nome] >= self.limite_dia(fornecedor):
            self.msg(f"{fornecedor.nome} não compra mais hoje! (melhore os Contratos)")
        else:
            self.msg("Ele não compra esse peixe (ou está pouco fresco).")

    def vender_tudo(self, fornecedor):
        """
        Vende tudo que o fornecedor aceita, até o limite do dia. Começamos pelos peixes
        que ele paga MAIS, para o limite diário ser usado nos melhores negócios.
        """
        nomes = {item["nome"] for item in self.mochila}   # set: nomes sem repetição

        def melhor_preco(nome):
            item = self.proximo_item_venda(fornecedor, nome)
            return self.preco_para(fornecedor, item) if item else 0

        ordenados = sorted(nomes, key=melhor_preco, reverse=True)
        total, quantidade = 0, 0
        for nome in ordenados:
            while True:
                preco = self.tentar_venda(fornecedor, nome)
                if preco == 0:
                    break
                total += preco
                quantidade += 1
        if quantidade > 0:
            self.msg(f"Vendeu {quantidade} peixes por {total} moedas")
        else:
            self.msg("Nada para vender a este fornecedor agora.")

    def grupos_mochila(self):
        """Agrupa a mochila por espécie: lista de dicionários {nome, qtd, frescor médio}."""
        grupos = {}
        for item in self.mochila:
            grupo = grupos.setdefault(item["nome"], {"nome": item["nome"], "qtd": 0, "soma": 0.0})
            grupo["qtd"] += 1
            grupo["soma"] += self.frescor_item(item)
        lista = [{"nome": g["nome"], "qtd": g["qtd"], "frescor": g["soma"] / g["qtd"]} for g in grupos.values()]
        # Ordena por raridade e depois por nome.
        lista.sort(key=lambda g: (ORDEM_RARIDADES.index(PEIXE_POR_NOME[g["nome"]].raridade), g["nome"]))
        return lista

    def reunir_encomenda(self, fornecedor):
        """
        Procura na mochila os peixes de uma encomenda. Devolve a lista de itens
        escolhidos, ou None se não há encomenda ou se falta algum peixe.
        """
        encomenda = self.encomendas[fornecedor.nome]
        if encomenda is None:
            return None
        escolhidos = []
        for nome, quantidade in encomenda["pedidos"].items():
            disponiveis = [item for item in self.mochila
                           if item["nome"] == nome and self.frescor_item(item) >= fornecedor.frescor_minimo]
            if len(disponiveis) < quantidade:
                return None
            escolhidos.extend(disponiveis[:quantidade])
        return escolhidos

    def concluir_encomenda(self, fornecedor, escolhidos):
        """Tira os peixes da mochila e paga a recompensa. Devolve o valor recebido."""
        encomenda = self.encomendas[fornecedor.nome]
        # Remove da mochila os peixes entregues (comparando pela identidade do objeto).
        ids = {id(item) for item in escolhidos}
        self.mochila = [item for item in self.mochila if id(item) not in ids]
        self.moedas += encomenda["recompensa"]
        self.vendas_dia += encomenda["recompensa"]
        self.reputacao[fornecedor.nome] += 1
        self.estat["encomendas"] += 1
        self.encomendas[fornecedor.nome] = None
        self.espera_encomenda[fornecedor.nome] = random.uniform(15, 30)
        return encomenda["recompensa"]

    def entregar_encomenda(self, fornecedor):
        """Confere se a mochila tem tudo que foi pedido; se tiver, paga a recompensa e sobe a reputação."""
        if self.encomendas[fornecedor.nome] is None:
            self.msg("Este fornecedor não tem encomenda agora.")
            return
        escolhidos = self.reunir_encomenda(fornecedor)
        if escolhidos is None:
            self.msg("Faltam peixes (ou estão pouco frescos) para esta encomenda.")
            return
        recompensa = self.concluir_encomenda(fornecedor, escolhidos)
        self.msg(f"Encomenda entregue! +{recompensa} moedas e +1 reputação")

    # ---------- vendedores (vendem sozinhos) ----------
    def especies_reservadas(self):
        """Nomes dos peixes pedidos em encomendas ativas: os vendedores não podem vendê-los."""
        reservadas = set()
        for encomenda in self.encomendas.values():
            if encomenda is not None:
                reservadas.update(encomenda["pedidos"].keys())
        return reservadas

    def vendedor_trabalhar(self, vendedor):
        """
        Uma rodada de trabalho do vendedor:
          1) se for Gerente, tenta entregar alguma encomenda pronta;
          2) senão, procura o MELHOR negócio (fornecedor + peixe com maior preço) e vende um peixe,
             pagando a comissão.
        """
        tipo = vendedor.tipo
        x_vendedor = 706 + self.vendedores.index(vendedor) * 34
        if tipo["entrega"]:
            for fornecedor in FORNECEDORES:
                escolhidos = self.reunir_encomenda(fornecedor)
                if escolhidos is not None:
                    recompensa = self.concluir_encomenda(fornecedor, escolhidos)
                    self.flutuantes.append([f"+{recompensa}", x_vendedor, ALTURA_PIER - 80, 2.0])
                    self.avisar(f"{vendedor.nome} entregou a encomenda: {fornecedor.nome}", VERDE)
                    return
        reservadas = self.especies_reservadas()
        melhor = None   # (preço, fornecedor, nome do peixe)
        nomes = {item["nome"] for item in self.mochila}
        for fornecedor in FORNECEDORES:
            if self.vendidos_hoje[fornecedor.nome] >= self.limite_dia(fornecedor):
                continue
            for nome in nomes:
                if nome in reservadas or PEIXE_POR_NOME[nome].raridade not in tipo["raridades"]:
                    continue
                item = self.proximo_item_venda(fornecedor, nome)
                if item is None:
                    continue
                preco = self.preco_para(fornecedor, item)
                if melhor is None or preco > melhor[0]:
                    melhor = (preco, fornecedor, nome)
        if melhor is not None:
            ganho = self.tentar_venda(melhor[1], melhor[2], tipo["comissao"])
            self.flutuantes.append([f"+{ganho}", x_vendedor, ALTURA_PIER - 80, 1.5])

    # ===== SELEÇÃO DO PERSONAGEM =====
    def teclas_escolha_personagem(self, tecla):
        # Setas mudam o card selecionado. O "%" faz a seleção dar a volta (do último para o primeiro).
        if tecla == pygame.K_LEFT:
            self.indice_escolhido = (self.indice_escolhido - 1) % len(PERSONAGENS)
        elif tecla == pygame.K_RIGHT:
            self.indice_escolhido = (self.indice_escolhido + 1) % len(PERSONAGENS)
        elif tecla in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.indice_escolhido = tecla - pygame.K_1
        elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.personagem = PERSONAGENS[self.indice_escolhido]
            self.reiniciar_pesca()
            self.estado = "jogando"
        elif tecla == pygame.K_ESCAPE:
            self.estado = "menu"

    def desenhar_escolha_personagem(self):
        desenhar_painel(self.tela, pygame.Rect(30, 40, 740, 520))
        desenhar_texto(self.tela, "Escolha seu pescador", self.fontes["grande"], BRANCO, LARGURA // 2, 85, True)
        for indice, personagem in enumerate(PERSONAGENS):
            card = pygame.Rect(60 + indice * 235, 130, 210, 330)
            selecionado = indice == self.indice_escolhido
            # O card selecionado ganha borda amarela e fica um pouco mais alto.
            if selecionado:
                card.y -= 10
            pygame.draw.rect(self.tela, COR_CARD, card, border_radius=10)
            pygame.draw.rect(self.tela, AMARELO if selecionado else CINZA, card, 4 if selecionado else 2, border_radius=10)
            desenhar_pescador(self.tela, card.centerx - 30, card.y + 220, personagem.cor)
            desenhar_texto(self.tela, f"{indice + 1}. {personagem.nome}", self.fontes["media"], BRANCO,
                           card.centerx, card.y + 245, True)
            # A descrição é dividida em duas linhas no ":" para caber no card.
            partes = personagem.descricao.split(": ")
            desenhar_texto(self.tela, partes[0], self.fontes["pequena"], AMARELO, card.centerx, card.y + 275, True)
            desenhar_texto(self.tela, partes[1], self.fontes["pequena"], CINZA_CLARO, card.centerx, card.y + 298, True)
        desenhar_texto(self.tela, "SETAS ou 1-3 para escolher   ENTER confirmar   ESC voltar",
                       self.fontes["pequena"], CINZA_CLARO, LARGURA // 2, 520, True)

    # ---------- MENU ----------
    def teclas_menu(self, tecla):
        if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
            # Se já existe personagem salvo, continua direto; senão vai escolher um.
            self.estado = "jogando" if self.personagem else "escolha_personagem"
            self.reiniciar_pesca()
        elif tecla == pygame.K_n:
            self.resetar_progresso()
            self.estado = "escolha_personagem"
        elif tecla == pygame.K_ESCAPE:
            self.rodando = False

    def desenhar_menu(self):
        desenhar_pescador(self.tela, POSICAO_PESCADOR, ALTURA_PIER, PERSONAGENS[0].cor)
        desenhar_painel(self.tela, pygame.Rect(150, 80, 500, 300), AMARELO)
        desenhar_texto(self.tela, "Pescaria Tranquila", self.fontes["titulo"], AMARELO, LARGURA // 2, 135, True)
        desenhar_texto(self.tela, "TYCOON", self.fontes["grande"], BRANCO, LARGURA // 2, 180, True)
        texto_jogar = "ENTER - Continuar" if self.personagem else "ENTER - Jogar"
        desenhar_texto(self.tela, texto_jogar, self.fontes["media"], BRANCO, LARGURA // 2, 245, True)
        desenhar_texto(self.tela, "N - Novo jogo (apaga o progresso)", self.fontes["media"], BRANCO, LARGURA // 2, 285, True)
        desenhar_texto(self.tela, "ESC - Sair", self.fontes["media"], BRANCO, LARGURA // 2, 325, True)
        desenhar_texto(self.tela, f"Meta: juntar {CUSTO_BARCO} moedas e comprar o Barco!", self.fontes["pequena"],
                       CINZA_CLARO, LARGURA // 2, 360, True)

    # ---------- CICLO DA PESCARIA ----------
    def lancar_linha(self):
        """
        Estado esperando -> isca_na_agua. Gasta uma isca, sorteia QUAL peixe vem
        (o sonar mostra isso) e quanto tempo ele vai demorar para morder.
        """
        if len(self.mochila) >= self.capacidade_mochila():
            self.avisar("Mochila cheia! Venda no Mercado (M)", VERMELHO)
            return
        if self.iscas <= 0:
            # Proteção contra ficar travado: sem iscas, sem dinheiro e sem peixes, um vizinho ajuda.
            if self.moedas < PRECO_PACOTE_ISCAS and not self.mochila:
                self.iscas = 3
                self.avisar("Um vizinho te deu 3 iscas!", VERDE)
            else:
                self.avisar("Sem iscas! Compre na Loja (L)", VERMELHO)
                return
        self.iscas -= 1
        self.peixe_atual = sortear_peixe(self.sorte_total(), self.local)
        self.tempo_ate_mordida = sortear_tempo_mordida(self.multiplicador_espera_total())
        self.estado_pesca = "isca_na_agua"

    def recolher_linha(self):
        """Tirar a linha antes da mordida perde a isca, a não ser que o Sonar esteja no nível 3."""
        if self.melhorias["sonar"] >= 3:
            self.iscas += 1
        self.reiniciar_pesca()

    def fisgar(self):
        """Estado isca_na_agua -> fisgou. Cria o minigame com a dificuldade do peixe sorteado."""
        self.minigame = MinigameCaptura(self.peixe_atual, self.bonus_zona_total())
        self.estado_pesca = "fisgou"

    def finalizar_captura(self, sucesso):
        """
        Estado fisgou -> resultado. Aplica as consequências:
          peixe normal  -> vai para a mochila, combo sobe, pode vir um peixe extra (rede)
          lixo          -> vale poucas moedas na hora
          bomba         -> custa moedas (se o jogador acertar!)
          erro          -> o peixe escapa, o combo zera e a linha pode quebrar
        """
        peixe = self.peixe_atual
        self.resultado_tipo = "escapou"
        self.peixe_novo = False
        self.completou_agora = False
        self.bonus_combo = 0
        self.extra_rede = False
        self.custo_quebra = 0
        if sucesso:
            if peixe.efeito == "lixo":
                self.resultado_tipo = "lixo"
                self.moedas += peixe.valor
            elif peixe.efeito == "bomba":
                self.resultado_tipo = "bomba"
                self.moedas = max(0, self.moedas - DANO_BOMBA)
                self.combo = 0
                self.estat["bombas"] += 1
            else:
                self.resultado_tipo = "pescou"
                estava_completa = colecao_completa(self.colecao)
                self.peixe_novo = self.registrar_captura(peixe)
                self.mochila.append({"nome": peixe.nome, "idade": 0.0})
                self.combo += 1
                self.estat["maior_combo"] = max(self.estat["maior_combo"], self.combo)
                # Combo: a partir do 2º acerto seguido ganha 10% do valor por acerto (máximo 50%).
                if self.combo >= 2:
                    self.bonus_combo = max(1, int(peixe.valor * 0.1 * min(self.combo - 1, 5)))
                    self.moedas += self.bonus_combo
                # Rede: chance de pegar mais um peixe igual, se ainda couber na mochila.
                if (len(self.mochila) < self.capacidade_mochila()
                        and random.random() < self.melhorias["rede"] * CHANCE_REDE_POR_NIVEL):
                    self.mochila.append({"nome": peixe.nome, "idade": 0.0})
                    self.registrar_captura(peixe)
                    self.extra_rede = True
                self.completou_agora = not estava_completa and colecao_completa(self.colecao)
        elif peixe.efeito is None:
            # Errar um peixe de verdade zera o combo (lixo e bomba não contam).
            self.combo = 0
            self.estat["fugas"] += 1
            if random.random() < self.chance_quebra(peixe.raridade):
                self.resultado_tipo = "quebrou"
                self.custo_quebra = min(CUSTO_QUEBRA[peixe.raridade], self.moedas)
                self.moedas -= self.custo_quebra
                self.estat["linhas_quebradas"] += 1
        self.estado_pesca = "resultado"
        self.tempo_resultado = TEMPO_TELA_RESULTADO

    def teclas_jogando(self, tecla):
        # Cada sub-estado da pesca reage ao teclado de um jeito diferente.
        if self.estado_pesca == "esperando":
            if tecla == pygame.K_SPACE:
                self.lancar_linha()
            # As outras telas só abrem com a linha recolhida,
            # para não deixar um peixe "congelado" no meio da captura.
            elif tecla == pygame.K_l:
                self.mensagem_tela = ""
                self.estado = "loja"
            elif tecla in (pygame.K_m, pygame.K_o):
                # M abre o mercado na aba de vender; O abre direto na aba de encomendas.
                self.mensagem_tela = ""
                self.mercado_aba = "vender" if tecla == pygame.K_m else "encomendas"
                self.estado = "mercado"
            elif tecla == pygame.K_e:
                self.mensagem_tela = ""
                self.estado = "empresa"
            elif tecla == pygame.K_c:
                self.estado = "colecao"
            elif tecla == pygame.K_q:
                self.estado = "conquistas"
            elif tecla == pygame.K_t:
                self.trocar_local()
            elif tecla == pygame.K_ESCAPE:
                self.estado = "menu"
        elif self.estado_pesca == "isca_na_agua":
            # Apertar ESPAÇO antes da mordida recolhe a linha.
            if tecla == pygame.K_SPACE:
                self.recolher_linha()
        elif self.estado_pesca == "fisgou":
            if tecla == pygame.K_SPACE:
                resposta = self.minigame.apertar()
                if resposta == "capturou":
                    self.finalizar_captura(True)
                elif resposta == "falhou":
                    self.finalizar_captura(False)
                # "continua": o peixe mítico exige mais um acerto, o minigame segue.
        elif self.estado_pesca == "resultado":
            # Pequena espera de 0.5s para o mesmo toque do minigame não pular o resultado.
            if tecla == pygame.K_SPACE and self.tempo_resultado < TEMPO_TELA_RESULTADO - 0.5:
                self.reiniciar_pesca()

    def trocar_local(self):
        """Passa para o próximo local liberado (o % faz a lista dar a volta)."""
        if len(self.locais_liberados) < 2:
            self.avisar("Compre licenças na Empresa (E) para pescar em outros locais", CINZA_CLARO)
            return
        indice = self.locais_liberados.index(self.local)
        self.local = self.locais_liberados[(indice + 1) % len(self.locais_liberados)]
        self.avisar(f"Agora pescando no {LOCAIS[self.local]['nome']}", AZUL_CLARO)

    def atualizar_pesca(self, dt):
        """Chamado todo quadro. Usa contadores de tempo em vez de sleep, para o jogo nunca travar."""
        if self.estado_pesca == "isca_na_agua":
            self.tempo_ate_mordida -= dt
            if self.tempo_ate_mordida <= 0:
                self.fisgar()
        elif self.estado_pesca == "fisgou":
            self.minigame.atualizar(dt)
            if self.minigame.acabou_tempo():
                self.finalizar_captura(False)  # demorou demais, o peixe escapou
        elif self.estado_pesca == "resultado":
            self.tempo_resultado -= dt
            if self.tempo_resultado <= 0:
                self.reiniciar_pesca()

    def desenhar_jogando(self):
        # Os funcionários ficam em fila no pier, à esquerda do pescador.
        for posicao, funcionario in enumerate(self.funcionarios):
            desenhar_funcionario(self.tela, 30 + posicao * 28, ALTURA_PIER,
                                 funcionario.tipo["cor"], self.tempo_total, funcionario.fase)
        # Vendedores ficam na banca de vendas, à direita, com a placa "VENDAS".
        if self.vendedores:
            desenhar_banca_de_vendas(self.tela)
            desenhar_texto(self.tela, "VENDAS", self.fontes["mini"], BRANCO, 737, ALTURA_PIER - 97, True)
            for posicao, vendedor in enumerate(self.vendedores):
                desenhar_vendedor(self.tela, 706 + posicao * 34, ALTURA_PIER,
                                  vendedor.tipo["cor"], self.tempo_total, vendedor.fase)
        ponta_vara = desenhar_pescador(self.tela, POSICAO_PESCADOR, ALTURA_PIER, self.personagem.cor)
        self.desenhar_linha_e_boia(ponta_vara)
        for texto, x, y, _ in self.flutuantes:
            desenhar_texto_sombra(self.tela, texto, self.fontes["pequena"], AMARELO, int(x), int(y), True)
        self.desenhar_hud()
        self.desenhar_avisos()
        if self.estado_pesca == "fisgou":
            self.desenhar_minigame()
        elif self.estado_pesca == "resultado":
            self.desenhar_resultado()

    def desenhar_linha_e_boia(self, ponta_vara):
        t = self.tempo_total
        if self.estado_pesca in ("esperando", "resultado"):
            # Linha recolhida: fica pendurada na ponta da vara.
            fim = (ponta_vara[0], ponta_vara[1] + 60)
            pygame.draw.line(self.tela, BRANCO, ponta_vara, fim, 1)
            if self.estado_pesca == "resultado" and self.resultado_tipo == "pescou":
                desenhar_peixe(self.tela, fim[0], fim[1] + 15, self.peixe_atual.cor, 16)
            else:
                pygame.draw.circle(self.tela, CINZA_CLARO, fim, 3)
            return
        if self.estado_pesca == "isca_na_agua":
            # Boia flutuando devagar: o seno faz ela subir e descer suavemente.
            boia = (POSICAO_BOIA, int(NIVEL_AGUA - 4 + math.sin(t * 3) * 3))
            self.desenhar_sonar()
        else:
            # Fisgou: a boia afunda e treme rápido para mostrar que o peixe mordeu.
            boia = (POSICAO_BOIA + int(math.sin(t * 40) * 3), NIVEL_AGUA + 6)
            pygame.draw.circle(self.tela, BRANCO, (POSICAO_BOIA, NIVEL_AGUA), 14 + int(t * 20) % 12, 2)
            desenhar_texto_sombra(self.tela, "!", self.fontes["titulo"], VERMELHO, POSICAO_BOIA, NIVEL_AGUA - 50, True)
        pygame.draw.line(self.tela, BRANCO, ponta_vara, boia, 1)
        pygame.draw.circle(self.tela, VERMELHO, boia, 8)
        pygame.draw.circle(self.tela, BRANCO, (boia[0], boia[1] - 4), 4)

    def desenhar_sonar(self):
        """Com o Sonar, o jogo revela o peixe sorteado enquanto a isca está na água."""
        nivel = self.melhorias["sonar"]
        if nivel == 0:
            return
        peixe = self.peixe_atual
        if nivel == 1:
            texto = f"Sonar: algo {peixe.raridade} se aproxima..."
        else:
            texto = f"Sonar: {peixe.nome} ({peixe.raridade})"
        desenhar_texto_sombra(self.tela, texto, self.fontes["media"], RARIDADES[peixe.raridade]["cor"],
                              POSICAO_BOIA, NIVEL_AGUA - 90, True)

    def desenhar_hud(self):
        """Barra de informações no topo e dica de controle embaixo."""
        desenhar_painel(self.tela, pygame.Rect(10, 8, 780, 68))
        pequena = self.fontes["pequena"]
        # linha de cima: dinheiro, dia/horário/clima e local de pesca
        desenhar_texto(self.tela, f"Moedas: {self.moedas}", self.fontes["media"], AMARELO, 25, 16)
        desenhar_texto(self.tela, f"Dia {self.dia} - {self.horario().capitalize()} - {self.clima.capitalize()}",
                       self.fontes["media"], BRANCO, 250, 16)
        desenhar_texto(self.tela, f"Local: {LOCAIS[self.local]['nome']}", self.fontes["media"], AZUL_CLARO, 620, 16)
        # linha de baixo: informações menores
        cheia = len(self.mochila) >= self.capacidade_mochila()
        desenhar_texto(self.tela, self.personagem.nome, pequena, BRANCO, 25, 46)
        desenhar_texto(self.tela, f"Mochila: {len(self.mochila)}/{self.capacidade_mochila()}", pequena,
                       VERMELHO if cheia else BRANCO, 150, 46)
        desenhar_texto(self.tela, f"Iscas: {self.iscas}", pequena, VERMELHO if self.iscas == 0 else BRANCO, 280, 46)
        desenhar_texto(self.tela, f"Equipe: {len(self.funcionarios)}/{MAX_FUNCIONARIOS}", pequena, BRANCO, 355, 46)
        desenhar_texto(self.tela, f"Vendas: {len(self.vendedores)}/{MAX_VENDEDORES}", pequena, BRANCO, 450, 46)
        desenhar_texto(self.tela, f"Coleção: {contar_descobertos(self.colecao)}/{len(PEIXES_COLECAO)}", pequena,
                       BRANCO, 545, 46)
        if self.combo >= 2:
            desenhar_texto(self.tela, f"COMBO x{self.combo}", pequena, AMARELO, 670, 46)
        # barrinha do dia: mostra quanto falta para o fim do dia (salários!)
        proporcao = self.tempo_dia / TEMPO_DIA
        pygame.draw.rect(self.tela, CINZA, (25, 68, 750, 4), border_radius=2)
        pygame.draw.rect(self.tela, AZUL_CLARO, (25, 68, int(750 * proporcao), 4), border_radius=2)

        # Dicionário de dicas: escolhemos a frase pelo sub-estado atual.
        dicas = {
            "esperando": "ESPAÇO lançar  L loja  M vender  O pedidos  E empresa  C coleção  Q conquistas  T local  ESC menu",
            "isca_na_agua": "Esperando o peixe morder...   (ESPAÇO recolhe a linha)",
            "fisgou": "",
            "resultado": "ESPAÇO continuar",
        }
        dica = dicas[self.estado_pesca]
        if dica:
            desenhar_texto_sombra(self.tela, dica, pequena, BRANCO, LARGURA // 2, 585, True)

    def desenhar_avisos(self):
        """Mensagens temporárias, empilhadas no canto esquerdo (abaixo da barra de informações)."""
        for posicao, (texto, _, cor) in enumerate(self.avisos):
            desenhar_texto_sombra(self.tela, texto, self.fontes["mini"], cor, 14, 86 + posicao * 18)

    def desenhar_minigame(self):
        jogo = self.minigame
        peixe = self.peixe_atual
        cor_raridade = RARIDADES[peixe.raridade]["cor"]
        desenhar_painel(self.tela, pygame.Rect(110, 400, 580, 170), cor_raridade)
        if peixe.raridade == "lixo":
            titulo = "Fisgou algo estranho..."
        else:
            titulo = f"Fisgou um peixe {peixe.raridade.upper()}!"
        desenhar_texto(self.tela, titulo, self.fontes["grande"], cor_raridade, LARGURA // 2, 428, True)
        if jogo.acertos_necessarios > 1:
            instrucao = f"Aperte ESPAÇO na zona verde - acertos: {jogo.acertos_feitos}/{jogo.acertos_necessarios}"
        else:
            instrucao = "Aperte ESPAÇO com o marcador na zona verde"
        desenhar_texto(self.tela, instrucao, self.fontes["pequena"], BRANCO, LARGURA // 2, 458, True)

        # A barra vai de x=150 até x=650 (500 pixels). Convertemos as posições
        # de 0.0-1.0 para pixels multiplicando pela largura.
        barra = pygame.Rect(150, 480, 500, 34)
        pygame.draw.rect(self.tela, (60, 60, 75), barra, border_radius=6)
        zona_x = barra.x + (jogo.centro_zona - jogo.largura_zona / 2) * barra.width
        pygame.draw.rect(self.tela, VERDE, (zona_x, barra.y, jogo.largura_zona * barra.width, barra.height))
        pygame.draw.rect(self.tela, BRANCO, barra, 2, border_radius=6)
        marcador_x = barra.x + jogo.posicao * barra.width
        pygame.draw.rect(self.tela, AMARELO, (marcador_x - 3, barra.y - 8, 6, barra.height + 16))

        # Barra de tempo: encolhe conforme o tempo restante diminui.
        proporcao = max(jogo.tempo_restante, 0) / jogo.tempo_limite
        pygame.draw.rect(self.tela, CINZA, (150, 532, 500, 10), border_radius=4)
        pygame.draw.rect(self.tela, VERMELHO if proporcao < 0.3 else AMARELO,
                         (150, 532, int(500 * proporcao), 10), border_radius=4)

    def desenhar_resultado(self):
        peixe = self.peixe_atual
        tipo = self.resultado_tipo
        fonte_g, fonte_m = self.fontes["grande"], self.fontes["media"]
        cor_raridade = RARIDADES[peixe.raridade]["cor"]
        # O painel fica à direita para não cobrir o pescador (e abaixo do HUD).
        centro = 500
        desenhar_painel(self.tela, pygame.Rect(centro - 190, 92, 380, 210), cor_raridade)
        if tipo == "pescou":
            desenhar_texto(self.tela, "Você pescou!", fonte_g, VERDE, centro, 120, True)
            desenhar_peixe(self.tela, centro, 170, peixe.cor, peixe.tamanho)
            desenhar_texto(self.tela, f"{peixe.nome} ({peixe.raridade})", fonte_m, cor_raridade, centro, 220, True)
            desenhar_texto(self.tela, f"Valor: {peixe.valor} moedas (vá ao Mercado)", self.fontes["pequena"],
                           AMARELO, centro, 247, True)
            if self.bonus_combo > 0:
                desenhar_texto(self.tela, f"COMBO x{self.combo}! +{self.bonus_combo} moedas", fonte_m, AMARELO,
                               centro, 273, True)
            if self.peixe_novo:
                desenhar_texto(self.tela, "NOVO!", fonte_m, AMARELO, centro + 145, 120, True)
            if self.extra_rede:
                desenhar_texto(self.tela, "A rede pegou mais um!", self.fontes["pequena"], AZUL_CLARO,
                               centro, 292, True)
            if self.completou_agora:
                desenhar_painel(self.tela, pygame.Rect(centro - 240, 315, 480, 60), AMARELO)
                desenhar_texto(self.tela, "COLEÇÃO COMPLETA! Parabéns!", fonte_g, AMARELO, centro, 345, True)
        elif tipo == "lixo":
            desenhar_texto(self.tela, "Você pescou lixo...", fonte_g, CINZA_CLARO, centro, 120, True)
            desenhar_item(self.tela, centro, 170, peixe, peixe.tamanho)
            desenhar_texto(self.tela, peixe.nome, fonte_m, BRANCO, centro, 220, True)
            desenhar_texto(self.tela, f"+{peixe.valor} moedas (reciclagem)", fonte_m, AMARELO, centro, 250, True)
        elif tipo == "bomba":
            desenhar_texto(self.tela, "BOOM! Peixe-Bomba!", fonte_g, VERMELHO, centro, 120, True)
            desenhar_item(self.tela, centro, 170, peixe, peixe.tamanho)
            desenhar_texto(self.tela, f"-{DANO_BOMBA} moedas e combo perdido", fonte_m, VERMELHO, centro, 235, True)
        elif tipo == "quebrou":
            desenhar_texto(self.tela, "A linha quebrou!", fonte_g, VERMELHO, centro, 120, True)
            desenhar_texto(self.tela, "Era um(a):", fonte_m, BRANCO, centro, 170, True)
            desenhar_texto(self.tela, f"{peixe.nome} ({peixe.raridade})", fonte_m, cor_raridade, centro, 205, True)
            desenhar_texto(self.tela, f"-{self.custo_quebra} moedas (linha nova)", fonte_m, VERMELHO, centro, 245, True)
        else:
            desenhar_texto(self.tela, "O peixe escapou...", fonte_g, VERMELHO, centro, 125, True)
            if peixe.efeito == "bomba":
                desenhar_texto(self.tela, "Ufa! Era uma bomba.", fonte_m, AMARELO, centro, 190, True)
            else:
                desenhar_texto(self.tela, "Era um(a):", fonte_m, BRANCO, centro, 180, True)
                desenhar_texto(self.tela, f"{peixe.nome} ({peixe.raridade})", fonte_m, cor_raridade, centro, 215, True)

    # ---------- LOJA DE PESCA (tela) ----------
    def entrega_pendente(self, chave):
        """Segundos que faltam para a entrega dessa melhoria chegar, ou None se não há pedido."""
        for pedido_chave, restante in self.entregas:
            if pedido_chave == chave:
                return restante
        return None

    def comprar_melhoria(self, chave):
        """Encomenda uma melhoria. Paga na hora, mas a loja demora alguns segundos para entregar."""
        nivel = self.melhorias[chave]
        if self.entrega_pendente(chave) is not None:
            self.msg("Já existe um pedido dessa melhoria a caminho!")
        elif nivel >= MELHORIAS[chave]["nivel_maximo"]:
            self.msg("Essa melhoria já está no nível máximo!")
        else:
            preco = preco_melhoria(chave, nivel)
            if self.moedas < preco:
                self.msg("Moedas insuficientes!")
            else:
                self.moedas -= preco
                prazo = min(TEMPO_ENTREGA_POR_NIVEL * (nivel + 1), TEMPO_ENTREGA_MAXIMO)
                self.entregas.append([chave, prazo])
                self.msg(f"Pedido enviado! Chega em {int(prazo)}s")

    def comprar_iscas(self):
        if self.moedas < PRECO_PACOTE_ISCAS:
            self.msg("Moedas insuficientes!")
        else:
            self.moedas -= PRECO_PACOTE_ISCAS
            self.iscas += PACOTE_ISCAS
            self.msg(f"Comprou {PACOTE_ISCAS} iscas!")

    def teclas_loja(self, tecla):
        if pygame.K_1 <= tecla <= pygame.K_9:
            # K_1 -> índice 0, K_2 -> índice 1, ... K_9 -> índice 8
            self.comprar_melhoria(ORDEM_MELHORIAS[tecla - pygame.K_1])
        elif tecla == pygame.K_b:
            self.comprar_iscas()
        elif tecla in (pygame.K_l, pygame.K_ESCAPE):
            self.estado = "jogando"

    def desenhar_loja(self):
        desenhar_painel(self.tela, pygame.Rect(20, 15, 760, 570), AMARELO)
        desenhar_texto(self.tela, "Loja de Pesca", self.fontes["grande"], AMARELO, LARGURA // 2, 42, True)
        desenhar_texto(self.tela, f"Moedas: {self.moedas}     Iscas: {self.iscas}", self.fontes["media"], BRANCO,
                       LARGURA // 2, 75, True)
        for indice, chave in enumerate(ORDEM_MELHORIAS):
            info = MELHORIAS[chave]
            nivel = self.melhorias[chave]
            y = 96 + indice * 48
            pygame.draw.rect(self.tela, COR_CARD, (40, y, 720, 44), border_radius=8)
            desenhar_texto(self.tela, f"{indice + 1}. {info['nome']}", self.fontes["media"], BRANCO, 55, y + 3)
            desenhar_texto(self.tela, info["descricao"], self.fontes["pequena"], CINZA_CLARO, 55, y + 25)
            desenhar_texto(self.tela, f"Nível {nivel}/{info['nivel_maximo']}", self.fontes["media"], BRANCO, 450, y + 3)
            restante = self.entrega_pendente(chave)
            if nivel >= info["nivel_maximo"]:
                texto_preco, cor_preco = "MÁXIMO", VERDE
            elif restante is not None:
                texto_preco, cor_preco = f"Entrega em {int(restante) + 1}s...", AZUL_CLARO
            else:
                preco = preco_melhoria(chave, nivel)
                texto_preco = f"{preco} moedas"
                # Preço em vermelho quando o jogador não tem moedas suficientes.
                cor_preco = AMARELO if self.moedas >= preco else VERMELHO
            desenhar_texto(self.tela, texto_preco, self.fontes["pequena"], cor_preco, 450, y + 27)
        if self.tempo_mensagem > 0:
            desenhar_texto(self.tela, self.mensagem_tela, self.fontes["media"], AMARELO, LARGURA // 2, 546, True)
        desenhar_texto(self.tela, f"1-9 encomendar   B comprar {PACOTE_ISCAS} iscas ({PRECO_PACOTE_ISCAS} moedas)   L ou ESC voltar",
                       self.fontes["pequena"], CINZA_CLARO, LARGURA // 2, 570, True)

    # ---------- MERCADO (tela com duas abas: VENDER e ENCOMENDAS) ----------
    LINHAS_VISIVEIS_MERCADO = 11

    def teclas_mercado(self, tecla):
        # TAB troca de aba; M, O e ESC fecham o mercado. O resto depende da aba aberta.
        if tecla == pygame.K_TAB:
            self.mercado_aba = "encomendas" if self.mercado_aba == "vender" else "vender"
        elif tecla in (pygame.K_m, pygame.K_o, pygame.K_ESCAPE):
            self.estado = "jogando"
        elif self.mercado_aba == "vender":
            self.teclas_aba_vender(tecla)
        else:
            self.teclas_aba_encomendas(tecla)

    def teclas_aba_vender(self, tecla):
        fornecedor = FORNECEDORES[self.mercado_forn]
        grupos = self.grupos_mochila()
        if tecla == pygame.K_LEFT:
            self.mercado_forn = (self.mercado_forn - 1) % len(FORNECEDORES)
        elif tecla == pygame.K_RIGHT:
            self.mercado_forn = (self.mercado_forn + 1) % len(FORNECEDORES)
        elif tecla == pygame.K_UP:
            self.mercado_sel = max(0, self.mercado_sel - 1)
        elif tecla == pygame.K_DOWN:
            self.mercado_sel = min(max(0, len(grupos) - 1), self.mercado_sel + 1)
        elif tecla in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
            if grupos:
                self.vender_um(fornecedor, grupos[self.mercado_sel]["nome"])
        elif tecla == pygame.K_v:
            self.vender_tudo(fornecedor)
        # Depois de qualquer ação, mantém a seleção e a rolagem dentro dos limites da lista.
        total = len(self.grupos_mochila())
        self.mercado_sel = min(self.mercado_sel, max(0, total - 1))
        if self.mercado_sel < self.mercado_scroll:
            self.mercado_scroll = self.mercado_sel
        elif self.mercado_sel >= self.mercado_scroll + self.LINHAS_VISIVEIS_MERCADO:
            self.mercado_scroll = self.mercado_sel - self.LINHAS_VISIVEIS_MERCADO + 1

    def teclas_aba_encomendas(self, tecla):
        if tecla == pygame.K_UP:
            self.encomenda_sel = (self.encomenda_sel - 1) % len(FORNECEDORES)
        elif tecla == pygame.K_DOWN:
            self.encomenda_sel = (self.encomenda_sel + 1) % len(FORNECEDORES)
        elif tecla in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.entregar_encomenda(FORNECEDORES[self.encomenda_sel])

    def desenhar_mercado(self):
        pequena, mini, media = self.fontes["pequena"], self.fontes["mini"], self.fontes["media"]
        vendendo = self.mercado_aba == "vender"
        cor_borda = FORNECEDORES[self.mercado_forn].cor if vendendo else AZUL_CLARO
        desenhar_painel(self.tela, pygame.Rect(10, 10, 780, 580), cor_borda)
        desenhar_texto(self.tela, "Mercado", self.fontes["grande"], BRANCO, LARGURA // 2, 35, True)
        desenhar_texto(self.tela, f"Moedas: {self.moedas}   Mochila: {len(self.mochila)}/{self.capacidade_mochila()}"
                       f"   Dia {self.dia}", media, AMARELO, LARGURA // 2, 65, True)
        # As duas abas ficam no canto de cima. A aba aberta ganha destaque.
        for posicao, (nome, aberta) in enumerate((("VENDER", vendendo), ("ENCOMENDAS", not vendendo))):
            botao = pygame.Rect(25 + posicao * 150, 22, 140, 30)
            pygame.draw.rect(self.tela, (70, 90, 130) if aberta else COR_CARD, botao, border_radius=6)
            pygame.draw.rect(self.tela, AMARELO if aberta else CINZA, botao, 3 if aberta else 1, border_radius=6)
            desenhar_texto(self.tela, nome, pequena, BRANCO if aberta else CINZA_CLARO, botao.centerx, botao.centery, True)
        desenhar_texto(self.tela, "TAB troca de aba", mini, CINZA_CLARO, 25, 58)
        if vendendo:
            self.desenhar_aba_vender()
            rodape = "SETAS escolher   ESPAÇO vender 1   V vender tudo   TAB encomendas   ESC voltar"
        else:
            self.desenhar_aba_encomendas()
            rodape = "CIMA/BAIXO escolher   E entregar   TAB vender   ESC voltar"
        if self.tempo_mensagem > 0:
            desenhar_texto(self.tela, self.mensagem_tela, media, AMARELO, LARGURA // 2, 540, True)
        desenhar_texto(self.tela, rodape, pequena, CINZA_CLARO, LARGURA // 2, 570, True)

    def desenhar_aba_vender(self):
        pequena, mini, media = self.fontes["pequena"], self.fontes["mini"], self.fontes["media"]
        fornecedor = FORNECEDORES[self.mercado_forn]
        # abas dos fornecedores (SETAS esquerda/direita)
        for indice, forn in enumerate(FORNECEDORES):
            aba = pygame.Rect(25 + indice * 188, 85, 180, 32)
            selecionada = indice == self.mercado_forn
            pygame.draw.rect(self.tela, (70, 90, 130) if selecionada else COR_CARD, aba, border_radius=6)
            pygame.draw.rect(self.tela, forn.cor if selecionada else CINZA, aba, 3 if selecionada else 1, border_radius=6)
            desenhar_texto(self.tela, forn.nome, pequena, BRANCO if selecionada else CINZA_CLARO,
                           aba.centerx, aba.centery, True)

        # coluna da esquerda: a mochila
        desenhar_texto(self.tela, "Sua mochila (peixe / qtd / frescor / preço aqui)", mini, CINZA_CLARO, 30, 128)
        grupos = self.grupos_mochila()
        if not grupos:
            desenhar_texto(self.tela, "A mochila está vazia.", pequena, CINZA, 30, 160)
        inicio = self.mercado_scroll
        for posicao, grupo in enumerate(grupos[inicio:inicio + self.LINHAS_VISIVEIS_MERCADO]):
            y = 148 + posicao * 31
            linha = pygame.Rect(25, y, 380, 28)
            peixe = PEIXE_POR_NOME[grupo["nome"]]
            if inicio + posicao == self.mercado_sel:
                pygame.draw.rect(self.tela, (70, 90, 130), linha, border_radius=5)
                pygame.draw.rect(self.tela, AMARELO, linha, 2, border_radius=5)
            else:
                pygame.draw.rect(self.tela, COR_CARD, linha, border_radius=5)
            desenhar_texto(self.tela, grupo["nome"], pequena, RARIDADES[peixe.raridade]["cor"], 33, y + 6)
            desenhar_texto(self.tela, f"x{grupo['qtd']}", pequena, BRANCO, 195, y + 6)
            cor_frescor = VERDE if grupo["frescor"] >= 0.6 else (AMARELO if grupo["frescor"] >= 0.3 else VERMELHO)
            desenhar_texto(self.tela, f"{int(grupo['frescor'] * 100)}%", pequena, cor_frescor, 250, y + 6)
            item = self.proximo_item_venda(fornecedor, grupo["nome"])
            if item is None:
                desenhar_texto(self.tela, "não compra", mini, CINZA, 320, y + 8)
            else:
                desenhar_texto(self.tela, f"{self.preco_para(fornecedor, item)}", pequena, AMARELO, 335, y + 6)

        # coluna da direita: dados do fornecedor
        x = 425
        desenhar_texto(self.tela, fornecedor.nome, media, fornecedor.cor, x, 128)
        desenhar_texto(self.tela, fornecedor.descricao, mini, CINZA_CLARO, x, 152)
        nivel = self.nivel_rep(fornecedor)
        desenhar_texto(self.tela, f"Reputação: nível {nivel} ({self.reputacao[fornecedor.nome]} pontos)"
                       f"  +{int(nivel * BONUS_PRECO_POR_REP * 100)}% no preço", pequena, BRANCO, x, 175)
        limite = self.limite_dia(fornecedor)
        vendidos = self.vendidos_hoje[fornecedor.nome]
        desenhar_texto(self.tela, f"Compra hoje: {vendidos}/{limite}  (sobe com Contratos)",
                       pequena, VERMELHO if vendidos >= limite else BRANCO, x, 198)
        if fornecedor.frescor_minimo > 0:
            desenhar_texto(self.tela, f"Só aceita frescor de {int(fornecedor.frescor_minimo * 100)}% ou mais",
                           pequena, AMARELO, x, 221)

        # caixa com a CONTA do preço do peixe selecionado (ótima para entender a lógica)
        caixa = pygame.Rect(x - 5, 250, 365, 235)
        pygame.draw.rect(self.tela, COR_CARD, caixa, border_radius=8)
        pygame.draw.rect(self.tela, fornecedor.cor, caixa, 2, border_radius=8)
        desenhar_texto(self.tela, "COMO O PREÇO É CALCULADO", pequena, AMARELO, x + 5, 258)
        item = None
        if grupos:
            nome_sel = grupos[self.mercado_sel]["nome"]
            item = self.proximo_item_venda(fornecedor, nome_sel)
        if not grupos:
            desenhar_texto(self.tela, "Pesque alguns peixes primeiro.", pequena, CINZA_CLARO, x + 5, 290)
        elif item is None:
            desenhar_texto(self.tela, f"{nome_sel}: este fornecedor", pequena, CINZA_CLARO, x + 5, 290)
            desenhar_texto(self.tela, "não compra (raridade ou frescor).", pequena, CINZA_CLARO, x + 5, 312)
        else:
            peixe = PEIXE_POR_NOME[nome_sel]
            frescor = self.frescor_item(item)
            linhas = [
                (f"{peixe.nome}: valor base", f"{peixe.valor}"),
                (f"x raridade ({peixe.raridade})", f"{fornecedor.mult_raridade[peixe.raridade]:.2f}"),
                (f"x frescor ({int(frescor * 100)}%)", f"{0.4 + 0.6 * frescor:.2f}"),
                (f"x reputação (nível {nivel})", f"{1 + BONUS_PRECO_POR_REP * nivel:.2f}"),
                ("x demanda", f"{self.demanda_atual(fornecedor, nome_sel):.2f}"),
            ]
            for posicao, (rotulo, valor) in enumerate(linhas):
                desenhar_texto(self.tela, rotulo, pequena, BRANCO, x + 5, 285 + posicao * 24)
                desenhar_texto(self.tela, valor, pequena, BRANCO, x + 290, 285 + posicao * 24)
            pygame.draw.line(self.tela, CINZA, (x + 5, 412), (x + 350, 412), 1)
            desenhar_texto(self.tela, "= preço final", media, AMARELO, x + 5, 425)
            desenhar_texto(self.tela, f"{self.preco_para(fornecedor, item)} moedas", media, AMARELO, x + 220, 425)
            desenhar_texto(self.tela, "Cada venda derruba a demanda em 8%.", mini, CINZA_CLARO, x + 5, 458)

    def desenhar_aba_encomendas(self):
        """Uma linha grande por fornecedor, mostrando o pedido, o prazo, a recompensa e se já dá para entregar."""
        pequena, mini, media = self.fontes["pequena"], self.fontes["mini"], self.fontes["media"]
        for indice, fornecedor in enumerate(FORNECEDORES):
            y = 90 + indice * 111
            card = pygame.Rect(25, y, 750, 104)
            selecionado = indice == self.encomenda_sel
            pygame.draw.rect(self.tela, (50, 68, 105) if selecionado else COR_CARD, card, border_radius=8)
            pygame.draw.rect(self.tela, AMARELO if selecionado else fornecedor.cor, card, 3 if selecionado else 2,
                             border_radius=8)
            nivel = self.nivel_rep(fornecedor)
            desenhar_texto(self.tela, fornecedor.nome, media, fornecedor.cor, 42, y + 8)
            desenhar_texto(self.tela, f"Reputação nível {nivel} ({self.reputacao[fornecedor.nome]} pts)", mini,
                           CINZA_CLARO, 42, y + 32)
            encomenda = self.encomendas[fornecedor.nome]
            if encomenda is None:
                desenhar_texto(self.tela, "Sem pedido no momento. Novos pedidos chegam de tempos em tempos.",
                               pequena, CINZA_CLARO, 42, y + 62)
                continue
            # lista de peixes pedidos: verde se já tem o suficiente, vermelho se falta
            pronta = True
            for posicao, (nome, quantidade) in enumerate(encomenda["pedidos"].items()):
                tem = self.contar_para_pedido(fornecedor, nome)
                pronta = pronta and tem >= quantidade
                desenhar_texto(self.tela, f"{nome}: {min(tem, quantidade)}/{quantidade}", pequena,
                               VERDE if tem >= quantidade else VERMELHO, 42 + posicao * 220, y + 62)
            if fornecedor.frescor_minimo > 0:
                desenhar_texto(self.tela, f"(frescor mínimo {int(fornecedor.frescor_minimo * 100)}%)", mini,
                               AMARELO, 42, y + 84)
            desenhar_texto(self.tela, f"Prazo: {formatar_tempo(encomenda['tempo'])}", media,
                           VERMELHO if encomenda["tempo"] < 30 else BRANCO, 520, y + 8)
            desenhar_texto(self.tela, f"Recompensa: {encomenda['recompensa']}", media, AMARELO, 520, y + 38)
            if pronta:
                desenhar_texto(self.tela, "PRONTA! Aperte E", pequena, VERDE, 520, y + 72)
            else:
                desenhar_texto(self.tela, "Faltam peixes", pequena, CINZA_CLARO, 520, y + 72)

    # ---------- EMPRESA (tela): funcionários e expansões ----------
    def contratar_vendedor(self, indice):
        tipo = TIPOS_VENDEDOR[indice]
        if len(self.vendedores) >= MAX_VENDEDORES:
            self.msg("A equipe de vendas já está completa!")
        elif self.moedas < tipo["custo"]:
            self.msg("Moedas insuficientes!")
        else:
            self.moedas -= tipo["custo"]
            novo = Vendedor(indice)
            self.vendedores.append(novo)
            self.msg(f"{novo.nome} ({tipo['nome']}) foi contratado!")

    def contratar(self, indice):
        if self.empresa_aba == "vendas":
            self.contratar_vendedor(indice)
            return
        tipo = TIPOS_FUNCIONARIO[indice]
        if len(self.funcionarios) >= MAX_FUNCIONARIOS:
            self.msg("A equipe já está completa!")
        elif self.moedas < tipo["custo"]:
            self.msg("Moedas insuficientes!")
        else:
            self.moedas -= tipo["custo"]
            novo = Funcionario(indice)
            self.funcionarios.append(novo)
            self.msg(f"{novo.nome} ({tipo['nome']}) foi contratado!")

    def demitir(self):
        # Demite da lista da aba aberta (vendedores ou pescadores).
        lista = self.vendedores if self.empresa_aba == "vendas" else self.funcionarios
        if lista:
            saiu = lista.pop()   # pop() remove o último da lista
            self.msg(f"{saiu.nome} foi demitido.")
        else:
            self.msg("Não há ninguém para demitir.")

    def expansao_comprada(self, expansao):
        if expansao["id"] == "barco":
            return self.venceu
        return expansao["id"] in self.locais_liberados

    def comprar_expansao(self, indice):
        expansao = EXPANSOES[indice]
        if self.expansao_comprada(expansao):
            self.msg("Você já comprou isso!")
        elif expansao["requer"] and expansao["requer"] not in self.locais_liberados:
            self.msg(f"Compre antes: Licença do {LOCAIS[expansao['requer']]['nome']}")
        elif self.moedas < expansao["custo"]:
            self.msg("Moedas insuficientes!")
        else:
            self.moedas -= expansao["custo"]
            if expansao["id"] == "barco":
                self.venceu = True
                self.salvar()
                self.estado = "vitoria"
            else:
                self.locais_liberados.append(expansao["id"])
                self.msg(f"{LOCAIS[expansao['id']]['nome']} liberado! (tecla T troca de local)")

    def teclas_empresa(self, tecla):
        if tecla == pygame.K_TAB:
            self.empresa_aba = "vendas" if self.empresa_aba == "pesca" else "pesca"
        elif tecla in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.contratar(tecla - pygame.K_1)
        elif tecla == pygame.K_d:
            self.demitir()
        elif tecla in (pygame.K_4, pygame.K_5, pygame.K_6) and self.empresa_aba == "pesca":
            self.comprar_expansao(tecla - pygame.K_4)
        elif tecla in (pygame.K_e, pygame.K_ESCAPE):
            self.estado = "jogando"

    def desenhar_empresa(self):
        pequena, mini, media = self.fontes["pequena"], self.fontes["mini"], self.fontes["media"]
        desenhar_painel(self.tela, pygame.Rect(10, 10, 780, 580), AMARELO)
        desenhar_texto(self.tela, "Sua Empresa", self.fontes["grande"], AMARELO, LARGURA // 2, 35, True)
        salarios = sum(pessoa.tipo["salario"] for pessoa in self.funcionarios + self.vendedores)
        desenhar_texto(self.tela, f"Moedas: {self.moedas}   Dia {self.dia}   Salários por dia: {salarios}",
                       media, BRANCO, LARGURA // 2, 65, True)
        if self.ultimo_relatorio:
            r = self.ultimo_relatorio
            cor = VERDE if r["lucro"] >= 0 else VERMELHO
            texto = f"Dia {r['dia']}: vendas {r['vendas']} - salários {r['salarios']} = lucro {r['lucro']}"
        else:
            cor, texto = CINZA_CLARO, "O relatório do primeiro dia aparece quando ele terminar."
        desenhar_texto(self.tela, texto, pequena, cor, LARGURA // 2, 90, True)

        # Duas abas: PESCA (pescadores e expansões) e VENDAS (vendedores). TAB troca.
        for posicao, (nome, chave) in enumerate((("PESCA", "pesca"), ("VENDAS", "vendas"))):
            aberta = self.empresa_aba == chave
            botao = pygame.Rect(25 + posicao * 120, 22, 110, 30)
            pygame.draw.rect(self.tela, (70, 90, 130) if aberta else COR_CARD, botao, border_radius=6)
            pygame.draw.rect(self.tela, AMARELO if aberta else CINZA, botao, 3 if aberta else 1, border_radius=6)
            desenhar_texto(self.tela, nome, pequena, BRANCO if aberta else CINZA_CLARO, botao.centerx, botao.centery, True)
        desenhar_texto(self.tela, "TAB troca de aba", mini, CINZA_CLARO, 25, 58)
        if self.empresa_aba == "vendas":
            self.desenhar_empresa_vendas()
        else:
            self.desenhar_empresa_pesca()

        if self.tempo_mensagem > 0:
            desenhar_texto(self.tela, self.mensagem_tela, media, AMARELO, LARGURA // 2, 570, True)
        else:
            desenhar_texto(self.tela, "Salários são pagos no fim de cada dia. Sem dinheiro, o funcionário pede demissão!",
                           mini, CINZA_CLARO, LARGURA // 2, 563, True)
            desenhar_texto(self.tela, "TAB troca de aba   E ou ESC voltar", pequena, CINZA_CLARO, LARGURA // 2, 581, True)

    def desenhar_empresa_pesca(self):
        pequena, mini, media = self.fontes["pequena"], self.fontes["mini"], self.fontes["media"]
        # contratar (esquerda)
        desenhar_texto(self.tela, "CONTRATAR (teclas 1-3)", pequena, AMARELO, 30, 112)
        for indice, tipo in enumerate(TIPOS_FUNCIONARIO):
            y = 135 + indice * 62
            pygame.draw.rect(self.tela, COR_CARD, (25, y, 380, 56), border_radius=8)
            pygame.draw.rect(self.tela, tipo["cor"], (25, y, 8, 56), border_radius=4)
            cor_custo = AMARELO if self.moedas >= tipo["custo"] else VERMELHO
            desenhar_texto(self.tela, f"{indice + 1}. {tipo['nome']}", media, BRANCO, 45, y + 6)
            desenhar_texto(self.tela, f"{tipo['custo']} moedas", pequena, cor_custo, 290, y + 9)
            desenhar_texto(self.tela, f"salário {tipo['salario']}/dia - pesca a cada {int(tipo['intervalo'])}s - "
                           f"acerta {int(tipo['acerto'] * 100)}%", mini, CINZA_CLARO, 45, y + 36)

        # equipe atual (direita)
        desenhar_texto(self.tela, f"EQUIPE ({len(self.funcionarios)}/{MAX_FUNCIONARIOS})   D demitir o último",
                       pequena, AMARELO, 425, 112)
        caixa = pygame.Rect(420, 135, 355, 182)
        pygame.draw.rect(self.tela, COR_CARD, caixa, border_radius=8)
        if not self.funcionarios:
            desenhar_texto(self.tela, "Ninguém contratado ainda.", pequena, CINZA, 435, 150)
        for posicao, funcionario in enumerate(self.funcionarios):
            y = 142 + posicao * 29
            pygame.draw.circle(self.tela, funcionario.tipo["cor"], (438, y + 10), 7)
            desenhar_texto(self.tela, f"{funcionario.nome} - {funcionario.tipo['nome']}", pequena, BRANCO, 452, y + 3)
            desenhar_texto(self.tela, f"{funcionario.tipo['salario']}/dia", pequena, CINZA_CLARO, 690, y + 3)

        # expansões (embaixo)
        desenhar_texto(self.tela, "EXPANSÕES (teclas 4-6)", pequena, AMARELO, 30, 335)
        for indice, expansao in enumerate(EXPANSOES):
            y = 358 + indice * 68
            comprada = self.expansao_comprada(expansao)
            bloqueada = bool(expansao["requer"]) and expansao["requer"] not in self.locais_liberados
            pygame.draw.rect(self.tela, COR_CARD, (25, y, 750, 60), border_radius=8)
            borda = VERDE if comprada else (CINZA if bloqueada else AMARELO)
            pygame.draw.rect(self.tela, borda, (25, y, 750, 60), 2, border_radius=8)
            desenhar_texto(self.tela, f"{indice + 4}. {expansao['nome']}", media, BRANCO, 45, y + 8)
            desenhar_texto(self.tela, expansao["descricao"], pequena, CINZA_CLARO, 45, y + 35)
            if comprada:
                texto_preco, cor_preco = "COMPRADO", VERDE
            elif bloqueada:
                texto_preco, cor_preco = "bloqueado", CINZA
            else:
                texto_preco = f"{expansao['custo']} moedas"
                cor_preco = AMARELO if self.moedas >= expansao["custo"] else VERMELHO
            desenhar_texto(self.tela, texto_preco, media, cor_preco, 590, y + 20)

    def desenhar_empresa_vendas(self):
        """Aba de vendedores: eles vendem os peixes da mochila sozinhos, ficando com uma comissão."""
        pequena, mini, media = self.fontes["pequena"], self.fontes["mini"], self.fontes["media"]
        desenhar_texto(self.tela, "CONTRATAR VENDEDORES (teclas 1-3)", pequena, AMARELO, 30, 112)
        for indice, tipo in enumerate(TIPOS_VENDEDOR):
            y = 135 + indice * 62
            pygame.draw.rect(self.tela, COR_CARD, (25, y, 380, 56), border_radius=8)
            pygame.draw.rect(self.tela, tipo["cor"], (25, y, 8, 56), border_radius=4)
            cor_custo = AMARELO if self.moedas >= tipo["custo"] else VERMELHO
            desenhar_texto(self.tela, f"{indice + 1}. {tipo['nome']}", media, BRANCO, 45, y + 5)
            desenhar_texto(self.tela, f"{tipo['custo']} moedas", pequena, cor_custo, 290, y + 8)
            desenhar_texto(self.tela, f"salário {tipo['salario']}/dia - 1 venda a cada {int(tipo['intervalo'])}s - "
                           f"comissão {int(tipo['comissao'] * 100)}%", mini, CINZA_CLARO, 45, y + 26)
            ate = tipo["raridades"][-1]
            extra = " - entrega encomendas" if tipo["entrega"] else ""
            desenhar_texto(self.tela, f"vende até: {ate}{extra}", mini, AMARELO, 45, y + 40)

        desenhar_texto(self.tela, f"VENDEDORES ({len(self.vendedores)}/{MAX_VENDEDORES})   D demitir o último",
                       pequena, AMARELO, 425, 112)
        caixa = pygame.Rect(420, 135, 355, 182)
        pygame.draw.rect(self.tela, COR_CARD, caixa, border_radius=8)
        if not self.vendedores:
            desenhar_texto(self.tela, "Ninguém contratado ainda.", pequena, CINZA, 435, 150)
        for posicao, vendedor in enumerate(self.vendedores):
            y = 142 + posicao * 29
            pygame.draw.circle(self.tela, vendedor.tipo["cor"], (438, y + 10), 7)
            desenhar_texto(self.tela, f"{vendedor.nome} - {vendedor.tipo['nome']}", pequena, BRANCO, 452, y + 3)
            desenhar_texto(self.tela, f"{vendedor.tipo['salario']}/dia", pequena, CINZA_CLARO, 690, y + 3)

        caixa = pygame.Rect(25, 335, 750, 215)
        pygame.draw.rect(self.tela, COR_CARD, caixa, border_radius=8)
        pygame.draw.rect(self.tela, AMARELO, caixa, 2, border_radius=8)
        desenhar_texto(self.tela, "COMO OS VENDEDORES TRABALHAM", pequena, AMARELO, 40, 345)
        regras = [
            "1. A cada intervalo, o vendedor procura o MELHOR preço entre os 4 fornecedores e vende 1 peixe.",
            "2. Ele fica com a comissão: você recebe só o resto do preço.",
            "3. Nunca vende peixes que estão pedidos em uma encomenda ativa.",
            "4. Respeita o limite diário e a demanda de cada fornecedor.",
            "5. Só o Gerente de Vendas também entrega as encomendas prontas.",
            "6. Salário pago no fim do dia, junto com o dos pescadores. Sem dinheiro, ele sai.",
        ]
        for posicao, regra in enumerate(regras):
            desenhar_texto(self.tela, regra, pequena, BRANCO, 40, 375 + posicao * 27)

    # ---------- VITÓRIA ----------
    def teclas_vitoria(self, tecla):
        if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            self.estado = "jogando"   # o jogo continua em "modo livre"

    def desenhar_vitoria(self):
        desenhar_painel(self.tela, pygame.Rect(120, 100, 560, 400), AMARELO)
        desenhar_texto(self.tela, "VOCÊ COMPROU O BARCO!", self.fontes["grande"], AMARELO, LARGURA // 2, 150, True)
        desenhar_texto(self.tela, "Seu negócio de pesca virou um império.", self.fontes["media"], BRANCO,
                       LARGURA // 2, 195, True)
        linhas = [
            f"Dias de trabalho: {self.estat['dias'] + 1}",
            f"Peixes pescados: {self.estat['pescados']}",
            f"Coleção: {contar_descobertos(self.colecao)}/{len(PEIXES_COLECAO)}",
            f"Encomendas cumpridas: {self.estat['encomendas']}",
            f"Conquistas: {len(self.conquistas_ganhas)}/{len(CONQUISTAS)}",
            f"Funcionários: {len(self.funcionarios)}",
        ]
        for posicao, linha in enumerate(linhas):
            desenhar_texto(self.tela, linha, self.fontes["media"], BRANCO, LARGURA // 2, 250 + posicao * 32, True)
        desenhar_texto(self.tela, "ENTER - continuar jogando (modo livre)", self.fontes["pequena"], CINZA_CLARO,
                       LARGURA // 2, 470, True)

    # ---------- COLEÇÃO (tela) ----------
    def teclas_colecao(self, tecla):
        if tecla in (pygame.K_c, pygame.K_ESCAPE):
            self.estado = "jogando"

    def desenhar_colecao(self):
        desenhar_painel(self.tela, pygame.Rect(10, 8, 780, 584))
        desenhar_texto(self.tela, "Coleção de Peixes", self.fontes["grande"], BRANCO, LARGURA // 2, 32, True)
        mini = self.fontes["mini"]
        # Grade de 5 colunas: a coluna é o resto da divisão e a linha é a divisão inteira.
        for indice, peixe in enumerate(PEIXES_COLECAO):
            coluna = indice % 5
            linha = indice // 5
            card = pygame.Rect(22 + coluna * 152, 56 + linha * 82, 146, 77)
            quantidade = self.colecao[peixe.nome]
            cor_raridade = RARIDADES[peixe.raridade]["cor"]
            pygame.draw.rect(self.tela, COR_CARD, card, border_radius=8)
            pygame.draw.rect(self.tela, cor_raridade if quantidade > 0 else CINZA, card, 2, border_radius=8)
            if quantidade > 0:
                desenhar_peixe(self.tela, card.centerx + 8, card.y + 24, peixe.cor, 14)
                desenhar_texto(self.tela, peixe.nome, mini, BRANCO, card.centerx, card.y + 50, True)
                desenhar_texto(self.tela, f"{peixe.raridade} - {quantidade}x", mini, cor_raridade,
                               card.centerx, card.y + 66, True)
            else:
                # Peixe não descoberto: silhueta cinza e nome escondido.
                desenhar_peixe(self.tela, card.centerx + 8, card.y + 24, (70, 70, 80), 14)
                desenhar_texto(self.tela, "???", mini, CINZA, card.centerx, card.y + 50, True)
                desenhar_texto(self.tela, peixe.raridade, mini, CINZA, card.centerx, card.y + 66, True)
        descobertos = contar_descobertos(self.colecao)
        if colecao_completa(self.colecao):
            texto, cor = "Coleção completa! Você é um mestre da pesca!", AMARELO
        else:
            texto, cor = f"Descobertos: {descobertos}/{len(PEIXES_COLECAO)}   (C ou ESC voltar)", CINZA_CLARO
        desenhar_texto(self.tela, texto, self.fontes["pequena"], cor, LARGURA // 2, 578, True)

    # ---------- CONQUISTAS (tela) ----------
    def teclas_conquistas(self, tecla):
        if tecla in (pygame.K_q, pygame.K_ESCAPE):
            self.estado = "jogando"

    def desenhar_conquistas(self):
        desenhar_painel(self.tela, pygame.Rect(10, 8, 780, 584), AMARELO)
        desenhar_texto(self.tela, "Conquistas", self.fontes["grande"], AMARELO, LARGURA // 2, 35, True)
        desenhar_texto(self.tela, f"{len(self.conquistas_ganhas)}/{len(CONQUISTAS)} desbloqueadas",
                       self.fontes["pequena"], CINZA_CLARO, LARGURA // 2, 62, True)
        for indice, conquista in enumerate(CONQUISTAS):
            coluna = indice % 2
            linha = indice // 2
            card = pygame.Rect(25 + coluna * 380, 80 + linha * 49, 365, 45)
            ganha = conquista["id"] in self.conquistas_ganhas
            pygame.draw.rect(self.tela, COR_CARD, card, border_radius=8)
            pygame.draw.rect(self.tela, AMARELO if ganha else CINZA, card, 2, border_radius=8)
            pygame.draw.circle(self.tela, AMARELO if ganha else CINZA, (card.x + 24, card.centery), 10)
            if ganha:
                pygame.draw.circle(self.tela, COR_CARD, (card.x + 24, card.centery), 4)
            desenhar_texto(self.tela, conquista["nome"], self.fontes["pequena"], BRANCO if ganha else CINZA_CLARO,
                           card.x + 46, card.y + 8)
            desenhar_texto(self.tela, conquista["descricao"], self.fontes["mini"], CINZA_CLARO, card.x + 46, card.y + 28)
        desenhar_texto(self.tela, "Q ou ESC voltar", self.fontes["pequena"], CINZA_CLARO, LARGURA // 2, 578, True)

    # ===== LOOP PRINCIPAL =====
    def tratar_eventos(self):
        """ETAPA 1 do loop: lê teclado e mouse e repassa para a tela ativa."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.KEYDOWN:
                # Máquina de estados: procura no dicionário a função de teclas do estado atual.
                self.funcoes_teclas[self.estado](evento.key)

    def atualizar(self, dt):
        """ETAPA 2 do loop: avança animações e contadores de tempo."""
        self.tempo_total += dt
        self.cenario.atualizar(dt, self.clima)
        if self.tempo_mensagem > 0:
            self.tempo_mensagem -= dt
        # O mundo (dia, funcionários, encomendas...) anda em todas as telas de jogo,
        # mas não no menu nem na escolha do personagem.
        if self.estado in ESTADOS_COM_MUNDO:
            self.atualizar_mundo(dt)
        # A pesca só avança quando estamos na tela de jogo
        # (nas outras telas ela fica parada, mas sempre em "esperando").
        if self.estado == "jogando":
            self.atualizar_pesca(dt)

    def desenhar(self):
        """ETAPA 3 do loop: desenha o cenário e depois a tela do estado atual por cima."""
        self.cenario.desenhar(self.tela, self.tempo_total, self.local, self.horario(), self.clima)
        self.funcoes_desenho[self.estado]()
        # flip mostra na janela tudo o que foi desenhado neste quadro.
        pygame.display.flip()

    def executar(self):
        """
        O loop principal roda ~60 vezes por segundo, sempre nas 3 etapas:
        eventos -> atualização -> desenho.
        """
        while self.rodando:
            # tick(FPS) segura o loop em 60 quadros por segundo e devolve os
            # milissegundos desde o último quadro; dividimos por 1000 para virar segundos.
            # min(..., 0.1) evita um "pulo" gigante se o jogo travar por um instante.
            dt = min(self.relogio.tick(FPS) / 1000, 0.1)
            self.tratar_eventos()
            self.atualizar(dt)
            self.desenhar()
        # Saiu do loop = jogador fechou o jogo. Salvamos antes de encerrar.
        self.salvar()
        pygame.quit()
        sys.exit()


# Este "if" garante que o jogo só começa quando o arquivo é executado
# diretamente (python jogo.py), e não quando é importado por outro arquivo.
if __name__ == "__main__":
    Jogo().executar()
