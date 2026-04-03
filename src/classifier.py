# ============================================================
# classifier.py — Classifica ações com Moondream 3
# BBC vs MSN — Tactical Action Classifier
# ============================================================

import os
import json
import base64
from PIL import Image
import moondream as md
from config import MOONDREAM_PROMPTS, PATHS


def load_model(endpoint: str = None) -> md.vl:
    '''Carrega o modelo Moondream 3.

    Se endpoint for None, usa o modelo local padrão.
    Para Moondream Station: endpoint='http://localhost:2020/v1'
    '''
    if endpoint:
        print(f"🔌 Conectando ao Moondream Station: {endpoint}")
        return md.vl(endpoint=endpoint)
    else:
        print("⬇️  Carregando Moondream 3 localmente...")
        return md.vl(model='vikhyatk/moondream2')


def classify_frame(model: md.vl, frame_path: str) -> dict:
    '''Classifica a ação em um frame usando Moondream 3.

    Retorna dict com:
      - action   : tipo de ação (A-G)
      - posture  : descrição da postura corporal
      - pressure : número de defensores próximos
    '''
    image = Image.open(frame_path)
    encoded = model.encode_image(image)

    result = {
        'frame_path': frame_path,
        'action'   : None,
        'posture'  : None,
        'pressure' : None,
    }

    try:
        result['action'] = model.query(
            image=encoded,
            question=MOONDREAM_PROMPTS['action']
        )['answer']

        result['posture'] = model.query(
            image=encoded,
            question=MOONDREAM_PROMPTS['posture']
        )['answer']

        result['pressure'] = model.query(
            image=encoded,
            question=MOONDREAM_PROMPTS['pressure']
        )['answer']

    except Exception as e:
        print(f"❌ Erro na classificação de {frame_path}: {e}")

    return result


def classify_event_frames(model: md.vl, frames_dir: str) -> list:
    '''Classifica todos os frames de um evento e retorna a moda das classificações.'''
    frames = sorted([
        os.path.join(frames_dir, f)
        for f in os.listdir(frames_dir)
        if f.endswith('.jpg')
    ])

    if not frames:
        return []

    # Classifica o frame central (mais próximo da ação)
    mid_frame = frames[len(frames) // 2]
    return [classify_frame(model, mid_frame)]


def save_classifications(results: list, output_path: str):
    '''Salva classificações em JSON.'''
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Classificações salvas em: {output_path}")