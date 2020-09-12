from accounts.views import register_view, login_view
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.urls import path

urlpatterns = [
    url(r'^register/$(?i)', register_view, name = 'register'),
    # url(r'^logout/?$', logout_view, name='logout'),
    url(r'^login/?$', login_view, name = 'login'),
    # url('account/', include('accounts.urls')),
    # url('games/', include('games.urls')),
    path('admin/', admin.site.urls),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)