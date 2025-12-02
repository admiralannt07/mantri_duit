from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Transaction(models.Model):
    # Pilihan Tipe Transaksi
    TRANSACTION_TYPES = [
        ('IN', 'Pemasukan (Modal/Omzet)'),
        ('OUT', 'Pengeluaran (Belanja)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    
    # KITA TAMBAHKAN FIELD INI
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default='OUT')
    
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    raw_ocr_text = models.TextField(blank=True, null=True)
    
    merchant_name = models.CharField(max_length=100, blank=True, null=True)
    # Deskripsi tambahan biar jelas (misal: "Setor Modal Awal")
    description = models.CharField(max_length=200, blank=True, null=True) 
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    transaction_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50, default='Uncategorized')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.merchant_name} - {self.total_amount}"

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField() # Chat User
    response = models.TextField() # Balasan AI Mantri
    
    # Context (Apakah chat ini ngebahas transaksi tertentu?)
    related_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"