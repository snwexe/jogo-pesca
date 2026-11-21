# Pescaria Tranquila Tycoon

Jogo de pesca 2D com economia (tycoon), feito em Python com Pygame.
Pesque, venda para fornecedores, contrate funcionários e compre o Barco Pesqueiro.

As regras completas e a explicação do código estão em [EXPLICACAO.md](EXPLICACAO.md).

## Como rodar no VS Code (Windows)

### 1. Instalar o que precisa (uma vez só)

- **Python 3.8 ou mais novo**: https://www.python.org/downloads/
  Na instalação, marque a opção **"Add python.exe to PATH"**.
- **Git**: https://git-scm.com/downloads
- **VS Code**: https://code.visualstudio.com/
- No VS Code, instale a extensão **Python** (da Microsoft), na aba de extensões (Ctrl+Shift+X).

### 2. Baixar o projeto

Abra um terminal (no VS Code: menu **Terminal > New Terminal**) numa pasta de sua escolha e rode:

```bash
git clone https://github.com/snwexe/jogo-pesca.git
cd jogo-pesca
```

Depois abra a pasta no VS Code: **File > Open Folder** e escolha `jogo-pesca`.
(Ou, no terminal: `code .`)

### 3. Instalar o Pygame

No terminal do VS Code, dentro da pasta do projeto:

```bash
python -m pip install pygame
```

Se aparecer erro dizendo que `python` não foi encontrado, tente `py -m pip install pygame`.

### 4. Rodar o jogo

```bash
python jogo.py
```

(ou `py jogo.py`). Também dá para abrir o arquivo `jogo.py` no VS Code e clicar no botão de
**play** (Run Python File) no canto superior direito.

Uma janela de 800x600 vai abrir. O progresso é salvo em `save.json`, na pasta do jogo,
quando você fecha a janela e no fim de cada dia do jogo.

## Controles principais

| Tecla | Ação |
|---|---|
| ESPAÇO | Lançar a linha / acertar o minigame / continuar |
| L | Loja de melhorias |
| M | Mercado: vender peixes (TAB alterna para as encomendas) |
| O | Mercado: aba de encomendas |
| E | Empresa: funcionários, vendedores e expansões (TAB troca de aba) |
| C | Coleção de peixes |
| Q | Conquistas |
| T | Trocar de local de pesca |
| ESC | Voltar / menu |

A lista completa de teclas está no [EXPLICACAO.md](EXPLICACAO.md).

## Problemas comuns

- **`python` não é reconhecido**: reinstale o Python marcando "Add python.exe to PATH", ou use `py` no lugar de `python`.
- **`No module named pygame`**: rode `python -m pip install pygame` de novo, usando o mesmo Python que roda o jogo.
- **Pygame não instala (Python muito novo)**: use `python -m pip install pygame-ce`. É compatível com este jogo.
- **Começar do zero**: no menu do jogo aperte **N** ou apague o arquivo `save.json`.

## Trabalhando em grupo com Git

Para pegar as mudanças mais recentes do colega:

```bash
git pull
```

Para enviar as suas mudanças:

```bash
git add -A
git commit -m "descreva o que mudou"
git push
```

Para poder dar `git push`, o dono do repositório precisa adicionar você como colaborador
(GitHub > Settings > Collaborators).
