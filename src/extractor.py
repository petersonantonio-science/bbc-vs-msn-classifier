# ============================================================
# extractor.py — Extrai frames de vídeo via FFmpeg
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os
import subprocess
import pandas as pd
from config import PATHS, PLAYER_SLUG, PLAYER_TRIO, LEAGUE_FOLDER


def extract_frames(
    video_path: str,
    output_dir: str,
    fps: float = 2.0,
    start_time: str = None,
    duration: float = 5.0
) -> list:
    """Extrai frames de um vídeo usando FFmpeg.

    Args:
        video_path : caminho para o vídeo .mkv
        output_dir : pasta de saída para os frames
        fps        : frames por segundo (default: 2)
        start_time : timestamp HH:MM:SS de início
        duration   : duração do trecho em segundos (default: 5s)

    Returns:
        lista de caminhos dos frames extraídos
    """
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
        print(f'❌ Erro FFmpeg: {result.stderr[:200]}')
        return []

    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith('.jpg')
    ])
    print(f'✅ {len(frames)} frames extraídos em: {output_dir}')
    return frames


def get_video_path(
    match_game: str,
    comp_key: str,
    half: int = 1,
    resolution: str = '224p'
) -> str:
    """Monta o caminho do vídeo SoccerNet.

    Args:
        match_game : nome do jogo ex: '2015-11-21 - 20-15 Real Madrid 0 - 4 Barcelona'
        comp_key   : 'laliga' ou 'ucl'
        half       : 1 ou 2
        resolution : '224p' ou '720p'

    Returns:
        caminho completo para o arquivo .mkv
    """
    # ✅ usa LEAGUE_FOLDER do config para montar caminho correto
    league_folder = LEAGUE_FOLDER.get(comp_key, comp_key)

    return os.path.join(
        PATHS['raw'],
        league_folder,
        '2015-2016',
        match_game,
        f'{half}_{resolution}.mkv'
    )


def get_frame_output_dir(
    player_name: str,
    comp_key: str,
    event_id: str
) -> str:
    """Monta o caminho de saída dos frames para um evento.

    Args:
        player_name : nome completo do jogador (StatsBomb)
        comp_key    : 'laliga' ou 'ucl'
        event_id    : ID único do evento StatsBomb

    Returns:
        caminho da pasta de saída para os frames
    """
    # ✅ usa PLAYER_SLUG do config — sem calcular na hora
    player_slug = PLAYER_SLUG.get(player_name)
    if not player_slug:
        raise ValueError(
            f"Jogador '{player_name}' não encontrado em PLAYER_SLUG. "
            f"Verifique config.py."
        )

    trio = PLAYER_TRIO.get(player_name, 'unknown').lower()

    return os.path.join(
        PATHS['frames'],
        comp_key,
        trio,
        player_slug,
        event_id
    )


def extract_event_frames(
    event_row: pd.Series,
    match_game: str,
    comp_key: str,
    half: int = 1,
    fps: float = 2.0,
    duration: float = 5.0,
    resolution: str = '224p'
) -> str:
    """Extrai frames de um evento específico do StatsBomb.

    Args:
        event_row  : linha do DataFrame de eventos StatsBomb
        match_game : nome do jogo no formato SoccerNet
        comp_key   : 'laliga' ou 'ucl'
        half       : 1 ou 2
        fps        : frames por segundo
        duration   : duração do trecho em segundos
        resolution : resolução do vídeo

    Returns:
        caminho da pasta com os frames extraídos
    """
    player_name = event_row['player_name']
    event_id    = str(event_row['id'])
    timestamp   = event_row['timestamp']

    # Determina qual metade do jogo pelo período
    period = event_row.get('period', 1)
    half   = 1 if period == 1 else 2

    # Monta caminhos
    video_path = get_video_path(match_game, comp_key, half, resolution)
    output_dir = get_frame_output_dir(player_name, comp_key, event_id)

    if not os.path.exists(video_path):
        print(f'⚠️  Vídeo não encontrado: {video_path}')
        return None

    frames = extract_frames(
        video_path=video_path,
        output_dir=output_dir,
        fps=fps,
        start_time=timestamp,
        duration=duration
    )

    return output_dir if frames else None


def batch_extract(
    events_df: pd.DataFrame,
    match_game: str,
    comp_key: str,
    fps: float = 2.0,
    duration: float = 5.0,
    resolution: str = '224p',
    event_types: list = None
) -> dict:
    """Extrai frames para todos os eventos de um jogo.

    Args:
        events_df   : DataFrame com eventos filtrados
        match_game  : nome do jogo no formato SoccerNet
        comp_key    : 'laliga' ou 'ucl'
        fps         : frames por segundo
        duration    : duração do trecho em segundos
        resolution  : resolução do vídeo
        event_types : lista de tipos a extrair
                      ex: ['Shot', 'Dribble']
                      None = todos os eventos

    Returns:
        dict {event_id: output_dir}
    """
    if event_types:
        events_df = events_df[
            events_df['type_name'].isin(event_types)
        ]

    total   = len(events_df)
    results = {}
    ok      = 0
    fail    = 0

    print(f'\n🎬 Extraindo frames de {total} eventos...')
    print(f'   Jogo       : {match_game}')
    print(f'   Competição : {comp_key}')
    print(f'   Resolução  : {resolution}')
    print(f'   FPS        : {fps}')
    print(f'   Duração    : {duration}s por evento\n')

    for i, (_, event) in enumerate(events_df.iterrows()):
        output_dir = extract_event_frames(
            event_row=event,
            match_game=match_game,
            comp_key=comp_key,
            fps=fps,
            duration=duration,
            resolution=resolution
        )

        event_id = str(event['id'])
        if output_dir:
            results[event_id] = output_dir
            ok += 1
        else:
            fail += 1

        if (i + 1) % 10 == 0:
            print(f'   {i+1}/{total} eventos processados '
                  f'({ok} OK, {fail} erros)')

    print(f'\n✅ Extração concluída:')
    print(f'   {ok} eventos OK')
    print(f'   {fail} eventos com erro')
    print(f'   {len(results)} pastas criadas')

    return results


def validate_sync(
    video_path: str,
    timestamp: str,
    output_path: str
) -> bool:
    """Extrai 1 frame para validação visual de sincronização.

    Args:
        video_path  : caminho do vídeo .mkv
        timestamp   : timestamp HH:MM:SS do evento
        output_path : caminho de saída do frame .jpg

    Returns:
        True se o frame foi extraído com sucesso
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        'ffmpeg', '-y',
        '-ss', timestamp,
        '-i', video_path,
        '-vframes', '1',
        '-q:v', '2',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(output_path)