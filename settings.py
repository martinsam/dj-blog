import os

# DEBUG = True
# TEMPLATE_DEBUG = DEBUG
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'NAME':     'django-blog',
        'ENGINE':   'django.db.backends.mysql',
        'USER':     '',
        'PASSWORD' : '',
    }
}

ROOT_URLCONF = 'django-blog.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'blog',
    #'dilla'
)

#DICTIONARY = "/usr/share/dict/words"
#DILLA_USE_LOREM_IPSUM = False # set to True ignores dictionary
#DILLA_APPS = ['blog', 'auth']


TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
)

#DILLA_SPAMLIBS = ['my_custom_spamlib']

