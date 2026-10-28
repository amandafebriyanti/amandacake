from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_amandacake_super_aman'

# --- DATABASE SEMENTARA ---
database_akun = {"amandafebriyanti": "12345"}

data_profil = {
    "amandafebriyanti": {
        "nama_lengkap": "Amanda Febriyanti",
        "email": "amanda@email.com",
        "telepon": "081234567890",
        "alamat": "Jl. Sultan Alauddin No. 259, Makassar, Sulawesi Selatan"
    }
}

keranjang_belanja = {}
daftar_favorit = {}
riwayat_pesanan = {} # BARU: Untuk menyimpan riwayat pesanan setelah checkout!

# --- DATA MENU ---
data_menu = {
    "kue_tar": [
        {"id": 1, "nama": "Red Velvet Classic", "harga": "Rp 150.000", "deskripsi": "Lapisan krim keju lembut.", "gambar": "Redvelvet.jpg", "rating": "4.9", "terjual": "1,2RB"},
        {"id": 2, "nama": "Chocolate Garnist", "harga": "Rp 175.000", "deskripsi": "Cokelat lezat tekstur lembut.", "gambar": "Chocolate.jpg", "rating": "5.0", "terjual": "5,3RB"},
        {"id": 3, "nama": "Vanilla Rainbow", "harga": "Rp 160.000", "deskripsi": "Vanila ceria warna-warni.", "gambar": "Rainbow.jpg", "rating": "4.7", "terjual": "540"},
        {"id": 4, "nama": "Strawberry Chocolate", "harga": "Rp 175.000", "deskripsi": "Sentuhan stroberi segar.", "gambar": "Strawberry.jpg", "rating": "5.0", "terjual": "2,1RB"},
        {"id": 5, "nama": "Blueberry Vanilla", "harga": "Rp 175.000", "deskripsi": "Selai blueberry pilihan.", "gambar": "Blueberry.jpg", "rating": "4.6", "terjual": "320"},
        {"id": 6, "nama": "Matcha Green Tea", "harga": "Rp 170.000", "deskripsi": "Teh hijau khas Jepang.", "gambar": "Matcha.jpg", "rating": "4.8", "terjual": "980"},
        {"id": 7, "nama": "Banana Chocolate", "harga": "Rp 165.000", "deskripsi": "Rasa piang yang manis dipadukan dengan coklat yang kaya", "gambar": "Banana", "rating": "4,7", "terjual": "890"},
        {"id": 8, "nama": "Mango Vanilla", "harga": "Rp 170.000", "deskripsi": "Mangga yang manis dan segar dipadukan dengan vanila yang lembut.", "gambar": "Mango", "rating": "4,8", "terjual": "760"},
        {"id": 9, "nama": "Chocolate Mint", "harga": "Rp 170.000", "deskripsi": "Cokelat manis dengan sensasi mint yang segar.", "gambar": "Tiramisu", "rating": "4,8", "terjual": "1,2RB"},
        {"id": 10, "nama": "Blueberry", "harga": "Rp 165.000", "deskripsi": "Rasa buah beri yang manis dan sedikit asam.", "gambar": "Blueberry", "rating": "4,7", "terjual": "670"}
    ],
    "kue_kering": [
        {"id": 11, "nama": "Nastar Klasik", "harga": "Rp 90.000", "deskripsi": "Selai nanas asli di dalam.", "gambar": "Chocolate.jpg", "rating": "5.0", "terjual": "5,4RB"},
        {"id": 12, "nama": "Castengels Spesial", "harga": "Rp 80.000", "deskripsi": "Taburan keju Edam melimpah.", "gambar": "Chocolate.jpg", "rating": "4.9", "terjual": "3,2RB"},
        {"id": 13, "nama": "Putri Salju", "harga": "Rp 75.000", "deskripsi": "Kue manis bertabur gula halus.", "gambar": "Salju.jpg", "rating": "4.8", "terjual": "1,2RB"},
        {"id": 14, "nama": "Chocolate Chip Cookies", "harga": "Rp 75.000", "deskripsi": "Cookies dengan taburan cokelat.", "gambar": "Cookies.jpg", "rating": "5.0", "terjual": "3,2RB"},
        {"id": 15, "nama": "Matcha Cookies", "harga": "Rp 80.000", "deskripsi": "Rasa teh hijau yang khas.", "gambar": "Matcha.jpg", "rating": "4.9", "terjual": "2,4RB"},
        {"id": 16, "nama": "Palmier", "harga": "Rp 70.000", "deskripsi": "Renyah dengan lapisan karamel.", "gambar": "Palmier.jpg", "rating": "4.6", "terjual": "1,3RB"}
    ],
    "puding": [
        {"id": 17, "nama": "Puding Cokelat Vla", "harga": "Rp 45.000", "deskripsi": "Vla vanila creamy.", "gambar": "Vla.jpg", "rating": "5.0", "terjual": "4,1RB"},
        {"id": 18, "nama": "Puding Buah Segar", "harga": "Rp 50.000", "deskripsi": "Topping aneka buah segar.", "gambar": "Buah.jpg", "rating": "4.8", "terjual": "2,5RB"},
        {"id": 19, "nama": "Puding Lumut", "harga": "Rp 35.000", "deskripsi": "Puding pandan dengan motif lumut yang unik.", "gambar": "Lumut.jpg", "rating": "4.6", "terjual": "795"},
        {"id": 20, "nama": "Tiramisu", "harga": "Rp 50.000", "deskripsi": "Puding rasa kopi dan krim dengan taburan cokelat.", "gambar": "Tiramisu.jpg", "rating": "4.8", "terjual": "2,5RB"}
    ]
}
semua_produk = data_menu["kue_tar"] + data_menu["kue_kering"] + data_menu["puding"]

# FUNGSI GLOBAL BADGE KERANJANG
@app.context_processor
def inject_cart_count():
    count = 0
    if 'username' in session:
        user = session['username']
        count = sum(item['qty'] for item in keranjang_belanja.get(user, []))
    return dict(cart_count=count)

# --- ROUTE OTENTIKASI ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user in database_akun and database_akun[user] == pwd:
            session['username'] = user
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Username atau password salah!")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user in database_akun:
            return render_template('register.html', pesan="Username sudah terdaftar!")
        if user and pwd:
            database_akun[user] = pwd
            data_profil[user] = {"nama_lengkap": user, "email": "", "telepon": "", "alamat": ""}
            flash("Akun berhasil dibuat! Silakan login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --- ROUTE HALAMAN UTAMA ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    keyword = request.args.get('q', '').lower()
    produk_tampil = semua_produk
    judul = "Rekomendasi Spesial"
    if keyword:
        produk_tampil = [p for p in semua_produk if keyword in p['nama'].lower()]
        judul = f"Hasil Pencarian: '{keyword}'"
    return render_template('katalog.html', produk=produk_tampil, judul=judul, keyword=keyword)

@app.route('/kue-tar')
def route_kue_tar():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('katalog.html', produk=data_menu["kue_tar"], judul="Kue Tar Pilihan")

@app.route('/kue-kering')
def route_kue_kering():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('katalog.html', produk=data_menu["kue_kering"], judul="Kue Kering Spesial")

@app.route('/puding')
def route_puding():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('katalog.html', produk=data_menu["puding"], judul="Puding Lembut & Segar")

@app.route('/detail/<nama_kue>')
def detail(nama_kue):
    if 'username' not in session: return redirect(url_for('login'))
    produk_detail = next((p for p in semua_produk if p['nama'] == nama_kue), None)
    return render_template('detail.html', produk=produk_detail)

# --- ROUTE TRANSAKSI & KERANJANG ---
@app.route('/beli-langsung/<nama_kue>')
def beli_langsung(nama_kue):
    if 'username' not in session: return redirect(url_for('login'))
    tambah_keranjang(nama_kue, redirect_back=False)
    return redirect(url_for('checkout'))

@app.route('/tambah-keranjang/<nama_kue>', methods=['GET'])
def tambah_keranjang(nama_kue, redirect_back=True):
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    if user not in keranjang_belanja: keranjang_belanja[user] = []
    
    ditemukan = False
    for item in keranjang_belanja[user]:
        if item['nama'] == nama_kue:
            item['qty'] += 1
            ditemukan = True
            break
            
    if not ditemukan:
        for p in semua_produk:
            if p['nama'] == nama_kue:
                item_baru = p.copy()
                item_baru['qty'] = 1
                keranjang_belanja[user].append(item_baru)
                break
                
    flash(f"✅ {nama_kue} dimasukkan ke keranjang!", "success")
    if redirect_back: return redirect(request.referrer or url_for('dashboard'))

@app.route('/tambah-custom/<nama_kue>', methods=['POST'])
def tambah_custom(nama_kue):
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    try: qty_pilih = int(request.form.get('qty', 1))
    except ValueError: qty_pilih = 1
    action = request.form.get('action')
    
    if user not in keranjang_belanja: keranjang_belanja[user] = []
    
    ditemukan = False
    for item in keranjang_belanja[user]:
        if item['nama'] == nama_kue:
            item['qty'] += qty_pilih
            ditemukan = True
            break
            
    if not ditemukan:
        for p in semua_produk:
            if p['nama'] == nama_kue:
                item_baru = p.copy()
                item_baru['qty'] = qty_pilih
                keranjang_belanja[user].append(item_baru)
                break
                
    flash(f"✅ {qty_pilih}x {nama_kue} berhasil ditambahkan!", "success")
    if action == 'beli': return redirect(url_for('checkout'))
    return redirect(url_for('detail', nama_kue=nama_kue))

@app.route('/keranjang')
def keranjang():
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    keranjang_user = keranjang_belanja.get(user, [])
    total_harga = sum([int(item['harga'].replace('Rp ', '').replace('.', '')) * item['qty'] for item in keranjang_user])
    total_format = f"Rp {total_harga:,}".replace(',', '.')
    return render_template('keranjang.html', keranjang=keranjang_user, total=total_format)

@app.route('/kurang-qty/<nama_kue>')
def kurang_qty(nama_kue):
    user = session.get('username')
    if user in keranjang_belanja:
        for item in keranjang_belanja[user]:
            if item['nama'] == nama_kue:
                if item['qty'] > 1: item['qty'] -= 1
                else: keranjang_belanja[user].remove(item)
                break
    return redirect(url_for('keranjang'))

@app.route('/hapus-keranjang/<nama_kue>')
def hapus_keranjang(nama_kue):
    user = session.get('username')
    if user in keranjang_belanja:
        keranjang_belanja[user] = [item for item in keranjang_belanja[user] if item['nama'] != nama_kue]
        flash(f"🗑️ {nama_kue} dihapus dari keranjang.", "success")
    return redirect(url_for('keranjang'))

@app.route('/tambah-favorit/<nama_kue>')
def tambah_favorit(nama_kue):
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    if user not in daftar_favorit: daftar_favorit[user] = []
    for p in semua_produk:
        if p['nama'] == nama_kue and p not in daftar_favorit[user]:
            daftar_favorit[user].append(p)
            flash(f"❤️ {nama_kue} ditambahkan ke Favorit!", "success")
            break
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/favorit')
def favorit():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('favorit.html', favorit=daftar_favorit.get(session['username'], []))

# --- ROUTE CHECKOUT (DIPERBARUI) ---
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    keranjang_user = keranjang_belanja.get(user, [])
    
    # Hitung total harga
    total_harga = sum([int(item['harga'].replace('Rp ', '').replace('.', '')) * item['qty'] for item in keranjang_user])
    total_format = f"Rp {total_harga:,}".replace(',', '.')
    
    profil_user = data_profil.get(user, {})
    
    if request.method == 'POST':
        if user not in riwayat_pesanan:
            riwayat_pesanan[user] = []
            
        metode_bayar = request.form.get('metode')
        
        pesanan_baru = {
            "tanggal": datetime.now().strftime("%d %b %Y, %H:%M"),
            "items": keranjang_belanja[user].copy(),
            "total": total_format,
            "metode": metode_bayar
        }
        riwayat_pesanan[user].append(pesanan_baru)
        keranjang_belanja[user] = [] # Kosongkan keranjang setelah beli
        
        # BARU: Mengirim data total belanja dan metode ke halaman sukses!
        return render_template('sukses.html', 
                               nama=request.form.get('nama'), 
                               alamat=request.form.get('alamat'), 
                               metode=metode_bayar,
                               total=total_format)
        
    return render_template('checkout.html', keranjang=keranjang_user, total=total_format, profil=profil_user)

# --- ROUTE PROFIL & FITUR BARU ---
@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    if request.method == 'POST':
        data_profil[user]['nama_lengkap'] = request.form.get('nama_lengkap')
        data_profil[user]['email'] = request.form.get('email')
        data_profil[user]['telepon'] = request.form.get('telepon')
        data_profil[user]['alamat'] = request.form.get('alamat')
        flash("✅ Profil & Alamat berhasil disimpan!", "success")
        return redirect(url_for('profil'))
    return render_template('profil.html', user=user, profil=data_profil.get(user))

# BARU: ROUTE UBAH PASSWORD
@app.route('/ubah-password', methods=['GET', 'POST'])
def ubah_password():
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    if request.method == 'POST':
        pass_lama = request.form.get('pass_lama')
        pass_baru = request.form.get('pass_baru')
        pass_konfirmasi = request.form.get('pass_konfirmasi')

        if database_akun.get(user) != pass_lama:
            flash("❌ Password lama yang Anda masukkan salah!", "error")
        elif pass_baru != pass_konfirmasi:
            flash("❌ Konfirmasi password baru tidak cocok!", "error")
        else:
            database_akun[user] = pass_baru
            flash("✅ Password berhasil diubah!", "success")
            
        return redirect(url_for('ubah_password'))
    return render_template('ubah_password.html', user=user)

# BARU: ROUTE PESANAN SAYA
@app.route('/pesanan')
def pesanan():
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    daftar_pesanan = riwayat_pesanan.get(user, [])
    # Dibalik (reverse) agar pesanan terbaru ada di paling atas
    return render_template('pesanan.html', user=user, pesanan=reversed(daftar_pesanan))

if __name__ == '__main__':
    app.run(debug=True)