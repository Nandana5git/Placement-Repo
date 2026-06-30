from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root redirects to the dashboard router
    path('', RedirectView.as_view(url='dashboard/', permanent=False)),
    
    # Modular apps routing
    path('', include('users.urls')),
    path('students/', include('students.urls')),
    path('companies/', include('companies.urls')),
    path('placements/', include('placements.urls')),
    path('analytics/', include('analytics.urls')),
    path('notifications/', include('notifications.urls')),
]

# Service uploaded media & static assets during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
