from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # AUTHENTICATION ROUTES
    # 1. Login (Pakai view bawaan Django, tapi kita kasih template sendiri)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # 2. Logout (Kita buat view custom biar simpel redirectnya)
    path('logout/', views.logout_view, name='logout'),
    
    # 3. Register (Kita butuh view khusus)
    path('register/', views.register_view, name='register'),
]