from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView


admin.site.site_header = "CHSBC Admin"
admin.site.site_title = "CHSBC Admin Portal"
admin.site.index_title = "Welcome To CHSBC Portal"


urlpatterns = [
    path('upload_file/', lambda request: HttpResponse('Ok'),name='upload_file'),
    # # path('', lambda request: HttpResponse('Ok'), name='home'),
    path('admin/', admin.site.urls),
    path('hub/chsbc/',include("apps.gym_hub.urls")),
    # path('hub/health_check/', lambda request: HttpResponse('Ok'),  name='health_check'),
    path('hub/', include('apps.authentication.urls')),
    path('', RedirectView.as_view(url='/hub/')),  # Redirect root URL to /hub/
    path('^celery-progress/', include('celery_progress.urls')),


]
urlpatterns += static(
    settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT
    )