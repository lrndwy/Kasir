from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, time
from .models import Barang, Transaksi, DetailTransaksi
from decimal import Decimal

# Decorator untuk mengecek apakah user adalah superuser
def superuser_required(function):
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url='login'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, 'Login berhasil!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah atau bukan superuser!')
            
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Berhasil logout!')
    return redirect('login')

@superuser_required
def dashboard(request):
    # Get today's date range
    today = timezone.now().date()
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)
    
    # Calculate statistics
    transaksi_hari_ini = Transaksi.objects.filter(
        waktu__range=(today_start, today_end),
        selesai=True
    ).count()
    
    pendapatan_hari_ini = Transaksi.objects.filter(
        waktu__range=(today_start, today_end),
        selesai=True
    ).aggregate(total=Sum('total_harga'))['total'] or 0
    
    total_barang = Barang.objects.count()
    
    # Anggap stok menipis jika kurang dari 10
    BATAS_STOK_MENIPIS = 10
    stok_menipis = Barang.objects.filter(stok__lt=BATAS_STOK_MENIPIS).count()
    
    # Get items with low stock
    barang_menipis = Barang.objects.filter(
        stok__lt=BATAS_STOK_MENIPIS
    ).order_by('stok')[:5]  # Tampilkan 5 barang dengan stok paling sedikit
    
    # Get recent transactions
    transaksi_terakhir = Transaksi.objects.filter(
        selesai=True
    ).order_by('-waktu')[:5]  # Tampilkan 5 transaksi terakhir
    
    context = {
        'transaksi_hari_ini': transaksi_hari_ini,
        'pendapatan_hari_ini': pendapatan_hari_ini,
        'total_barang': total_barang,
        'stok_menipis': stok_menipis,
        'barang_menipis': barang_menipis,
        'transaksi_terakhir': transaksi_terakhir,
    }
    
    return render(request, 'kasir/dashboard.html', context)

@superuser_required
def kelola_barang(request):
    barang_list = Barang.objects.all()
    barang_edit = None
    
    # Handle Edit Mode
    if 'edit' in request.GET:
        barang_edit = get_object_or_404(Barang, id=request.GET['edit'])
    
    # Handle POST requests (Create, Update, Delete)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Create new barang
            try:
                Barang.objects.create(
                    nama=request.POST['nama'],
                    harga=request.POST['harga'],
                    stok=request.POST['stok']
                )
                messages.success(request, 'Barang berhasil ditambahkan!')
            except Exception as e:
                messages.error(request, f'Gagal menambahkan barang: {str(e)}')
                
        elif action == 'edit':
            # Update existing barang
            try:
                barang = get_object_or_404(Barang, id=request.POST['barang_id'])
                barang.nama = request.POST['nama']
                barang.harga = request.POST['harga']
                barang.stok = request.POST['stok']
                barang.save()
                messages.success(request, 'Barang berhasil diupdate!')
                return redirect('kelola_barang')
            except Exception as e:
                messages.error(request, f'Gagal mengupdate barang: {str(e)}')
                
        elif action == 'delete':
            # Delete barang
            try:
                barang = get_object_or_404(Barang, id=request.POST['barang_id'])
                barang.delete()
                messages.success(request, 'Barang berhasil dihapus!')
            except Exception as e:
                messages.error(request, f'Gagal menghapus barang: {str(e)}')
        
        return redirect('kelola_barang')
    
    context = {
        'barang_list': barang_list,
        'barang_edit': barang_edit,
    }
    
    return render(request, 'kasir/barang.html', context)

@superuser_required
def kasir(request):
    # Ambil atau buat transaksi yang sedang aktif
    transaksi_aktif = Transaksi.objects.filter(selesai=False).first()
    if not transaksi_aktif:
        transaksi_aktif = Transaksi.objects.create()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_item':
            try:
                barang = get_object_or_404(Barang, id=request.POST['barang_id'])
                kuantitas = int(request.POST['kuantitas'])
                
                # Cek stok
                if kuantitas > barang.stok:
                    messages.error(request, f'Stok tidak mencukupi! Stok tersedia: {barang.stok}')
                    return redirect('kasir')
                
                # Hitung subtotal
                subtotal = barang.harga * kuantitas
                
                # Buat detail transaksi
                DetailTransaksi.objects.create(
                    transaksi=transaksi_aktif,
                    barang=barang,
                    kuantitas=kuantitas,
                    subtotal=subtotal
                )
                
                # Update stok
                barang.stok -= kuantitas
                barang.save()
                
                # Update total transaksi
                transaksi_aktif.total_harga += subtotal
                transaksi_aktif.save()
                
                messages.success(request, 'Item berhasil ditambahkan!')
                
            except Exception as e:
                messages.error(request, f'Gagal menambahkan item: {str(e)}')
                
        elif action == 'delete_item':
            try:
                detail = get_object_or_404(DetailTransaksi, id=request.POST['item_id'])
                
                # Kembalikan stok
                detail.barang.stok += detail.kuantitas
                detail.barang.save()
                
                # Update total transaksi
                transaksi_aktif.total_harga -= detail.subtotal
                transaksi_aktif.save()
                
                # Hapus detail
                detail.delete()
                
                messages.success(request, 'Item berhasil dihapus!')
                
            except Exception as e:
                messages.error(request, f'Gagal menghapus item: {str(e)}')
                
        elif action == 'selesai':
            try:
                transaksi_aktif.selesai = True
                transaksi_aktif.save()
                messages.success(request, 'Transaksi berhasil diselesaikan!')
                return redirect('kasir')
            except Exception as e:
                messages.error(request, f'Gagal menyelesaikan transaksi: {str(e)}')
        
        return redirect('kasir')
    
    context = {
        'barang_list': Barang.objects.filter(stok__gt=0),
        'detail_transaksi': transaksi_aktif.details.all(),
        'total_harga': transaksi_aktif.total_harga,
    }
    
    return render(request, 'kasir/kasir.html', context)

@superuser_required
def history_transaksi(request):
    # Ambil semua transaksi yang sudah selesai
    transaksi_list = Transaksi.objects.filter(selesai=True).order_by('-waktu')
    
    context = {
        'transaksi_list': transaksi_list
    }
    
    return render(request, 'kasir/history.html', context)

@superuser_required
def struk(request, transaksi_id):
    # Ambil detail transaksi
    transaksi = get_object_or_404(Transaksi, id=transaksi_id)
    
    if not transaksi.selesai:
        messages.error(request, 'Transaksi belum selesai!')
        return redirect('history')
    
    context = {
        'transaksi': transaksi
    }
    
    return render(request, 'kasir/struk.html', context)
