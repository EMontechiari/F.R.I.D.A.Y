import os
from pynput.keyboard import Controller, Key

keyboard_controller = Controller()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJETOS_FILE = os.path.join(BASE_DIR, "Dados", "projetos.txt")
COORDENADAS_FILE = os.path.join(BASE_DIR, "Dados", "coordenadas.txt")

def executar_comando_sistema(comando):
    cmd = comando.lower()
    if "spotify" in cmd:
        os.system('start spotify:')
        return "Abrindo o Spotify, Senhor."
    elif "discord" in cmd:
        os.system('start discord:')
        return "Iniciando o Discord, Senhor."
    elif "roblox" in cmd:
        os.system(r'start C:\Users\enzom\AppData\Local\Roblox\Versions\version-e380c8edc8f6477c\RobloxPlayerBeta.exe')
        return "Protocolos do Roblox ativos, Senhor."
    elif any(x in cmd for x in ["pausar", "pause", "play", "tocar", "retomar"]):
        keyboard_controller.press(Key.media_play_pause)
        keyboard_controller.release(Key.media_play_pause)
        return "Entendido, Senhor."
    return None

def salvar_projeto(texto):
    try:
        os.makedirs(os.path.dirname(PROJETOS_FILE), exist_ok=True)
        ideia = texto.lower().replace("salvar projeto", "").strip()
        if ideia:
            with open(PROJETOS_FILE, "a", encoding="utf-8") as f:
                f.write(f"- {ideia}\n")
            return f"Projeto registrado no banco de dados, Senhor."
        return "Não consegui identificar a ideia, Senhor."
    except Exception as e:
        return f"Erro no banco de dados, Senhor: {e}"

def salvar_coordenada(texto):
    try:
        os.makedirs(os.path.dirname(COORDENADAS_FILE), exist_ok=True)
        info = texto.lower().replace("salvar coordenada", "").strip()
        if info:
            with open(COORDENADAS_FILE, "a", encoding="utf-8") as f:
                f.write(f"- {info}\n")
            return f"Coordenada devidamente registrada, Senhor."
        return "Dados insuficientes, Senhor."
    except Exception as e:
        return f"Falha geográfica, Senhor: {e}"

def listar_coordenadas():
    try:
        if not os.path.exists(COORDENADAS_FILE): return "Banco vazio, Senhor."
        with open(COORDENADAS_FILE, "r", encoding="utf-8") as f:
            coords = f.readlines()
        return "Aqui estão os locais, Senhor: " + " ".join([c.strip() for c in coords])
    except: return "Erro ao acessar dados, Senhor."