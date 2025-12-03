import json
import datetime
import io 
from PIL import Image
from .gemini_client import GeminiClient
from .prompts import OCR_INSTRUCTION

class OCRHandler:
    def __init__(self):
        self.client = GeminiClient()

    def extract_receipt_data(self, image_file):
        """
        Menerima file gambar, copy ke memori, kirim ke Gemini, return Dict.
        """
        try:
            # NUCLEAR FIX: Baca file ke memori dulu biar aman dari isu pointer
            # Kita support baik file path (string) maupun file object (Django Upload)
            if isinstance(image_file, str):
                image_data = open(image_file, 'rb').read()
            else:
                # Kalau ini file upload dari Django/Python open()
                if hasattr(image_file, 'read'):
                    image_file.seek(0) # Reset pointer ke awal
                    image_data = image_file.read()
                else:
                    image_data = image_file # Asumsi sudah bytes

            # Buka gambar dari RAM
            pil_image = Image.open(io.BytesIO(image_data))
            
        except Exception as e:
            # PRINT ERROR ASLINYA BIAR KITA TAU
            print(f"ERROR SAAT BUKA GAMBAR: {e}") 
            return {"error": f"File gambar rusak atau tidak terbaca. Detail: {str(e)}"}

        # 2. Kirim ke Gemini
        raw_response = self.client.generate_text(OCR_INSTRUCTION, pil_image)

        if not raw_response:
            return {"error": "Gagal menghubungi AI (Response Kosong)"}

        # 3. Bersihkan & Parse JSON
        try:
            cleaned_json = self._clean_json_string(raw_response)
            data = json.loads(cleaned_json)
            
            # Validasi Tanggal
            if not data.get('transaction_date'):
                data['transaction_date'] = datetime.date.today().strftime('%Y-%m-%d')
                
            return data
        except json.JSONDecodeError:
            print(f"JSON ERROR. Raw Output AI: {raw_response}")
            return {"error": "AI bingung baca notanya. Coba foto lebih jelas."}

    def _clean_json_string(self, text):
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"): # Handle kasus markdown tanpa label json
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()