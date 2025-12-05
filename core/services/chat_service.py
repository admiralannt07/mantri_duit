from django.db.models import Sum
from .gemini_client import GeminiClient
from .prompts import get_system_prompt, get_reaction_prompt
from ..models import Transaction, ChatHistory, UserProfile

class ChatService:
    def __init__(self, user):
        self.user = user
        self.client = GeminiClient()

    def get_financial_context(self):
        # 1. Hitung Saldo Real-time
        income = Transaction.objects.filter(user=self.user, type='IN').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        expense = Transaction.objects.filter(user=self.user, type='OUT').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        balance = income - expense

        # 2. Ambil 5 Transaksi Terakhir
        last_transactions = Transaction.objects.filter(user=self.user).order_by('-created_at')[:5]
        trans_str = ""
        for t in last_transactions:
            jenis = "MASUK" if t.type == 'IN' else "KELUAR"
            trans_str += f"- {t.transaction_date}: {jenis} Rp {t.total_amount:,} ({t.merchant_name})\n"
            
        # RETURN 3 VARIABLE: Balance, Income, dan History String
        return balance, income, trans_str
    
    # Fitur Baru: Ambil Riwayat Obrolan
    def get_chat_history_context(self):
        # Ambil 6 chat terakhir (3 pasang tanya-jawab)
        last_chats = ChatHistory.objects.filter(user=self.user).order_by('-timestamp')[:6]
        
        # Karena order_by desc (terbaru diatas), kita balik biar urut kronologis (lama -> baru)
        last_chats = reversed(last_chats)
        
        history_str = ""
        for chat in last_chats:
            history_str += f"User: {chat.message}\nMagatra: {chat.response}\n---\n"
            
        if not history_str:
            return "Belum ada riwayat obrolan."
        return history_str

    def get_business_context(self):
        # FITUR BARU: Ambil deskripsi usaha
        try:
            profile = self.user.profile
            return f"Nama Usaha: {profile.business_name}\nDeskripsi: {profile.business_description}"
        except UserProfile.DoesNotExist:
            return "User belum setting profil usaha. Anggap saja usaha serabutan/umum."

    def ask_mantri(self, user_message):
        # 1. Siapkan Data (Unpack 3 variable)
        balance, income, trans_str = self.get_financial_context()
        business_ctx = self.get_business_context()
        history_ctx = self.get_chat_history_context()
        
        # 2. Rakit Prompt (Kirim income dan business context juga ke prompt generator)
        # Format angka pake k koma separator biar AI gampang baca
        system_prompt = get_system_prompt(self.user.username, f"{balance:,}", f"{income:,}", trans_str, business_ctx, history_ctx)
        
        # 3. Kirim ke Gemini
        full_prompt = f"{system_prompt}\n\nUser bertanya sekarang: {user_message}\nJawab (Ingat Rules Misdirection):"
        
        response_text = self.client.generate_text(full_prompt)
        
        # 4. Simpan History
        if response_text:
            ChatHistory.objects.create(
                user=self.user,
                message=user_message,
                response=response_text
            )
            
        return response_text

    def react_to_transaction(self, transaction):
        """
        AI memberikan komentar pendek setelah transaksi tersimpan.
        """
        # 1. Ambil Data Keuangan
        balance, income, _ = self.get_financial_context()

        if balance < 0:
            return "DARURAT! Saldo lo minus woy! Ini namanya gali lubang tutup lubang. Stop jajan atau cari duit sekarang!"
        
        # 2. Hitung Rasio Dampak (Hanya untuk pengeluaran)
        income_ratio = 0
        if transaction.type == 'OUT' and income > 0:
            income_ratio = (transaction.total_amount / income) * 100
            
        # 3. Buat Prompt Reaksi
        prompt = get_reaction_prompt(
            self.user.username,
            transaction.type,
            transaction.total_amount,
            transaction.merchant_name or transaction.description,
            balance,
            income_ratio
        )
        
        # 4. Generate (Tanpa simpan history chat, biar database gak penuh sampah)
        reaction = self.client.generate_text(prompt)
        return reaction