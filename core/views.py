from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.
def landing_page(request):
    # Jika user sudah login, lempar langsung ke dashboard (Nanti)
    if request.user.is_authenticated:
        return render(request, 'dashboard.html') # Kita buat file ini nanti
    return render(request, 'landing.html')

@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'dashboard.html')

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

