from django.contrib import admin
from .models import (
    Occasion,
    Bouquet,
    BouquetOccasion,
    BouquetImage,
    Vendor,
    DeliveryPincode
)

admin.site.register(Occasion)
admin.site.register(Bouquet)
admin.site.register(BouquetOccasion)
admin.site.register(BouquetImage)
admin.site.register(Vendor)
admin.site.register(DeliveryPincode)