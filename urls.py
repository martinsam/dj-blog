from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # admin
    (r'^admin/', include(admin.site.urls)),

    # blog
    (r'^blog/', include('blog.urls')),

)
