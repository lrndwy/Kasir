# Kasir

## Installasi

1. Download project ini dari github,
2. Buka terminal dan arahkan ke folder project ini menggunakan command prompt
3. Buat virtual environment dengan command berikut:

```bash
python -m venv venv
```

4. Install requirements.txt dengan command berikut:

```bash
pip install -r requirements.txt
```

5. Aktifkan virtual environment dengan command berikut:

```bash
.\venv\Scripts\activate
```

6. Migrate database dengan command berikut:

```bash
python manage.py makemigrations
python manage.py migrate
```

7. Buat super user dengan command berikut:

```bash
python manage.py createsuperuser
```

8. Jalankan server dengan command berikut:

```bash
python manage.py runserver
```

## Penggunaan

1. Buka browser dan arahkan ke http://127.0.0.1:8000
2. Login dengan username dan password yang sudah di sediakan
3. Selamat menggunakan aplikasi ini
