import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# KODE UNTUK MENYEMBUNYIKAN MENU & TOMBOL STREAMLIT
# ==========================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# MENYEMBUNYIKAN LOGO / MENU BAWAAN STREAMLIT
# ==========================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# PENGATURAN UTAMA HALAMAN WEB
# ==========================================
st.title("Manajemen ZIS BAZNAS")
st.write("Formulir Input Data Muzaki & Transaksi")

# ==========================================
# KONEKSI & STRUKTUR DATABASE
# ==========================================
conn = sqlite3.connect('database_baznas.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS muzaki (
        id_muzaki TEXT PRIMARY KEY,
        nama_lengkap TEXT,
        no_hp TEXT,
        segment TEXT,
        alamat TEXT,
        kategori TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaksi (
        id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
        id_muzaki TEXT,
        tanggal TEXT,
        nominal INTEGER,
        jenis_dana TEXT,
        program TEXT,
        kanal TEXT,
        bukti_donasi TEXT,
        status_ucapan TEXT,
        status_laporan TEXT,
        catatan TEXT
    )
''')
conn.commit()

# ==========================================
# FORMULIR INPUT DATA BARU (STREAMLIT UI)
# ==========================================
with st.form("form_muzaki_lengkap"):
    st.subheader("➕ Tambah Data Baru")
    
    col1, col2 = st.columns(2)
    
    with col1:
        id_muzaki = st.text_input("ID Muzaki", value="MZK-004")
        nama_lengkap = st.text_input("Nama Lengkap", placeholder="Nama Muzaki")
        no_hp = st.text_input("No HP", placeholder="08...")
        segment = st.selectbox("Segment", ['Ritel', 'Besar', 'Komunitas', 'Korporate', 'Pekurban', 'Donatur Ramadhan', 'Muzaki', 'Relawan Donatur'])
        alamat = st.text_area("Alamat", placeholder="Alamat lengkap")
        tanggal = st.text_input("Tanggal", value="2026/07/23")
        
    with col2:
        kategori = st.selectbox("Kategori", ['Individu', 'Perusahaan', 'Lembaga'])
        jenis_dana = st.selectbox("Jenis Dana", ['Zakat', 'Infak', 'Sedekah', 'CSR', 'Kurban', 'Dana Terikat', 'Dana Amil', 'DSKL'])
        nominal = st.number_input("Nominal (Rp)", min_value=0, step=10000)
        
        # Format Rupiah Otomatis
        format_str = f"Rp {nominal:,.0f}".replace(",", ".")
        st.markdown(f"**Format Rupiah:** <span style='color: green;'>{format_str}</span>", unsafe_allow_html=True)
        
        program = st.selectbox("Program", ['Pendidikan', 'Kesehatan', 'Ekonomi Produktif', 'Konsumtif', 'Bencana', 'Ramadhan', 'Kurban', 'Zakat Maal', 'Zakat Fitrah', 'Lainnya'])
        kanal = st.selectbox("Kanal", ['WhatsApp', 'Media Sosial', 'Website', 'QRIS', 'Transfer Bank', 'Event', 'Patrol', 'CSR', 'Komunitas/Masjid', 'Referral', 'Walk-In'])

    bukti_donasi = st.text_input("Bukti Donasi", placeholder="Link / Keterangan Bukti")
    
    col3, col4 = st.columns(2)
    with col3:
        status_ucapan = st.selectbox("Status Ucapan", ['Belum Terkirim', 'Terkirim'])
    with col4:
        status_laporan = st.selectbox("Status Laporan", ['Belum Terkirim', 'Terkirim'])
        
    catatan = st.text_area("Catatan", placeholder="Catatan tambahan...")

    submit_button = st.form_submit_button(label="Simpan Data")

    if submit_button:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO muzaki (id_muzaki, nama_lengkap, no_hp, segment, alamat, kategori)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id_muzaki, nama_lengkap, no_hp, segment, alamat, kategori))
            
            cursor.execute('''
                INSERT INTO transaksi (
                    id_muzaki, tanggal, nominal, jenis_dana, program, 
                    kanal, bukti_donasi, status_ucapan, status_laporan, catatan
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_muzaki, tanggal, nominal, jenis_dana, program, 
                kanal, bukti_donasi, status_ucapan, status_laporan, catatan
            ))
            
            conn.commit()
            st.success(f"Sukses! Data untuk {nama_lengkap} berhasil disimpan ke database.")
            st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# ==========================================
# LAPORAN, PENCARIAN, EDIT & HAPUS DATA
# ==========================================
st.divider()
st.subheader("📊 Laporan Transaksi & Rekapitulasi")

# --- FITUR PENCARIAN ---
keyword_cari = st.text_input("🔍 Cari Data (Berdasarkan Nama, ID, atau Jenis Dana):")

# Mengambil data lengkap dari database
query_laporan = '''
    SELECT 
        transaksi.id_transaksi,
        transaksi.tanggal, 
        muzaki.id_muzaki,
        muzaki.nama_lengkap, 
        muzaki.kategori,
        transaksi.jenis_dana, 
        transaksi.nominal,
        transaksi.program,
        transaksi.kanal,
        transaksi.catatan
    FROM transaksi
    JOIN muzaki ON transaksi.id_muzaki = muzaki.id_muzaki
    ORDER BY transaksi.tanggal DESC
'''

df_laporan = pd.read_sql_query(query_laporan, conn)

if not df_laporan.empty:
    # Filter data jika kotak pencarian diisi
    if keyword_cari:
        df_filtered = df_laporan[
            df_laporan['nama_lengkap'].str.contains(keyword_cari, case=False, na=False) |
            df_laporan['id_muzaki'].str.contains(keyword_cari, case=False, na=False) |
            df_laporan['jenis_dana'].str.contains(keyword_cari, case=False, na=False)
        ]
    else:
        df_filtered = df_laporan

    # Format Rupiah untuk tampilan tabel
    df_filtered_display = df_filtered.copy()
    df_filtered_display['nominal_format'] = df_filtered_display['nominal'].apply(lambda x: f"Rp {x:,.0f}")
    
    # Menampilkan Tabel Laporan
    st.dataframe(df_filtered_display[['id_transaksi', 'tanggal', 'id_muzaki', 'nama_lengkap', 'kategori', 'jenis_dana', 'nominal_format']])

    # --- FITUR KELOLA DATA (EDIT & HAPUS BERDASARKAN ID TRANSAKSI) ---
    st.markdown("### ⚙️ Kelola Data (Edit atau Hapus Transaksi)")
    
    list_id_transaksi = df_laporan['id_transaksi'].tolist()
    id_pilih = st.selectbox("Pilih ID Transaksi yang akan diedit/dihapus:", list_id_transaksi)
    
    if id_pilih:
        # Ambil data spesifik berdasarkan ID Transaksi yang dipilih
        data_terpilih = df_laporan[df_laporan['id_transaksi'] == id_pilih].iloc[0]
        
        with st.form("form_edit_data"):
            st.write(f"**Edit Data untuk ID Transaksi: {id_pilih}**")
            
            edit_tanggal = st.text_input("Tanggal", value=str(data_terpilih['tanggal']))
            edit_nominal = st.number_input("Nominal (Rp)", value=int(data_terpilih['nominal']), min_value=0, step=10000)
            
            # Pilihan Jenis Dana
            list_jenis_dana = ['Zakat', 'Infak', 'Sedekah', 'CSR', 'Kurban', 'Dana Terikat', 'Dana Amil', 'DSKL']
            idx_jenis = list_jenis_dana.index(data_terpilih['jenis_dana']) if data_terpilih['jenis_dana'] in list_jenis_dana else 0
            edit_jenis_dana = st.selectbox("Jenis Dana", list_jenis_dana, index=idx_jenis)
            
            edit_catatan = st.text_area("Catatan", value=str(data_terpilih['catatan']) if data_terpilih['catatan'] else "")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                tombol_update = st.form_submit_button("💾 Simpan Perubahan (Edit)")
            with col_btn2:
                tombol_hapus = st.form_submit_button("🗑️ Hapus Data Ini")
                
            if tombol_update:
                try:
                    cursor.execute('''
                        UPDATE transaksi 
                        SET tanggal = ?, nominal = ?, jenis_dana = ?, catatan = ?
                        WHERE id_transaksi = ?
                    ''', (edit_tanggal, edit_nominal, edit_jenis_dana, edit_catatan, id_pilih))
                    conn.commit()
                    st.success(f"Data transaksi ID {id_pilih} berhasil diperbarui!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal mengedit data: {e}")
                    
            if tombol_hapus:
                try:
                    cursor.execute("DELETE FROM transaksi WHERE id_transaksi = ?", (id_pilih,))
                    conn.commit()
                    st.success(f"Data transaksi ID {id_pilih} berhasil dihapus!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus data: {e}")

    # Rekapitulasi Total Dana Masuk
    st.markdown("### 📈 Total Pemasukan Berdasarkan Jenis Dana")
    summary_dana = df_filtered.groupby('jenis_dana')['nominal'].sum().reset_index()
    summary_dana['Total (Rp)'] = summary_dana['nominal'].apply(lambda x: f"Rp {x:,.0f}")
    
    st.dataframe(summary_dana[['jenis_dana', 'Total (Rp)']])
else:
    st.info("Belum ada data transaksi yang tersimpan.")
