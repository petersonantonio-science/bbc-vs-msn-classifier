# BBC vs MSN - Tactical Action Classifier
## La Liga & Champions League 2015/16

Analise comparativa de padroes de decisao e acao tecnica
entre as duas maiores trincas ofensivas da historia recente
do futebol, usando Moondream 3 + StatsBomb Open Data + SoccerNet.

> Projeto de portfolio open source - Peterson Antonio

---

## Pergunta Central

Os padroes de decisao do BBC e do MSN mudam quando
o contexto passa de campeonato (La Liga) para
eliminatoria europeia (Champions League)?

Mesmos jogadores. Mesma temporada. Pressao diferente.

---

## Os Jogadores

| BBC - Real Madrid | MSN - Barcelona |
|---|---|
| Gareth Frank Bale | Lionel Andres Messi Cuccittini |
| Karim Benzema | Neymar da Silva Santos Junior |
| Cristiano Ronaldo dos Santos Aveiro | Luis Alberto Suarez Diaz |

---

## Contexto Historico

La Liga 2015/16 - Barcelona (91 pts), Real Madrid (90) e
Atletico (88) separados por apenas 3 pontos.

Champions League 2015/16 - Real Madrid eliminou
Manchester City nas quartas e Atletico na semi.
Barcelona caiu para o Atletico nas semis.

---

## Fontes de Dados

| Dataset | Uso | Acesso |
|---|---|---|
| StatsBomb Open Data | Eventos, coordenadas, xG, pressao | Gratuito |
| SoccerNet | Videos dos lances | Gratuito (NDA) |
| Moondream 3 | Classificacao de acao tecnica | Open Source |

---

## Dataset

| Competicao | Jogos BBC | Jogos MSN | Eventos |
|---|---|---|---|
| La Liga 2015/16 | 10 | 10 | 23.767 |
| UCL 2015/16 | 3 | 1* | 554 |

* Cobertura limitada do StatsBomb open data para UCL 2015/16.
Ver secao de Limitacoes.

---

## Como Usar

### 1. Solicite acesso ao SoccerNet
Acesse https://www.soccer-net.org/,
preencha o formulario e aguarde o e-mail com a senha.

### 2. Configure a senha
Crie o arquivo soccernet_key.txt na raiz com apenas a senha:

    sua_senha_aqui

### 3. Execute o notebook de setup
Abra BBC_vs_MSN_Setup.ipynb no Google Colab
e execute as secoes em ordem (1 a 6).

### 4. Instale as dependencias

    pip install -r requirements.txt

---

## Limitacoes Honestas

1. Sem identificacao automatica de jogador
O Moondream 3 classifica acoes, nao identidades.
Os clipes sao segmentados manualmente por jogador.

2. Neymar sem dados na UCL
O StatsBomb open data nao possui jogos do Barcelona
na UCL 2015/16 onde Neymar apareca nos splits disponiveis.

3. Cobertura limitada da UCL
Apenas 1 jogo do Barcelona e 3 do Real Madrid disponiveis
no StatsBomb open data para UCL 2015/16.

4. StatsBomb 360 nao disponivel para 2015/16
Os freeze frames com posicao de todos os jogadores
nao estao na versao gratuita desta temporada.

5. Processamento frame a frame
O Moondream nao tem memoria entre frames.
Contexto temporal precisa ser montado externamente.

---

## Proximos Passos

- [ ] Extracao de frames dos videos SoccerNet
- [ ] Classificacao de acoes com Moondream 3
- [ ] Fine-tuning com dataset anotado
- [ ] Interface web interativa de visualizacao
- [ ] Extensao para Copa do Mundo 2022

---

## Stack

| Ferramenta | Uso |
|---|---|
| Moondream 3 | Classificacao de acao tecnica |
| statsbombpy | Acesso ao StatsBomb Open Data |
| SoccerNet | Download de videos |
| FFmpeg | Extracao de frames |
| OpenCV | Pre-processamento de imagem |
| mplsoccer | Pitch plots e visualizacoes |
| Pandas | Estruturacao do dataset |

---

## Referencias

- StatsBomb Open Data: https://github.com/statsbomb/open-data
- SoccerNet: https://www.soccer-net.org
- Moondream 3: https://moondream.ai/blog/moondream-3-preview
- mplsoccer: https://mplsoccer.readthedocs.io
- statsbombpy: https://github.com/statsbomb/statsbombpy

---

## Licencas e Creditos

- Dados StatsBomb: uso nao-comercial, credito obrigatorio
- Videos SoccerNet: uso nao-comercial, NDA assinado
- Videos originais NAO incluidos no repositorio
- Apenas JSONs de anotacao e codigo sao versionados

Data source: StatsBomb Open Data - statsbomb.com