from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Transaction(models.Model):
    # Pakai UUID biar kelihatan pro & aman (bukan ID: 1, 2, 3)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    
    # Bukti Foto
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    
    # Hasil Ekstraksi AI (Kita simpan raw text nya juga buat jaga-jaga)
    raw_ocr_text = models.TextField(blank=True, null=True)
    
    # Data Terstruktur (Yang masuk pembukuan)
    merchant_name = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0) # Rupiah gak butuh desimal
    transaction_date = models.DateField(null=True, blank=True)
    
    # Kategori (Otomatis ditebak AI nanti: 'Food', 'Transport', 'Business Material')
    category = models.CharField(max_length=50, default='Uncategorized')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant_name} - {self.total_amount}"

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField() # Chat User
    response = models.TextField() # Balasan AI Mantri
    
    # Context (Apakah chat ini ngebahas transaksi tertentu?)
    related_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"