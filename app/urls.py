from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from main.views import IndexPageView, ChangeLanguageView , MessagesView , ProfileView , ConnectionsView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', IndexPageView.as_view(), namespace='index'),
    path('profile/', ProfileView.as_view(), namespace='profile'),
    path('messages/', MessagesView.as_view(), namespace='messages'),
    path('connections/', ConnectionsView.as_view(), namespace='connections'),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/', ChangeLanguageView.as_view(), namespace='change_language'),

    path('accounts/', include('accounts.urls')),
    path('django_messages/', include('django_messages.urls'), namespace="django_messages"),
    path('connection/', include('connection.urls') , namespace="connection"),
    path('quickbooks/', include('quickbooks.urls') , namespace="quickbooks"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
