from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from main.views import IndexPageView, ChangeLanguageView , MessagesView , ProfileView , ConnectionsView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', IndexPageView.as_view(), name='index'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('connections/', ConnectionsView.as_view(), name='connections'),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/', ChangeLanguageView.as_view(), name='change_language'),

    path('accounts/', include('accounts.urls')),
    path('django_messages/', include('django_messages.urls'), name="django_messages"),
    path('connection/', include('connection.urls') , name="connection"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
