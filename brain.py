from google import genai
from config import GOOGLE_API_KEY, MODEL_NAME, SISTEMA_JARVIS

class JarvisBrain:
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.chat = self.client.chats.create(
            model=MODEL_NAME,
            config={"system_instruction": SISTEMA_JARVIS}
        )

    def perguntar(self, mensagem):
        try:
            response = self.chat.send_message(mensagem)
            return response.text
        except Exception as e:
            return f"Erro na conexão neural: {e}"