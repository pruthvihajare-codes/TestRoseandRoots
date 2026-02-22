from django.contrib import admin
from .models import *

# Register all models simply
admin.site.register(Occasion)
admin.site.register(Bouquet)
admin.site.register(BouquetOccasion)
admin.site.register(BouquetImage)
admin.site.register(Vendor)
admin.site.register(DeliveryPincode)

# Print confirmation (you'll see this in the console when Django loads)
print("Masters admin registered!")