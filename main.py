import asyncio
import datetime
import keyboard
import threading
from brain import JarvisBrain
from voice import JarvisVoice
from tools import executar_comando_sistema, salvar_projeto, salvar_coordenada, listar_coordenadas

async def processar_fluxo(brain, voice, prompt):
    prompt_lower = prompt.lower()
    
    if "salvar projeto" in prompt_lower:
        resposta = salvar_projeto(prompt)
    elif any(x in prompt_lower for x in ["salvar coordenada", "marcar coordenada"]):
        resposta = salvar_coordenada(prompt)
    elif any(x in prompt_lower for x in ["quais coordenadas", "listar coordenadas"]):
        resposta = listar_coordenadas()
    else:
        resposta_tool = executar_comando_sistema(prompt)
        if resposta_tool:
            resposta = resposta_tool
        else:
            hora_atual = datetime.datetime.now().strftime("%H:%M")
            # Injeção de contexto para garantir o tratamento como Senhor
            prompt_completo = f"(Contexto: Agora são {hora_atual}. Trate o usuário estritamente como Senhor.) {prompt}"
            resposta = brain.perguntar(prompt_completo)
    
    await voice.falar(resposta)

def thread_hotkey(voice):
    keyboard.add_hotkey('delete', voice.interromper_fala)
    keyboard.wait()

async def loop_voz(brain, voice):
    while True:
        if voice.escutar_passivo():
            comando = voice.escutar_comando()
            if comando: await processar_fluxo(brain, voice, comando)
        await asyncio.sleep(0.1)

async def loop_teclado(brain, voice):
    while True:
        prompt = await asyncio.to_thread(input, "Senhor: ")
        if prompt: await processar_fluxo(brain, voice, prompt)

async def main():
    brain = JarvisBrain()
    voice = JarvisVoice()
    threading.Thread(target=thread_hotkey, args=(voice,), daemon=True).start()
    print("--- Protocolos JARVIS Online ---")
    await voice.falar("Sistemas inicializados. Às suas ordens, Senhor.")
    await asyncio.gather(loop_voz(brain, voice), loop_teclado(brain, voice))

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\nSistemas em stand-by, Senhor.")