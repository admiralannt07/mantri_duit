import os
import google.generativeai as genai
from django.conf import settings
from PIL import Image

# Konfigurasi API Key sekali jalan saat file di-load
def configure_genai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum diset pada .env")
    genai.configure(api_key=api_key)

class GeminiClient:
    def __init__(self):
        configure_genai()
        # Gunakan Flash untuk kecepatan tinggi di PWA
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_text(self, prompt, image=None):
        """
        Fungsi general untuk kirim prompt + opsi gambar
        """
        try:
            if image:
                # Gemini butuh list inputs [prompt, image]
                response = self.model.generate_content([prompt, image])
            else:
                response = self.model.generate_content(prompt)
            
            return response.text
        except Exception as e:
            print(f"Error Gemini: {e}")
            return None

    def start_chat(self, history=[]):
        """
        Memulai sesi chat dengan history
        """
        return self.model.start_chat(history=history)