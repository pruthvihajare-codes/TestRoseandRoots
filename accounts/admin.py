from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Roles)
admin.site.register(PasswordStorage)
admin.site.register(ErrorLog)

print("Accounts admin registered!")