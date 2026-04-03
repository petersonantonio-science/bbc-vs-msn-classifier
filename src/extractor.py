# ============================================================
# extractor.py — Extrai frames de vídeo via FFmpeg + upscale
# BBC vs MSN — Tactical Action Classifier
#
# Design decisions:
#   - Source    : SoccerNet 224p videos
#   - Upscale   : Real-ESRGAN 4x (~896p)
#   - Window    : 10s per event (4s before + action + 4s after)
#   - FPS       : 4 frames/second = ~40 frames per event
#   - Offset    : -2.26s (StatsBomb records goal, SoccerNet records shot)
#   - Events    : Shot, Dribble, Pass, Carry
# ============================================================

import os
import subprocess
import pandas as pd
from config import (
    PATHS, PLAYER_SLUG, PLAYER_TRIO,
    LEAGUE_FOLDER, SYNC_OFFSET_SECONDS
)

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
FPS             = 4.0    # frames per second
WINDOW_BEFORE   = 4.0    # seconds before StatsBomb timestamp
WINDOW_AFTER    = 6.0    # seconds after (total window = 10s)
RESOLUTION      = "224p"
UPSCALE_FACTOR  = 4      # Real-ESRGAN 4x → ~896p
EVENT_TYPES     = ["Shot", "Dribble", "Pass", "Carry"]


# ------------------------------------------------------------
# Upscale
# ------------------------------------------------------------
def setup_upscaler():
    """Loads Real-ESRGAN model for 4x upscaling."""
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        model = RRDBNet(
            num_in_ch=3, num_out_ch=3,
            num_feat=64, num_block=23, num_grow_ch=32,
            scale=4
        )
        upsampler = RealESRGANer(
            scale=UPSCALE_FACTOR,
            model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True
        )
        print(f"✅ Real-ESRGAN loaded (4x upscale)")
        return upsampler
    except Exception as e:
        print(f"⚠️  Real-ESRGAN not available: {e}")
        print("   Install with: pip install basicsr realesrgan")
        return None


def upscale_frame(upsampler, input_path: str, output_path: str) -> bool:
    """Upscales a single frame using Real-ESRGAN."""
    try:
        import cv2
        import numpy as np

        img = cv2.imread(input_path, cv2.IMREAD_COLOR)
        if img is None:
            return False

        output, _ = upsampler.enhance(img, outscale=UPSCALE_FACTOR)
        cv2.imwrite(output_path, output)
        return True
    except Exception as e:
        print(f"❌ Upscale failed for {input_path}: {e}")
        return False


def upscale_directory(upsampler, frames_dir: str) -> int:
    """Upscales all frames in a directory in-place."""
    if upsampler is None:
        return 0

    frames = sorted([
        f for f in os.listdir(frames_dir)
        if f.endswith(".jpg")
    ])

    ok = 0
    for frame_file in frames:
        input_path  = os.path.join(frames_dir, frame_file)
        output_path = os.path.join(frames_dir, frame_file)
        if upscale_frame(upsampler, input_path, output_path):
            ok += 1

    return ok


# ------------------------------------------------------------
# Timestamp utilities
# ------------------------------------------------------------
def ts_to_seconds(ts: str) -> float:
    """Converts HH:MM:SS.mmm to total seconds."""
    try:
        parts = ts.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
    except:
        return 0.0
    return 0.0


def seconds_to_ts(seconds: float) -> str:
    """Converts total seconds to HH:MM:SS.mmm."""
    seconds  = max(0.0, seconds)
    hours    = int(seconds // 3600)
    minutes  = int((seconds % 3600) // 60)
    secs     = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def get_start_timestamp(statsbomb_ts: str) -> str:
    """Calculates extraction start timestamp.

    Applies sync offset and window_before:
      start = statsbomb_ts - SYNC_OFFSET - WINDOW_BEFORE
    """
    total_seconds = ts_to_seconds(statsbomb_ts)
    start_seconds = total_seconds - SYNC_OFFSET_SECONDS - WINDOW_BEFORE
    return seconds_to_ts(start_seconds)


# ------------------------------------------------------------
# Path utilities
# ------------------------------------------------------------
def get_video_path(
    match_game: str,
    comp_key: str,
    half: int = 1,
) -> str:
    """Builds SoccerNet video path."""
    league_folder = LEAGUE_FOLDER.get(comp_key, comp_key)
    return os.path.join(
        PATHS["raw"],
        league_folder,
        "2015-2016",
        match_game,
        f"{half}_{RESOLUTION}.mkv"
    )


def get_frame_output_dir(
    player_name: str,
    comp_key: str,
    event_id: str
) -> str:
    """Builds output directory for event frames."""
    player_slug = PLAYER_SLUG.get(player_name)
    if not player_slug:
        raise ValueError(
            f"Player \"{player_name}\" not found in PLAYER_SLUG. "
            f"Check config.py."
        )
    trio = PLAYER_TRIO.get(player_name, "unknown").lower()
    return os.path.join(
        PATHS["frames"],
        comp_key,
        trio,
        player_slug,
        event_id
    )


# ------------------------------------------------------------
# Core extraction
# ------------------------------------------------------------
def extract_frames(
    video_path: str,
    output_dir: str,
    start_time: str,
    duration: float = 10.0,
    fps: float = FPS,
) -> list:
    """Extracts frames from a video segment using FFmpeg.

    Args:
        video_path : path to .mkv file
        output_dir : output folder for frames
        start_time : HH:MM:SS.mmm start timestamp
        duration   : segment duration in seconds
        fps        : frames per second to extract

    Returns:
        list of extracted frame paths
    """
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-ss", start_time,
        "-i", video_path,
        "-t", str(duration),
        "-vf", f"fps={fps}",
        "-q:v", "2",
        os.path.join(output_dir, "frame_%04d.jpg")
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FFmpeg error: {result.stderr[:200]}")
        return []

    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".jpg")
    ])
    return frames


def extract_event_frames(
    event_row: pd.Series,
    match_game: str,
    comp_key: str,
    upsampler=None,
) -> str:
    """Extracts and optionally upscales frames for a single event.

    Args:
        event_row  : StatsBomb event row
        match_game : SoccerNet match folder name
        comp_key   : "laliga" or "ucl"
        upsampler  : Real-ESRGAN model (None = no upscale)

    Returns:
        output directory path or None on failure
    """
    player_name = event_row["player_name"]
    event_id    = str(event_row["id"])
    timestamp   = event_row["timestamp"]
    period      = event_row.get("period", 1)
    half        = 1 if period == 1 else 2

    # Skip if already extracted
    output_dir = get_frame_output_dir(player_name, comp_key, event_id)
    if os.path.exists(output_dir) and len(os.listdir(output_dir)) > 0:
        return output_dir

    # Build paths
    video_path  = get_video_path(match_game, comp_key, half)
    if not os.path.exists(video_path):
        return None

    # Calculate start timestamp
    start_time = get_start_timestamp(timestamp)

    # Extract frames
    frames = extract_frames(
        video_path=video_path,
        output_dir=output_dir,
        start_time=start_time,
        duration=WINDOW_BEFORE + WINDOW_AFTER,
        fps=FPS,
    )

    if not frames:
        return None

    # Upscale if model available
    if upsampler is not None:
        upscale_directory(upsampler, output_dir)

    return output_dir


# ------------------------------------------------------------
# Batch extraction
# ------------------------------------------------------------
def batch_extract(
    events_df: pd.DataFrame,
    match_game: str,
    comp_key: str,
    upsampler=None,
    event_types: list = None,
) -> dict:
    """Batch extracts frames for all events in a match.

    Args:
        events_df   : filtered StatsBomb events DataFrame
        match_game  : SoccerNet match folder name
        comp_key    : "laliga" or "ucl"
        upsampler   : Real-ESRGAN model (None = no upscale)
        event_types : list of event types to extract
                      None = uses default EVENT_TYPES

    Returns:
        dict {event_id: output_dir}
    """
    if event_types is None:
        event_types = EVENT_TYPES

    filtered = events_df[
        events_df["type_name"].isin(event_types)
    ].copy()

    total   = len(filtered)
    results = {}
    ok      = 0
    skip    = 0
    fail    = 0

    total_frames_est = total * int(FPS * (WINDOW_BEFORE + WINDOW_AFTER))

    print(f"\n🎬 Batch extraction")
    print(f"   Match      : {match_game}")
    print(f"   Competition: {comp_key}")
    print(f"   Events     : {total} ({', '.join(event_types)})")
    print(f"   Window     : {WINDOW_BEFORE + WINDOW_AFTER}s per event")
    print(f"   FPS        : {FPS}")
    print(f"   Est. frames: ~{total_frames_est:,}")
    print(f"   Upscale    : {'Real-ESRGAN 4x' if upsampler else 'disabled'}\n")

    for i, (_, event) in enumerate(filtered.iterrows()):
        output_dir = extract_event_frames(
            event_row=event,
            match_game=match_game,
            comp_key=comp_key,
            upsampler=upsampler,
        )

        event_id = str(event["id"])
        if output_dir is None:
            fail += 1
        elif output_dir in results.values():
            skip += 1
        else:
            results[event_id] = output_dir
            ok += 1

        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"   {i+1:>5}/{total} | "
                  f"✅ {ok} | ⏭️  {skip} | ❌ {fail}")

    print(f"\n✅ Batch complete:")
    print(f"   Extracted : {ok} events")
    print(f"   Skipped   : {skip} (already exist)")
    print(f"   Failed    : {fail}")
    print(f"   Dirs      : {len(results)}")

    return results


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------
def validate_sync(
    video_path: str,
    timestamp: str,
    output_path: str,
) -> bool:
    """Extracts 1 frame for sync validation."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", timestamp,
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(output_path)