from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # AUTHENTICATION ROUTES
    # 1. Login (Pakai view bawaan Django, tapi kita kasih template sendiri)
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    
    # 2. Logout (Kita buat view custom biar simpel redirectnya)
    path('logout/', views.logout_view, name='logout'),
    
    # 3. Register (Kita butuh view khusus)
    path('auth/register/', views.register_view, name='register'),

    # 4. Scan Receipt
    path('dashboard/scan/', views.scan_receipt, name='scan_receipt'),

    # 5. Input Manual
    path('dashboard/add/', views.add_transaction_manual, name='add_manual'),

    # 6. Chat
    path('dashboard/chat/', views.chat_page, name='chat_page'),
    path('api/chat/', views.chat_api, name='chat_api'), 
    path('history/', views.transaction_history, name='transaction_history'),
    path('dashboard/profile/', views.profile_settings, name='profile_settings'),
    path('dashboard/settings/', views.settings_page, name='settings_page'),
]