# ============================================================
# loader.py — Carrega e filtra dados StatsBomb
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os
import pandas as pd
from statsbombpy import sb
from config import COMPETITIONS, ALL_PLAYERS, PLAYER_TRIO, PLAYER_TEAM, PATHS


def extract_team_name(value):
    """Extrai nome do time — API retorna dict ou string."""
    if isinstance(value, dict):
        return value.get('name', str(value))
    return str(value)


def load_competition_events(competition_key: str) -> pd.DataFrame:
    """Carrega todos os eventos de uma competição e filtra pelos 6 jogadores."""
    comp = COMPETITIONS[competition_key]
    print(f"⬇️  Carregando {comp['name']}...")

    matches = sb.matches(
        competition_id=comp['competition_id'],
        season_id=comp['season_id']
    )
    matches['home_team_name'] = matches['home_team'].apply(extract_team_name)
    matches['away_team_name'] = matches['away_team'].apply(extract_team_name)

    relevant = matches[
        matches['home_team_name'].isin(['Real Madrid', 'Barcelona']) |
        matches['away_team_name'].isin(['Real Madrid', 'Barcelona'])
    ].copy()

    comp_events = []
    for _, match in relevant.iterrows():
        try:
            events   = sb.events(match_id=match['match_id'])
            # ✅ coluna correta: 'player' (não 'player_name')
            filtered = events[events['player'].isin(ALL_PLAYERS)].copy()

            if len(filtered) == 0:
                continue

            filtered['match_id']    = match['match_id']
            filtered['match_date']  = match['match_date']
            filtered['home_team']   = match['home_team_name']
            filtered['away_team']   = match['away_team_name']
            filtered['competition'] = comp['name']
            filtered['comp_key']    = competition_key
            filtered['trio']        = filtered['player'].map(PLAYER_TRIO)
            filtered['player_team'] = filtered['player'].map(PLAYER_TEAM)

            # Aliases para compatibilidade
            filtered['player_name'] = filtered['player']
            # ✅ coluna correta: 'type' (não 'type_name')
            filtered['type_name']   = filtered['type']

            if 'location' in filtered.columns:
                filtered['x'] = filtered['location'].apply(
                    lambda loc: loc[0] if isinstance(loc, list) else None
                )
                filtered['y'] = filtered['location'].apply(
                    lambda loc: loc[1] if isinstance(loc, list) else None
                )

            comp_events.append(filtered)

        except Exception as e:
            print(f"   ⚠️  match {match['match_id']}: {e}")

    if not comp_events:
        print(f"   ⚠️  Nenhum evento encontrado para {comp['name']}")
        return pd.DataFrame()

    df = pd.concat(comp_events, ignore_index=True)
    print(f"   ✅ {len(df):,} eventos encontrados")
    return df


def load_all_events() -> pd.DataFrame:
    """Carrega e combina eventos de La Liga e UCL."""
    laliga = load_competition_events('laliga')
    ucl    = load_competition_events('ucl')
    combined = pd.concat([laliga, ucl], ignore_index=True)
    print(f"\n📊 Total combinado: {len(combined):,} eventos")
    return combined


def load_from_csv(competition_key: str = None) -> pd.DataFrame:
    """Carrega eventos de CSV já processado (mais rápido)."""
    if competition_key:
        path = os.path.join(
            PATHS['statsbomb'], 'events', competition_key,
            f'bbc_msn_events_{competition_key}.csv'
        )
        return pd.read_csv(path, low_memory=False)

    laliga = pd.read_csv(os.path.join(
        PATHS['statsbomb'], 'events/laliga/bbc_msn_events_laliga.csv'
    ), low_memory=False)
    ucl = pd.read_csv(os.path.join(
        PATHS['statsbomb'], 'events/ucl/bbc_msn_events_ucl.csv'
    ), low_memory=False)
    return pd.concat([laliga, ucl], ignore_index=True)


def filter_by_event_type(df: pd.DataFrame, event_type: str) -> pd.DataFrame:
    """Filtra eventos por tipo usando coluna type_name."""
    return df[df['type_name'] == event_type].copy()


def filter_by_player(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Filtra eventos por jogador."""
    return df[df['player_name'] == player_name].copy()


def filter_by_trio(df: pd.DataFrame, trio: str) -> pd.DataFrame:
    """Filtra eventos por trio (BBC ou MSN)."""
    return df[df['trio'] == trio].copy()


def get_shots(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna chutes com coordenadas e xG."""
    shots = filter_by_event_type(df, 'Shot')
    shots = shots.dropna(subset=['shot_statsbomb_xg'])

    def parse_coord(loc, idx):
        try:
            if isinstance(loc, str) and loc.startswith('['):
                return eval(loc)[idx]
            if isinstance(loc, list):
                return loc[idx]
        except:
            return None
        return None

    shots['x'] = shots['location'].apply(lambda l: parse_coord(l, 0))
    shots['y'] = shots['location'].apply(lambda l: parse_coord(l, 1))
    return shots.dropna(subset=['x', 'y'])


def summary(df: pd.DataFrame):
    """Imprime resumo dos eventos carregados."""
    print("\n" + "="*50)
    print("📊 RESUMO DOS DADOS")
    print("="*50)
    print(f"Total de eventos : {len(df):,}")
    print(f"Jogadores únicos : {df['player_name'].nunique()}")
    print()
    pivot = df.groupby(
        ['player_name', 'comp_key', 'type_name']
    ).size().unstack(fill_value=0)
    for col in ['Shot', 'Dribble', 'Pass', 'Carry']:
        if col not in pivot.columns:
            pivot[col] = 0
    print(pivot[['Shot', 'Dribble', 'Pass', 'Carry']].to_string())
    print("="*50)