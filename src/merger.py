# ============================================================
# merger.py — Cruza dados StatsBomb + Moondream
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os
import json
import pandas as pd
from config import PATHS, PLAYER_TRIO, PLAYER_TEAM, ZONES


def get_zone(x: float, y: float) -> str:
    """Retorna zona do campo — coordenadas StatsBomb (x:0-120, y:0-80)."""
    if x is None or y is None:
        return 'desconhecido'
    for zone_name, (x_min, x_max, y_min, y_max) in ZONES.items():
        if x_min <= x <= x_max and y_min <= y <= y_max:
            return zone_name
    return 'outro'


def enrich_event(event_row: pd.Series, moondream_result: dict) -> dict:
    """Combina um evento StatsBomb com a classificação Moondream."""
    def parse_coord(loc, idx):
        try:
            if isinstance(loc, str) and loc.startswith('['):
                return eval(loc)[idx]
            if isinstance(loc, list):
                return loc[idx]
        except:
            return None
        return None

    location = event_row.get('location')
    x = parse_coord(location, 0)
    y = parse_coord(location, 1)

    return {
        # Identificação
        'event_id'   : event_row.get('id'),
        'match_id'   : event_row.get('match_id'),
        'timestamp'  : event_row.get('timestamp'),
        'competition': event_row.get('competition', ''),
        'comp_key'   : event_row.get('comp_key', ''),

        # Jogador
        # ✅ usa player_name (alias já criado no loader)
        'player'     : event_row.get('player_name'),
        'trio'       : PLAYER_TRIO.get(event_row.get('player_name', ''), ''),
        'team'       : PLAYER_TEAM.get(event_row.get('player_name', ''), ''),

        # Evento StatsBomb
        # ✅ usa type_name (alias já criado no loader)
        'event_type' : event_row.get('type_name'),
        'x'          : x,
        'y'          : y,
        'zone'       : get_zone(x, y),
        'xg'         : event_row.get('shot_statsbomb_xg'),
        'under_pressure': event_row.get('under_pressure', False),
        # ✅ shot_outcome (não shot_outcome_name)
        'outcome'    : event_row.get('shot_outcome') or event_row.get('dribble_outcome'),

        # Moondream
        'md_action'  : moondream_result.get('action'),
        'md_posture' : moondream_result.get('posture'),
        'md_pressure': moondream_result.get('pressure'),
        'frame_path' : moondream_result.get('frame_path'),
    }


def build_dataset(events_df: pd.DataFrame, classifications: list) -> pd.DataFrame:
    """Constrói dataset final combinando eventos e classificações."""
    class_map = {
        c['frame_path']: c
        for c in classifications
        if c.get('frame_path')
    }

    rows = []
    for _, event in events_df.iterrows():
        event_id = event.get('id', '')
        matching = {k: v for k, v in class_map.items() if str(event_id) in str(k)}
        md_result = list(matching.values())[0] if matching else {}
        rows.append(enrich_event(event, md_result))

    return pd.DataFrame(rows)


def save_dataset(df: pd.DataFrame, name: str) -> str:
    """Salva o dataset final."""
    path = os.path.join(PATHS['processed'], f'{name}.csv')
    df.to_csv(path, index=False)
    print(f"💾 Dataset salvo: {path} ({len(df):,} linhas)")
    return path