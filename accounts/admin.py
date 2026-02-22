from django.contrib import admin
from .models import CustomUser, Roles, PasswordStorage, ErrorLog

admin.site.register(CustomUser)
admin.site.register(Roles)
admin.site.register(PasswordStorage)
admin.site.register(ErrorLog)