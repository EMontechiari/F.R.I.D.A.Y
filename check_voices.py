import win32com.client as wincl
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

print("--- Verificando vozes TTS instaladas no sistema ---")

try:
    speaker = wincl.Dispatch("SAPI.SpVoice")
    voices = speaker.GetVoices()
    
    if not voices:
        print("\nNenhuma voz encontrada no sistema.")
    else:
        print("\nVozes disponíveis:")
        for i, voice in enumerate(voices):
            # o .GetDescription() retorna com o nome da voz ex: "Microsoft David Desktop - English (United States)"
            print(f"  Índice [{i}]: {voice.GetDescription()}")

except Exception as e:
    print(f"\nOcorreu um erro ao tentar acessar as vozes: {e}")

input("\nDiagnóstico concluído. Pressione Enter para fechar esta janela...")
