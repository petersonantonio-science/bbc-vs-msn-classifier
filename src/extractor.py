# ============================================================
# extractor.py — Extrai frames de vídeo via FFmpeg
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os
import subprocess
import pandas as pd
from config import PATHS, PLAYER_TRIO


def extract_frames(
    video_path: str,
    output_dir: str,
    fps: float = 2.0,
    start_time: str = None,
    duration: float = 5.0
) -> list:
    '''Extrai frames de um vídeo usando FFmpeg.

    Args:
        video_path : caminho para o vídeo
        output_dir : pasta de saída para os frames
        fps        : frames por segundo a extrair (default: 2)
        start_time : timestamp de início no formato HH:MM:SS
        duration   : duração do trecho em segundos (default: 5s)

    Returns:
        lista de caminhos dos frames extraídos
    '''
    os.makedirs(output_dir, exist_ok=True)

    cmd = ['ffmpeg', '-y']

    if start_time:
        # Começa 2s antes para pegar contexto pré-ação
        cmd += ['-ss', start_time]

    cmd += [
        '-i', video_path,
        '-t', str(duration),
        '-vf', f'fps={fps}',
        '-q:v', '2',
        os.path.join(output_dir, 'frame_%04d.jpg')
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Erro FFmpeg: {result.stderr}")
        return []

    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith('.jpg')
    ])
    print(f"✅ {len(frames)} frames extraídos em: {output_dir}")
    return frames


def extract_event_frames(
    event_row: pd.Series,
    video_path: str,
    competition_key: str
) -> str:
    '''Extrai frames de um evento específico e salva na pasta do jogador.''''
    player   = event_row['player_name']
    trio     = PLAYER_TRIO[player].lower()
    player_slug = player.lower().replace(' ', '_')
    event_id = event_row['id']
    timestamp = event_row['timestamp']

    output_dir = os.path.join(
        PATHS['frames'],
        competition_key,
        trio,
        player_slug,
        event_id
    )

    frames = extract_frames(
        video_path=video_path,
        output_dir=output_dir,
        fps=2.0,
        start_time=timestamp,
        duration=5.0
    )
    return output_dir


def batch_extract(events_df: pd.DataFrame, video_map: dict, competition_key: str):
    '''Extrai frames para um batch de eventos.

    Args:
        events_df       : DataFrame com eventos filtrados
        video_map       : dict {match_id: video_path}
        competition_key : 'laliga' ou 'ucl'
    '''
    total = len(events_df)
    print(f"
🎬 Extraindo frames de {total} eventos...")

    for i, (_, row) in enumerate(events_df.iterrows()):
        match_id = row['match_id']
        if match_id not in video_map:
            continue

        video_path = video_map[match_id]
        extract_event_frames(row, video_path, competition_key)

        if (i + 1) % 10 == 0:
            print(f"   {i+1}/{total} eventos processados")

    print(f"
✅ Extração concluída: {total} eventos")