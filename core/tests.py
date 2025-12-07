import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Transaction, ChatHistory
from core.services.chat_service import ChatService

# Create your tests here.
# --- 1. MODEL TESTS (DATA INTEGRITY) ---
class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_create_income_transaction(self):
        trans = Transaction.objects.create(
            user=self.user,
            total_amount=10000000,
            type='IN',
            category='Omzet',
            merchant_name='Klien Besar',
            description='Project Website',
            transaction_date=timezone.now().date()
        )
        self.assertEqual(trans.total_amount, 10000000)
        self.assertEqual(trans.type, 'IN')
        print("✅ Unit Test: Create Income (IN) Sukses")

    def test_create_expense_transaction(self):
        trans = Transaction.objects.create(
            user=self.user,
            total_amount=50000,
            type='OUT',
            category='Makanan',
            merchant_name='Warteg Bahari',
            transaction_date=timezone.now().date()
        )
        self.assertEqual(trans.total_amount, 50000)
        self.assertEqual(trans.type, 'OUT')
        print("✅ Unit Test: Create Expense (OUT) Sukses")


# --- 2. VIEW TESTS (CRUD & FLOW) ---
class TransactionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        
        # Data Awal Lengkap (Penting untuk Search Test)
        self.trans = Transaction.objects.create(
            user=self.user, 
            total_amount=100000, 
            type='OUT', 
            category='Jajan',
            merchant_name='Toko Jajan Enak', # Tambahkan ini biar search kena
            description='Beli Jajan Sore',   # Tambahkan ini biar search kena
            transaction_date=timezone.now().date()
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_expense', response.context)

    def test_add_manual_transaction(self):
        # FIX: Menggunakan nama URL 'add_manual' sesuai urls.py
        data = {
            'type': 'IN',
            'amount': 5000000,
            'category': 'Gaji',
            'date': timezone.now().date(),
            'description': 'Gajian Bulan Ini'
        }
        response = self.client.post(reverse('add_manual'), data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Transaction.objects.filter(total_amount=5000000, type='IN').exists())
        print("✅ Integration Test: Add Manual Transaction Sukses")

    def test_edit_transaction(self):
        url = reverse('edit_transaction', args=[self.trans.id])
        data = {
            'type': 'OUT',
            'amount': 200000,
            'description': 'Jajan Mahal',
            'date': timezone.now().date()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.trans.refresh_from_db()
        self.assertEqual(self.trans.total_amount, 200000)
        print("✅ Integration Test: Edit Transaction Sukses")

    def test_delete_transaction(self):
        url = reverse('delete_transaction', args=[self.trans.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.count(), 0)
        print("✅ Integration Test: Delete Transaction Sukses")

    def test_history_filter(self):
        # FIX: URL Search query
        url = reverse('transaction_history') + '?search=Jajan'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Pastikan transaksi 'Jajan' muncul di context
        self.assertEqual(len(response.context['transactions']), 1)
        print("✅ Integration Test: History Filter Sukses")


# --- 3. SERVICE & AI MOCK TESTS (FIXED PATCH PATH) ---
class AIServiceMockTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    # FIX: Patch langsung ke library Google, bukan via import di file kita
    # Ini lebih aman dan anti-error AttributeError
    @patch('google.generativeai.GenerativeModel') 
    def test_scan_receipt_mock(self, MockGenerativeModel):
        """
        Simulasi Upload Nota dengan GAMBAR VALID (1x1 Pixel GIF).
        """
        # 1. Setup Mock Response (Jawaban Palsu Gemini)
        mock_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        
        mock_response.text = json.dumps({
            "merchant_name": "Indomaret Mock",
            "total_amount": 50000,
            "transaction_date": "2023-12-01",
            "category": "Keperluan Rumah",
            "transaction_type": "OUT",
            "is_valid_receipt": True
        })
        mock_instance.generate_content.return_value = mock_response

        # 2. Buat File Gambar Palsu tapi VALID (GIF 1x1 Pixel)
        # Django ImageField butuh struktur file gambar asli, bukan cuma text random.
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        image = SimpleUploadedFile("nota.gif", small_gif, content_type="image/gif")

        # 3. Hit Endpoint Scan
        response = self.client.post(reverse('scan_receipt'), {'receipt_image': image})

        # DEBUGGING: Kalau masih error, print ini buat liat kenapa form ditolak
        if response.status_code != 302:
            print(f"\n❌ Form Errors: {response.context.get('form').errors if response.context else 'No Context'}")

        # 4. Assertions
        self.assertEqual(response.status_code, 302) # Redirect = Sukses
        self.assertTrue(Transaction.objects.filter(merchant_name="Indomaret Mock").exists())
        print("✅ Mock Test: Scan Receipt OCR Sukses (Tanpa API Call)")

    # FIX: Patch langsung ke library Google
    @patch('google.generativeai.GenerativeModel')
    def test_chat_service_mock(self, MockGenerativeModel):
        """
        Simulasi Chat Mantri.
        """
        # 1. Setup Mock Response
        mock_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = "Ini jawaban sarkas dari Mantri Mock."
        mock_instance.generate_content.return_value = mock_response

        # 2. Panggil Service Langsung
        service = ChatService(self.user)
        reply = service.ask_mantri("Halo min")

        # 3. Assertions
        self.assertEqual(reply, "Ini jawaban sarkas dari Mantri Mock.")
        self.assertTrue(ChatHistory.objects.filter(response="Ini jawaban sarkas dari Mantri Mock.").exists())
        print("✅ Mock Test: Chat Service Sukses (Tanpa API Call)")