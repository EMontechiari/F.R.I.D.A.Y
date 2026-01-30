import speech_recognition as sr
import google.generativeai as genai
import win32com.client as wincl
import time
import os
from dotenv import load_dotenv
import datetime
import locale
import pvporcupine
import pyaudio
import struct
import threading
import re
import json
import keyboard
from pynput.keyboard import Controller, Key
import pygetwindow as gw

# config de diretório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt-BR')
    except:
        locale.setlocale(locale.LC_TIME, 'brazilian')

load_dotenv(os.path.join(BASE_DIR, '.env'))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")

if not all([GOOGLE_API_KEY, PICOVOICE_ACCESS_KEY]):
    print("ERRO CRÍTICO: Verifique as chaves GOOGLE_API_KEY e PICOVOICE_ACCESS_KEY no seu .env")
    exit()
    
keyboard_controller = Controller()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') 

gemini_lock = threading.Lock()
running = True

# arquivos de dados
MEMORY_FILE = os.path.join(BASE_DIR, "Dados", "memory.json")
PROJECTS_FILE = os.path.join(BASE_DIR, "Dados", "projetos.txt")
memory = {}

def load_memory():
    global memory
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        else:
            memory = {"waypoints": {}, "lembretes": []}
            save_memory()
        print("--- Memória de Longo Prazo carregada. ---")
    except Exception as e:
        print(f"Erro ao carregar a memória: {e}")
        memory = {"waypoints": {}, "lembretes": []}

def save_memory():
    try:
        os.makedirs(os.path.join(BASE_DIR, "Dados"), exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar a memória: {e}")

def save_project(project_text):
    try:
        clean_text = project_text.lower().replace("salvar projeto", "").strip()
        if not clean_text:
            speak("Qual é o nome do projeto, chefe?")
            return
        with open(PROJECTS_FILE, "a", encoding="utf-8") as f:
            f.write(f"- {clean_text}\n")
        speak(f"Projeto '{clean_text}' adicionado ao banco de ideias.")
    except Exception as e:
        print(f"Erro ao salvar projeto: {e}")
        speak("Erro ao gravar o arquivo de projetos.")

def list_projects():
    try:
        if not os.path.exists(PROJECTS_FILE):
            speak("O banco de ideias está vazio, chefe.")
            return
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            projects = f.readlines()
        if not projects:
            speak("Não há projetos pendentes no momento.")
        else:
            speak(f"Você tem {len(projects)} projetos registrados. Aqui estão:")
            for proj in projects:
                speak(proj.strip().replace("-", ""))
    except Exception as e:
        print(f"Erro ao ler projetos: {e}")
        speak("Não consegui acessar o banco de dados.")

def load_mod_list(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            mods = [line.strip() for line in f if line.strip()]
            return ", ".join(mods), len(mods)
    except FileNotFoundError:
        print(f"AVISO: Arquivo de mods '{filename}' não encontrado.")
        return "", 0

speaker = wincl.Dispatch("SAPI.SpVoice")
try:
    voices = speaker.GetVoices()
    target_voice_index = 2  # Muda a voz da IA 
    if target_voice_index < len(voices):
        speaker.Voice = voices.Item(target_voice_index)
        print(f"Voz '{speaker.Voice.GetDescription()}' selecionada com sucesso.")
    else:
        print(f"Índice de voz {target_voice_index} não encontrado.")
except Exception as e:
    print(f"Não foi possível alterar a voz: {e}")

speaker.Rate = 1.45
speaker.Volume = 45

MOD_STRING, MOD_COUNT = load_mod_list(os.path.join(BASE_DIR, "Dados", "modlist.txt"))
print(f"--- Sistema: {MOD_COUNT} mods carregados na memória da FRIDAY. ---")

# Configuração da IA
CONVERSATION_CONTEXT = (
    f"Você é F.R.I.D.A.Y., uma IA tática e engenheira auxiliar. "
    f"Seu foco principal é o mod 'Create' e o addon SatsuIronmanAddon. "
    f"O servidor possui {MOD_COUNT} mods. "
    f"DIRETRIZES DE RESPOSTA:"
    f"1. Para cumprimentos ('oi', 'tudo bem'), seja BREVE e MILITAR (ex: 'Sistemas prontos'). "
    f"2. Se o Chefe pedir ESTRATÉGIAS ou PROJETOS, aí sim dê detalhes, mas busque sempre resumir o máximo que puder pra que ele possa entender rapidamente."
    f"3. Pense como o Tony Stark: tecnologia vence força bruta."
)

conversation = model.start_chat(history=[{'role': 'user', 'parts': [CONVERSATION_CONTEXT]},{'role': 'model', 'parts': ["Protocolos ajustados. Aguardando ordens, chefe."]}])

def clean_text_for_speech(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    return text

def speak(text):
    print(f"FRIDAY: {text}")
    cleaned_text = clean_text_for_speech(text)
    try:
        speaker.Speak(cleaned_text, 1)
    except:
        pass

def get_time():
    now = datetime.datetime.now()
    hora_formatada = now.strftime("%H horas e %M minutos")
    return f"São {hora_formatada}, chefe."

# Data
def get_date():
    now = datetime.datetime.now()
    dias_semana = {0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira", 3: "quinta-feira", 4: "sexta-feira", 5: "sábado", 6: "domingo"}
    meses = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}
    try:
        dia_nome = dias_semana[now.weekday()]
        mes_nome = meses[now.month]
        return f"Hoje é {dia_nome}, {now.day} de {mes_nome}, chefe."
    except:
        return f"Hoje é dia {now.day}, chefe."

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("FRIDAY ouvindo o comando...")
        recognizer.pause_threshold = 1.2
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=8)
            command = recognizer.recognize_google(audio, language='pt-BR')
            print(f"Comando recebido: {command}")
            return command
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Erro no microfone: {e}")
            return None

def open_spotify():
    try:
        speak("Abrindo o Spotify, chefe.")
        os.system('start spotify:')
    except: speak("Não consegui abrir o Spotify.")

def open_discord(): #TODO: corrigir inicialização
    try:
        speak("Abrindo o Discord, chefe.")
        if os.system('start discord:') != 0:
             os.system()
    except: speak("Não consegui abrir o discord.")

def open_roblox(): 
    try:
        speak("Iniciando protocolos do Roblox, chefe.")
        if os.system('start roblox:') != 0:
             # atualizar caso necessário
             os.system(r'start C:\Users\enzom\AppData\Local\Roblox\Versions\version-e380c8edc8f6477c\RobloxPlayerBeta.exe')
    except: speak("Não consegui abrir o roblox.")

def press_media_key(key):
    try:
        keyboard_controller.press(key)
        keyboard_controller.release(key)
    except: speak("Falha no controle de mídia.")

def process_command(prompt):
    global running
    if not prompt: return 

    prompt_lower = prompt.lower()
    
    if "salvar projeto" in prompt_lower:
        save_project(prompt)
    elif "listar projetos" in prompt_lower or "quais projetos" in prompt_lower:
        list_projects()
    elif "abra o spotify" in prompt_lower or "abrir spotify" in prompt_lower:
        open_spotify()
    elif "abrir discord" in prompt_lower or "abra discord" in prompt_lower:
        open_discord()
    elif "abrir roblox" in prompt_lower or "abra roblox" in prompt_lower:
        open_roblox()
    elif "pause" in prompt_lower or "pausar" in prompt_lower:
        speak("Pausando.")
        press_media_key(Key.media_play_pause)
    elif "play" in prompt_lower or "tocar" in prompt_lower or "retomar" in prompt_lower:
        speak("Retomando.")
        press_media_key(Key.media_play_pause)
    elif "próxima" in prompt_lower:
        speak("Próxima faixa.")
        press_media_key(Key.media_next)
    elif "anterior" in prompt_lower or "voltar" in prompt_lower:
        speak("Faixa anterior.")
        press_media_key(Key.media_previous)
    elif 'hora' in prompt_lower:
        speak(get_time())
    elif 'data' in prompt_lower or 'dia' in prompt_lower:
        speak(get_date())
    elif "desligar sistema" in prompt_lower:
        speak("Entendido, chefe. Desligando.")
        time.sleep(1)
        running = False
    else:
        try:
            with gemini_lock:
                response = conversation.send_message(prompt)
            speak(response.text)
        except Exception as e:
            print(f"Erro API: {e}")
            speak("Sem conexão.")

def on_cancel_key_press(e):
    if speaker.Status.RunningState == 2:
        speaker.Speak("", 2)

def hotkey_listener_loop():
    keyboard.on_press_key("pause", on_cancel_key_press)
    while running:
        time.sleep(1)

def voice_input_loop():
    global running
    keyword_paths = [os.path.join(BASE_DIR, "Library", "Sexta-Feira_pt_windows_v3_0_0.ppn")]
    model_file_path = os.path.join(BASE_DIR, "Library", "porcupine_params_pt.pv")
    
    porcupine = None
    pa = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(access_key=PICOVOICE_ACCESS_KEY, keyword_paths=keyword_paths, model_path=model_file_path)
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        
        print("--- F.R.I.D.A.Y. Online ---")
        
        while running:
            # Leitura do Porcupine
            try:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                keyword_index = porcupine.process(pcm_unpacked)
            except:
                continue

            if keyword_index >= 0:
                if speaker.Status.RunningState == 2: speaker.Speak("", 2) 
                
                audio_stream.stop_stream()
                
                tentativas = 0
                max_tentativas = 3
                
                while tentativas < max_tentativas:
                    command = listen_for_command()
                    
                    if command:
                        process_command(command)
                        break 
                    else:
                        tentativas += 1
                        if tentativas < max_tentativas:
                            speak("Não entendi. Repita?")
                        else:
                            speak("Cancelando.")
                
                audio_stream.start_stream()

    except Exception as e:
        print(f"Erro Crítico Voz: {e}")
        running = False
    finally:
        if porcupine: porcupine.delete()
        if audio_stream: audio_stream.close()
        if pa: pa.terminate()

def text_input_loop():
    global running
    while running:
        try:
            prompt = input()
            if prompt:
                if speaker.Status.RunningState == 2: speaker.Speak("", 2)
                process_command(prompt)
        except:
            running = False
            break

if __name__ == "__main__":
    load_memory()
    speak("Sistemas online.")
    
    voice_thread = threading.Thread(target=voice_input_loop)
    hotkey_thread = threading.Thread(target=hotkey_listener_loop)
    
    voice_thread.start()
    hotkey_thread.start()
    
    text_input_loop()
    
    voice_thread.join()
    hotkey_thread.join()
    print("Até logo Chefe.")