# ============================================================
# config.py — Configurações e constantes do projeto
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os

# ------------------------------------------------------------
# Caminhos base — ajuste PROJECT_ROOT se necessário
# ------------------------------------------------------------
PROJECT_ROOT = '/content/drive/MyDrive/bbc-vs-msn-classifier'

PATHS = {
    'statsbomb': os.path.join(PROJECT_ROOT, 'data/statsbomb'),
    'frames'   : os.path.join(PROJECT_ROOT, 'data/frames'),
    'raw'      : os.path.join(PROJECT_ROOT, 'data/raw'),
    'annotations': os.path.join(PROJECT_ROOT, 'data/annotations'),
    'processed' : os.path.join(PROJECT_ROOT, 'data/processed'),
    'results'   : os.path.join(PROJECT_ROOT, 'results'),
}

# ------------------------------------------------------------
# Jogadores e trios
# ------------------------------------------------------------
BBC_PLAYERS = ['Gareth Frank Bale', 'Karim Benzema', 'Cristiano Ronaldo dos Santos Aveiro']
MSN_PLAYERS = ['Lionel Andrés Messi Cuccittini', 'Neymar da Silva Santos Junior', 'Luis Alberto Suárez Díaz']
ALL_PLAYERS = BBC_PLAYERS + MSN_PLAYERS

PLAYER_TRIO = {
    'Gareth Frank Bale'      : 'BBC',
    'Karim Benzema'    : 'BBC',
    'Cristiano Ronaldo dos Santos Aveiro': 'BBC',
    'Lionel Andrés Messi Cuccittini'     : 'MSN',
    'Neymar da Silva Santos Junior'       : 'MSN',
    'Luis Alberto Suárez Díaz'      : 'MSN',
}

PLAYER_TEAM = {
    'Gareth Frank Bale'      : 'Real Madrid',
    'Karim Benzema'    : 'Real Madrid',
    'Cristiano Ronaldo dos Santos Aveiro': 'Real Madrid',
    'Lionel Andrés Messi Cuccittini'     : 'Barcelona',
    'Neymar da Silva Santos Junior'       : 'Barcelona',
    'Luis Alberto Suárez Díaz'      : 'Barcelona',
}

PLAYER_COLORS = {
    'Gareth Frank Bale'      : '#FFFFFF',  # Real Madrid branco
    'Karim Benzema'    : '#C0C0C0',  # Real Madrid prata
    'Cristiano Ronaldo dos Santos Aveiro': '#00529F',  # Real Madrid azul
    'Lionel Andrés Messi Cuccittini'     : '#A50044',  # Barcelona vermelho
    'Neymar da Silva Santos Junior'       : '#004D98',  # Barcelona azul
    'Luis Alberto Suárez Díaz'      : '#EDBB00',  # Barcelona amarelo
}

# ------------------------------------------------------------
# Competições StatsBomb
# ------------------------------------------------------------
COMPETITIONS = {
    'laliga': {'competition_id': 11, 'season_id': 27, 'name': 'La Liga 2015/16'},
    'ucl'   : {'competition_id': 16, 'season_id': 27, 'name': 'Champions League 2015/16'},
}

# Tipos de eventos para análise
EVENT_TYPES = ['Shot', 'Dribble', 'Pass', 'Carry', 'Pressure']

# Tipos de ação para classificação Moondream
ACTION_TYPES = [
    'finalizacao-pe-direito',
    'finalizacao-pe-esquerdo',
    'finalizacao-cabeca',
    'drible-direita',
    'drible-esquerda',
    'passe-decisivo',
    'conducao-velocidade',
    'outro',
]

# Zonas do campo (sistema StatsBomb: x 0-120, y 0-80)
ZONES = {
    'proprio-campo'     : (0, 60, 0, 80),
    'meio-campo'        : (60, 80, 0, 80),
    'terco-ofensivo'    : (80, 102, 0, 80),
    'area-penalti'      : (102, 120, 18, 62),
    'area-central'      : (108, 120, 30, 50),
}

# Pressão defensiva
PRESSURE_THRESHOLDS = {
    'baixa'  : 5.0,   # defensores a mais de 5m
    'media'  : 3.0,   # defensores entre 3m e 5m
    'alta'   : 0.0,   # defensores a menos de 3m
}

# Moondream
MOONDREAM_ENDPOINT = 'http://localhost:2020/v1'  # local via Moondream Station
# ou use a API cloud: https://api.moondream.ai/v1

MOONDREAM_PROMPTS = {
    'action': (
        "O jogador está: (A) finalizando com pé direito, "
        "(B) finalizando com pé esquerdo, (C) finalizando de cabeça, "
        "(D) driblando para direita, (E) driblando para esquerda, "
        "(F) fazendo passe decisivo, (G) conduzindo em velocidade. "
        "Responda apenas com a letra."
    ),
    'posture': (
        "Descreva em uma frase curta a posição corporal do jogador "
        "e a orientação do seu corpo em relação ao gol."
    ),
    'pressure': (
        "Quantos defensores adversários estão a menos de 3 metros "
        "do jogador com a bola? Responda apenas com o número."
    ),
}
# ------------------------------------------------------------
# Mapeamento jogador → slug de pasta
# Usado pelo extractor.py para montar caminhos de frames
# Sem acentos, espaços substituídos por underscore
# ------------------------------------------------------------
PLAYER_SLUG = {
    'Gareth Frank Bale'                  : 'gareth_frank_bale',
    'Karim Benzema'                      : 'karim_benzema',
    'Cristiano Ronaldo dos Santos Aveiro': 'cristiano_ronaldo_dos_santos_aveiro',
    'Lionel Andrés Messi Cuccittini'     : 'lionel_andres_messi_cuccittini',
    'Neymar da Silva Santos Junior'      : 'neymar_da_silva_santos_junior',
    'Luis Alberto Suárez Díaz'           : 'luis_alberto_suarez_diaz',
}

# Mapeamento slug → nome completo (inverso)
SLUG_PLAYER = {v: k for k, v in PLAYER_SLUG.items()}

# Mapeamento liga → pasta SoccerNet
LEAGUE_FOLDER = {
    'laliga': 'spain_laliga',
    'ucl'   : 'europe_uefa-champions-league',
}
