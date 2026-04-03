# ============================================================
# visualizer.py — Visualizações com mplsoccer
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mplsoccer import Pitch, VerticalPitch
from config import PATHS, PLAYER_COLORS, BBC_PLAYERS, MSN_PLAYERS

PLAYER_SHORT = {
    'Gareth Frank Bale'                  : 'Bale',
    'Karim Benzema'                      : 'Benzema',
    'Cristiano Ronaldo dos Santos Aveiro': 'Cristiano',
    'Lionel Andrés Messi Cuccittini'     : 'Messi',
    'Neymar da Silva Santos Júnior'      : 'Neymar',
    'Luis Alberto Suárez Díaz'           : 'Suárez',
}


def parse_coord(loc, idx):
    """Extrai coordenada x ou y de location."""
    try:
        if isinstance(loc, str) and loc.startswith('['):
            return eval(loc)[idx]
        if isinstance(loc, list):
            return loc[idx]
    except:
        return None
    return None


def prepare_shots(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara DataFrame de chutes com coordenadas."""
    # ✅ usa type_name (alias criado no loader)
    shots = df[df['type_name'] == 'Shot'].copy()
    shots['x'] = shots['location'].apply(lambda l: parse_coord(l, 0))
    shots['y'] = shots['location'].apply(lambda l: parse_coord(l, 1))
    shots = shots.dropna(subset=['x', 'y', 'shot_statsbomb_xg'])
    shots['player_short'] = shots['player_name'].map(PLAYER_SHORT)
    return shots


def plot_shot_map(
    shots_df: pd.DataFrame,
    title: str = 'Shot Map',
    save_path: str = None
):
    """Gera mapa de chutes BBC vs MSN."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 11))
    fig.patch.set_facecolor('#0d1117')
    fig.suptitle(title, color='white', fontsize=18,
                 fontweight='bold', y=1.01)

    for ax, (trio_name, players) in zip(
        axes, [('BBC', BBC_PLAYERS), ('MSN', MSN_PLAYERS)]
    ):
        pitch = VerticalPitch(
            pitch_type='statsbomb', half=True,
            pitch_color='#1a1a2e', line_color='#8d99ae',
            linewidth=1.2, goal_type='box'
        )
        pitch.draw(ax=ax)
        ax.set_facecolor('#1a1a2e')
        ax.set_title(trio_name, color='white', fontsize=14,
                     fontweight='bold', pad=12)

        trio_shots     = shots_df[shots_df['player_name'].isin(players)]
        legend_handles = []

        for player in players:
            p_shots = trio_shots[trio_shots['player_name'] == player]
            if len(p_shots) == 0:
                continue

            color  = PLAYER_COLORS.get(player, '#ffffff')
            p_name = PLAYER_SHORT.get(player, player)

            # ✅ shot_outcome (não shot_outcome_name)
            no_goal = p_shots[p_shots['shot_outcome'] != 'Goal']
            goals   = p_shots[p_shots['shot_outcome'] == 'Goal']

            if len(no_goal) > 0:
                pitch.scatter(
                    no_goal['x'], no_goal['y'], ax=ax,
                    s=no_goal['shot_statsbomb_xg'] * 700 + 30,
                    color=color, edgecolors='white',
                    linewidth=0.4, alpha=0.45, marker='o', zorder=3
                )
            if len(goals) > 0:
                pitch.scatter(
                    goals['x'], goals['y'], ax=ax,
                    s=goals['shot_statsbomb_xg'] * 900 + 60,
                    color=color, edgecolors='white',
                    linewidth=1.0, alpha=0.95, marker='*', zorder=4
                )

            legend_handles.append(mpatches.Patch(
                color=color,
                label=f"{p_name}: {len(goals)}G / {len(p_shots)}S"
                      f" / xG {p_shots['shot_statsbomb_xg'].sum():.1f}"
            ))

        ax.legend(
            handles=legend_handles, loc='lower center',
            fontsize=8.5, facecolor='#0d1117',
            labelcolor='white', framealpha=0.85
        )
        ax.text(0.02, 0.02, 'Tamanho = xG  ⭐ = Gol',
                transform=ax.transAxes, color='#8d99ae', fontsize=7.5)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight',
                    facecolor='#0d1117')
        print(f"💾 Shot map salvo: {save_path}")
    plt.show()


def plot_xg_comparison(
    shots_df: pd.DataFrame,
    title: str = 'xG por Jogador — BBC vs MSN',
    save_path: str = None
):
    """Gráfico de barras comparando xG médio por jogador."""
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')

    summary = shots_df.groupby('player_name').agg(
        total_shots=('shot_statsbomb_xg', 'count'),
        avg_xg     =('shot_statsbomb_xg', 'mean'),
        total_xg   =('shot_statsbomb_xg', 'sum'),
        # ✅ shot_outcome (não shot_outcome_name)
        goals      =('shot_outcome', lambda x: (x == 'Goal').sum())
    ).reset_index().sort_values('avg_xg', ascending=False)

    summary['player_short'] = summary['player_name'].map(PLAYER_SHORT)
    colors = [PLAYER_COLORS.get(p, '#ffffff') for p in summary['player_name']]

    bars = ax.bar(
        summary['player_short'], summary['avg_xg'],
        color=colors, edgecolor='white', linewidth=0.5, alpha=0.85
    )

    for bar, (_, row) in zip(bars, summary.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.002,
            f"G:{int(row['goals'])} ({int(row['total_shots'])}S)",
            ha='center', va='bottom', fontsize=8, color='white'
        )

    ax.set_title(title, color='white', fontsize=14, fontweight='bold')
    ax.set_ylabel('xG Médio por Chute', color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#444444')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight',
                    facecolor='#0d1117')
        print(f"💾 xG comparison salvo: {save_path}")
    plt.show()


def plot_pressure_heatmap(
    events_df: pd.DataFrame,
    player: str,
    title: str = None,
    save_path: str = None
):
    """Heatmap de posição de um jogador em eventos sob pressão."""
    # ✅ usa player_name e under_pressure
    player_events = events_df[
        (events_df['player_name'] == player) &
        (events_df['under_pressure'] == True)
    ].copy()

    player_events['x'] = player_events['location'].apply(
        lambda l: parse_coord(l, 0)
    )
    player_events['y'] = player_events['location'].apply(
        lambda l: parse_coord(l, 1)
    )
    player_events = player_events.dropna(subset=['x', 'y'])

    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#1a1a2e', line_color='#ffffff'
    )
    fig, ax = pitch.draw(figsize=(12, 8))
    fig.patch.set_facecolor('#1a1a2e')

    if len(player_events) > 0:
        pitch.kdeplot(
            player_events['x'], player_events['y'],
            ax=ax, fill=True, cmap='hot', alpha=0.6, levels=20
        )

    p_short = PLAYER_SHORT.get(player, player)
    ax.set_title(
        title or f'Heatmap de Pressão — {p_short}',
        color='white', fontsize=14, fontweight='bold'
    )
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight',
                    facecolor='#1a1a2e')
        print(f"💾 Heatmap salvo: {save_path}")
    plt.show()