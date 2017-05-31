from django.contrib import admin

# Register your models here.

from .models import Project
from .models import File
from .models import Bear

admin.site.register(Project)
admin.site.register(File)
admin.site.register(Bear)
