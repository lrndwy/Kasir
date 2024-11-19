from django.db import models

class Barang(models.Model):
    nama = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.IntegerField()

    def __str__(self):
        return self.nama

class Transaksi(models.Model):
    waktu = models.DateTimeField(auto_now_add=True)
    total_harga = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selesai = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaksi {self.id} - {self.waktu}"

class DetailTransaksi(models.Model):
    transaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE, related_name='details')
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE)
    kuantitas = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.barang.nama} - {self.kuantitas}"
