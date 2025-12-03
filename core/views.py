from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from .models import Transaction, ChatHistory, UserProfile
from .forms import ReceiptForm, UserProfileForm, UserUpdateForm
from .services.ocr_handler import OCRHandler
from django.db.models import Sum
from django.utils import timezone
from .services.chat_service import ChatService 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json 

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
    # Ambil semua transaksi untuk perhitungan saldo
    all_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Limit 10 transaksi terbaru untuk tampilan list
    transactions = all_transactions[:10]
    
    # HITUNG CASHFLOW (Logic Sisa Uang) - Gunakan all_transactions agar saldo akurat
    total_income = all_transactions.filter(type='IN').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_expense = all_transactions.filter(type='OUT').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
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
    return render(request, 'dashboard/dashboard.html', context)

# View untuk Input Manual (Pemasukan/Pengeluaran tanpa scan)
@login_required(login_url='/login/')
def add_transaction_manual(request):
    if request.method == 'POST':
        t_type = request.POST.get('type')
        amount = int(request.POST.get('amount'))
        description = request.POST.get('description')
        date = request.POST.get('date') or timezone.now().date()
        
        # TANGKAP GAMBAR (OPSIONAL)
        # request.FILES.get('manual_image') akan return None kalau user gak upload
        image = request.FILES.get('manual_image') 
        
        # Simpan ke DB
        t = Transaction.objects.create(
            user=request.user,
            type=t_type,
            total_amount=amount,
            description=description,
            merchant_name=description, 
            transaction_date=date,
            category='Manual Input',
            receipt_image=image # Masukkan gambar ke field receipt_image
        )
        
        # --- START AI REACTION (Sama kayak kemarin) ---
        try:
            service = ChatService(request.user)
            reaction = service.react_to_transaction(t)
            reaction = reaction.replace('"', '').replace("'", "")

            if t_type == 'IN':
                messages.success(request, f"💰 Masuk! Kata Mantri: \"{reaction}\"")
            else:
                messages.warning(request, f"💸 Tercatat. Kata Mantri: \"{reaction}\"")
        except Exception as e:
            messages.success(request, "Data berhasil dicatat!")
        # --- END AI REACTION ---

        return redirect('dashboard')
        
    return render(request, 'dashboard/manual_input.html')

@login_required(login_url='/login/')
def scan_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            ocr = OCRHandler()
            image_file = request.FILES['receipt_image']
            result = ocr.extract_receipt_data(image_file)
            
            # 1. Cek Error Teknis AI (misal API down)
            if "error" in result:
                messages.error(request, result["error"])
                return redirect('scan_receipt')

            # 2. SATPAM: Cek Validitas Gambar (Dari Prompt Baru)
            is_valid = result.get('is_valid_receipt', False)
            if not is_valid:
                messages.error(request, "❌ Gambar ditolak! Ini bukan nota transaksi atau bukti transfer yang valid.")
                return redirect('scan_receipt')

            # 3. DATA CLEANING (Anti-Crash Integrity Error)
            # Handle kasus jika AI mengembalikan null/None
            merchant = result.get('merchant_name') or 'Unknown'
            amount = result.get('total_amount')
            
            # Paksa amount jadi integer 0 jika None atau invalid
            if amount is None:
                amount = 0
            else:
                try:
                    amount = int(amount)
                except:
                    amount = 0

            # Double Check: Kalau lolos is_valid tapi amount 0, tolak juga (opsional, tapi aman)
            if amount == 0:
                 messages.warning(request, "⚠️ Nota terbaca tapi nominal 0. Pastikan total harga terlihat jelas.")
                 return redirect('scan_receipt')

            # --- SIMPAN KE DB (Aman dari Integrity Error) ---
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.merchant_name = merchant
            transaction.total_amount = amount
            transaction.transaction_date = result.get('transaction_date') or timezone.now().date()
            transaction.category = result.get('category', 'Lain-lain')
            
            ai_type = result.get('transaction_type')
            if ai_type not in ['IN', 'OUT']:
                ai_type = 'OUT'
            transaction.type = ai_type
            
            transaction.raw_ocr_text = str(result)
            transaction.save()
            
            # AI Reaction
            try:
                service = ChatService(request.user)
                reaction = service.react_to_transaction(transaction)
                icon = "💰" if transaction.type == 'IN' else "✅"
                messages.success(request, f"{icon} Berhasil! Kata Mantri: \"{reaction}\"")
            except:
                messages.success(request, "Nota berhasil disimpan.")
            
            return redirect('dashboard')
    else:
        form = ReceiptForm()

    return render(request, 'dashboard/scan.html', {'form': form})
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            ocr = OCRHandler()
            image_file = request.FILES['receipt_image']
            result = ocr.extract_receipt_data(image_file)
            
            # 1. Cek Error Teknis AI
            if "error" in result:
                messages.error(request, result["error"])
                return redirect('scan_receipt')

            # 2. VALIDASI DATA SAMPAH (Satpam Baru)
            # Kalau merchant unknown DAN total 0, kemungkinan besar bukan nota
            merchant = result.get('merchant_name', 'Unknown')
            amount = result.get('total_amount', 0)
            
            if (merchant == 'Unknown' or merchant == 'Unknown Store') and amount == 0:
                messages.warning(request, "Gambar tidak dikenali sebagai nota/bukti transfer yang valid. Coba foto ulang yang jelas.")
                return redirect('scan_receipt')

            # Kalau lolos validasi, baru simpan
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            transaction.merchant_name = merchant
            transaction.total_amount = amount
            transaction.transaction_date = result.get('transaction_date')
            transaction.category = result.get('category', 'Lain-lain')
            
            # FIX INTEGRITY ERROR: Pastikan Type tidak pernah None
            ai_type = result.get('transaction_type')
            if ai_type not in ['IN', 'OUT']:
                ai_type = 'OUT' # Default fallback
            transaction.type = ai_type
            
            transaction.raw_ocr_text = str(result)
            transaction.save()
            
            # AI Reaction (Code lama tetap sama)
            try:
                service = ChatService(request.user)
                reaction = service.react_to_transaction(transaction)
                if transaction.type == 'IN':
                    messages.success(request, f"💰 Masuk! Kata Mantri: \"{reaction}\"")
                else:
                    messages.success(request, f"✅ Keluar! Kata Mantri: \"{reaction}\"")
            except Exception as e:
                messages.success(request, "Nota berhasil disimpan.")
            
            return redirect('dashboard')
    else:
        form = ReceiptForm()

    return render(request, 'dashboard/scan.html', {'form': form})

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
    return render(request, 'dashboard/chat.html', context)

@login_required(login_url='/login/')
def chat_api(request):
    """
    Endpoint ini dipanggil HTMX.
    """
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        service = ChatService(request.user)
        ai_response = service.ask_mantri(user_message)
        
        # FIX: Jangan kirim 'message' lagi ke template, cukup 'response' (AI)
        # Karena 'message' (User) sudah dirender duluan oleh JavaScript (Optimistic UI)
        return render(request, 'dashboard/chat_bubble.html', {
            'message': None, # Set None agar if di template tidak jalan
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

    return render(request, 'auth/register.html', {'form': form})

@login_required(login_url='/login/')
def profile_settings(request):
    # Ambil atau buat profile jika belum ada (Safe handling)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil usaha berhasil diupdate! Mantri sekarang lebih paham bisnismu.")
            return redirect('profile_settings')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'dashboard/profile.html', {'form': form})

@login_required(login_url='/login/')
def transaction_history(request):
    """
    Halaman history transaksi dengan filter dan search
    """
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date', '-created_at')
    
    # Filter berdasarkan tipe (IN/OUT)
    transaction_type = request.GET.get('type')
    if transaction_type in ['IN', 'OUT']:
        transactions = transactions.filter(type=transaction_type)
    
    # Filter berdasarkan kategori
    category = request.GET.get('category')
    if category:
        transactions = transactions.filter(category=category)
    
    # Filter berdasarkan tanggal
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        transactions = transactions.filter(transaction_date__gte=date_from)
    if date_to:
        transactions = transactions.filter(transaction_date__lte=date_to)
    
    # Search berdasarkan merchant name atau description
    search_query = request.GET.get('search')
    if search_query:
        transactions = transactions.filter(
            merchant_name__icontains=search_query
        ) | transactions.filter(
            description__icontains=search_query
        )
    
    # Hitung total berdasarkan filter
    total_income = transactions.filter(type='IN').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_expense = transactions.filter(type='OUT').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Ambil semua kategori unik untuk filter dropdown
    categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True).distinct()
    
    # Pagination: 10 transaksi per halaman
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    
    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    context = {
        'transactions': transactions_page, # Pass Page object instead of QuerySet
        'total_income': total_income,
        'total_expense': total_expense,
        'categories': categories,
        'current_type': transaction_type or '',
        'current_category': category or '',
        'current_search': search_query or '',
        'date_from': date_from or '',
        'date_to': date_to or '',
    }
    return render(request, 'dashboard/history.html', context)

@login_required(login_url='/login/')
def settings_page(request):
    user = request.user
    
    # Init Forms
    user_form = UserUpdateForm(instance=user)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        # Cek tombol mana yang ditekan berdasarkan 'name' di HTML
        
        # 1. LOGIC GANTI INFO (Username/Email)
        if 'update_info' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Info profil berhasil diupdate!")
                return redirect('settings_page')
            else:
                messages.error(request, "Gagal update profil. Cek inputan.")

        # 2. LOGIC GANTI PASSWORD (Verifikasi Bawaan Django)
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # PENTING: Update session hash biar gak ke-logout otomatis
                update_session_auth_hash(request, user) 
                messages.success(request, "Password berhasil diubah! Jangan lupa ya.")
                return redirect('settings_page')
            else:
                messages.error(request, "Gagal ganti password. Pastikan password lama benar.")

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, 'dashboard/settings.html', context)
