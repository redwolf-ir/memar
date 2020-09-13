from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^begin_password_reset/$(?i)', views.password_reset, name='password_reset'),
]