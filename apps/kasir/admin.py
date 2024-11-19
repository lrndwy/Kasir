from django.contrib import admin

# Register your models here.
from .models import Barang, Transaksi, DetailTransaksi

admin.site.register(Barang)
admin.site.register(Transaksi)
admin.site.register(DetailTransaksi)
