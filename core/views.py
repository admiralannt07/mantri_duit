from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from .models import Transaction
from .forms import ReceiptForm
from .services.ocr_handler import OCRHandler
from django.db.models import Sum
from django.utils import timezone
from .services.chat_service import ChatService 
from .models import ChatHistory 

# Create your views here.
def landing_page(request):
    # FIX: Gunakan REDIRECT, bukan RENDER. 
    # Redirect memaksa browser memanggil fungsi 'dashboard' di bawah, 
    # sehingga logic hitung saldo dijalankan.
    if request.user.is_authenticated:
        return redirect('dashboard') 
    return render(request, 'landing.html')

@login_required(login_url='/login/')
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # HITUNG CASHFLOW (Logic Sisa Uang)
    total_income = transactions.filter(type='IN').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_expense = transactions.filter(type='OUT').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    current_balance = total_income - total_expense
    
    # Logic status keuangan (buat UI nanti)
    status = "Aman"
    if current_balance < 0:
        status = "Bahaya" # Boncos
    elif current_balance < 100000:
        status = "Waspada" # Tipis

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'current_balance': current_balance,
        'status': status
    }
    return render(request, 'dashboard.html', context)

# View untuk Input Manual (Pemasukan/Pengeluaran tanpa scan)
@login_required(login_url='/login/')
def add_transaction_manual(request):
    if request.method == 'POST':
        t_type = request.POST.get('type')
        amount = int(request.POST.get('amount')) # Pastikan jadi integer
        description = request.POST.get('description')
        date = request.POST.get('date') or timezone.now().date()
        
        # FIX 1: Tampung hasil create ke variabel 't'
        t = Transaction.objects.create(
            user=request.user,
            type=t_type,
            total_amount=amount,
            description=description,
            merchant_name=description, 
            transaction_date=date,
            category='Manual Input'
        )
        
        # --- START AI REACTION ---
        # Kita pakai print error biar tau kenapa kalau gagal
        try:
            service = ChatService(request.user)
            reaction = service.react_to_transaction(t)
            
            # Bersihkan tanda kutip jika AI bandel ngasih kutip
            reaction = reaction.replace('"', '').replace("'", "")

            if t_type == 'IN':
                messages.success(request, f"💰 Masuk Pak Eko! Kata Mantri: \"{reaction}\"")
            else:
                messages.warning(request, f"💸 Tercatat. Kata Mantri: \"{reaction}\"")
        except Exception as e:
            print(f"🔥 AI REACTION ERROR: {e}") # Cek terminal kalau error lagi
            messages.success(request, "Data berhasil dicatat!")
        # --- END AI REACTION ---

        return redirect('dashboard')
        
    return render(request, 'manual_input.html')

@login_required(login_url='/login/')
def scan_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Simpan object sementara (belum commit ke DB)
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            # 2. Panggil AI OCR
            ocr = OCRHandler()
            # Ambil file gambar dari memory/request
            image_file = request.FILES['receipt_image']
            
            # 3. Proses!
            result = ocr.extract_receipt_data(image_file)
            
            if "error" in result:
                messages.error(request, result["error"])
                return redirect('scan_receipt')

            # 4. Isi data otomatis dari hasil AI
            transaction.merchant_name = result.get('merchant_name', 'Unknown')
            transaction.total_amount = result.get('total_amount', 0)
            transaction.transaction_date = result.get('transaction_date')
            transaction.category = result.get('category', 'Lain-lain')
            transaction.raw_ocr_text = str(result) # Simpan log mentah
            
            # 5. Simpan Final
            transaction.save()
            
            # --- START AI REACTION ---
            try:
                service = ChatService(request.user)
                reaction = service.react_to_transaction(transaction)
                # Tampilkan sebagai pesan sukses (tapi isinya omelan AI)
                messages.success(request, f"✅ Nota Disimpan! Kata Mantri: \"{reaction}\"")
            except Exception as e:
                # Fallback kalau AI error/lambat
                messages.success(request, "Nota berhasil disimpan.")
            # --- END AI REACTION ---
            
            return redirect('dashboard')
    else:
        form = ReceiptForm()

    return render(request, 'scan.html', {'form': form})

@login_required(login_url='/login/')
def chat_page(request):
    # Tampilkan history chat
    chats = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
    
    # FIX: Panggil service untuk ambil saldo REAL-TIME buat ditampilkan di bubble awal
    service = ChatService(request.user)
    
    # Kita unpack 3 values (karena service akan kita update di Tahap 3)
    # Variable 'income' dan 'trans_str' kita abaikan dulu pakai underscore (_)
    current_balance, _, _ = service.get_financial_context() 
    
    context = {
        'chats': chats,
        'current_balance': current_balance # Lempar ke template chat.html
    }
    return render(request, 'chat.html', context)

@login_required(login_url='/login/')
def chat_api(request):
    """
    Endpoint ini akan dipanggil oleh HTMX saat user klik kirim.
    Return-nya bukan JSON, tapi potongan HTML (Partial).
    """
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # Panggil Service
        service = ChatService(request.user)
        ai_response = service.ask_mantri(user_message)
        
        # Kembalikan HTML Bubble Chat (User + AI)
        return render(request, 'partials/chat_bubble.html', {
            'message': user_message, 
            'response': ai_response
        })
    return HttpResponse("")

def logout_view(request):
    logout(request)
    return redirect('landing') # Balik ke landing page setelah logout

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Langsung login setelah daftar
            messages.success(request, f"Selamat datang, {user.username}!")
            return redirect('dashboard')
        else:
            # Kalau password gak cocok atau username udah ada
            messages.error(request, "Registrasi gagal. Cek input Anda.")
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

