"""
URL configuration for rentalcars project.
"""

from django.contrib import admin
from django.urls import path, include, re_path # --- MODIFICA 1: Aggiunto re_path ---
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # --- MODIFICA 2: Importato serve ---

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('main.urls')),       # Home Page
    path('cars/', include('cars.urls')),   # Car management and API
    path('rentals/', include('rentals.urls')), # Interactive map view
    path('accounts/', include('accounts.urls')), # Accounts manageent
    path('payments/', include('payments.urls')), # Payents management
    path('tools/', include('tools.urls')),  # Tools for test database
    path('api/v1/', include('api.urls')), # django rest framework api
]

# --- MODIFICA 3: Gestione MEDIA e STATIC sia in Debug che in Produzione ---
if settings.DEBUG:
    # In locale (Docker Desktop), Django serve tutto automaticamente
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Sul VPS (Produzione), forziamo Django a servire i file MEDIA (immagini auto)
    # WhiteNoise gestisce gli STATIC, ma questa regola serve per i MEDIA
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
