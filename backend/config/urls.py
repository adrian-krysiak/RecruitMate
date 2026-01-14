from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # User authentication routes, user data
    path('auth/', include('accounts.urls')),
    # AI routes (ml_service, GenAI)
    path('advisor/', include('advisor.urls'))
]
