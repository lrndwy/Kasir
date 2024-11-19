from django.urls import path
from apps.kasir.views import *

urlpatterns = [
	path('login/', login_view, name='login'),
	path('logout/', logout_view, name='logout'),
	path('', dashboard, name='dashboard'),
	path('barang/', kelola_barang, name='kelola_barang'),
	path('kasir/', kasir, name='kasir'),
	path('history/', history_transaksi, name='history'),
	path('struk/<int:transaksi_id>/', struk, name='struk'),
]
