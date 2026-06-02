# ==============================================================================
# SCRIPT UTAMA: GUI DASHBOARD KTP SAMPANG DENGAN STREAMLIT
# ==============================================================================

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 

# ------------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CACHING DATA
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard KTP Sampang", page_icon="🏢", layout="wide")

@st.cache_data # Cache data agar tidak perlu load ulang setiap kali interaksi GUI
def load_data():
    df_loaded = None
    # Mencari file data KTP di direktori lokal
    for file in os.listdir('.'):
        if 'DATA PENGAMBILAN KTP' in file:
            try:
                if file.endswith('.csv'):
                    df_loaded = pd.read_csv(file, header=2)
                else:
                    df_loaded = pd.read_excel(file, header=2)
                break
            except Exception as e:
                st.error(f"Gagal memproses file {file}. Detail: {e}")
                
    if df_loaded is not None:
        df_loaded.columns = df_loaded.columns.str.strip()
        if 'Tanggal Pengambilan' in df_loaded.columns:
            df_loaded = df_loaded.rename(columns={'Tanggal Pengambilan': 'Tanggal'})
        
        # Konversi tipe data dan hapus NaN
        df_loaded['Tanggal'] = pd.to_datetime(df_loaded['Tanggal'], errors='coerce')
        df_loaded = df_loaded.dropna(subset=['Tanggal', 'Desa', 'Kecamatan'])
        return df_loaded
    return None

df = load_data()

# ------------------------------------------------------------------------------
# 2. HELPER FUNGSI STATISTIK
# ------------------------------------------------------------------------------
def hitung_deskriptif(data_target, total_global):
    if len(data_target) == 0:
        return None
    
    return {
        'total': len(data_target),
        'variasi_desa': data_target['Desa'].nunique(),
        'variasi_kec': data_target['Kecamatan'].nunique(),
        'hari_unik': data_target['Tanggal'].dt.date.nunique(),
        'desa_modus': data_target['Desa'].mode().iloc[0] if not data_target['Desa'].empty else "-",
        'kec_modus': data_target['Kecamatan'].mode().iloc[0] if not data_target['Kecamatan'].empty else "-",
        'persentase': (len(data_target) / total_global) * 100 if total_global > 0 else 0
    }

# ------------------------------------------------------------------------------
# 3. HEADER GUI & NAVIGASI SIDEBAR
# ------------------------------------------------------------------------------
# Sidebar untuk Navigasi (Pengganti tombol widget)
st.sidebar.title("🧭 Navigasi Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["Menu Utama (Overview)", "Filter Data (Periode)", "Cari Data (Harian)"])

# --- KODE TAMBAHAN UNTUK LOGO (AMAN & AMAN DARI ERROR) ---
# Membuat susunan grid layout: Kolom 1 (Logo 1), Kolom 2 (Judul Teks Tengah), Kolom 3 (Logo 2)
logo_col1, title_col, logo_col2 = st.columns([1, 4, 1])

with logo_col1:
    if os.path.exists("logo_unesa.png"):
        st.image("logo_unesa.png", width=100)
    else:
        st.caption("⚠️ logo_unesa.png tidak ditemukan")

with title_col:
    # Header Utama berupa teks diposisikan di tengah
    st.markdown("""
        <h2 style='text-align: center; color: #0f172a; margin-top: 0px;'>Dashboard Visualisasi Pengambilan Kartu Tanda Penduduk (KTP)</h2>
        <h4 style='text-align: center; color: #475569; margin-bottom: 10px;'>Dinas Kependudukan dan Pencatatan Sipil Kabupaten Sampang</h4>
    """, unsafe_allow_html=True)

with logo_col2:
    if os.path.exists("logo_sampang.png"):
        # use_container_width=False dan width diatur manual agar ukuran stabil teratur
        st.image("logo_sampang.png", width=90) 
    else:
        st.caption("⚠️ logo_sampang.png tidak ditemukan")

# Garis pembatas horizontal di bawah susunan header
st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)
# -------------------------------------------------------------

if df is None:
    st.error("❌ PERINGATAN CRITICAL: File 'DATA PENGAMBILAN KTP' belum terdeteksi di direktori folder!")
    st.stop()

total_keseluruhan = len(df)

# ------------------------------------------------------------------------------
# 4. LOGIKA HALAMAN MENU UTAMA
# ------------------------------------------------------------------------------
if menu == "Menu Utama (Overview)":
    st.markdown("### 📊 Statistik Keseluruhan")
    
    # [KODE TAMBAHAN] CSS untuk mencegah teks terpotong (Gunung Se...) pada metric card
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
            white-space: normal !important;
            word-wrap: break-word !important;
        }
        </style>
    """, unsafe_allow_html=True)

    kec_counts = df['Kecamatan'].value_counts()
    desa_counts = df['Desa'].value_counts()
    date_counts = df['Tanggal'].value_counts()
    
   # # Render KPI Cards menggunakan HTML/CSS - Teks Lebih Besar & Dilengkapi Panah Indikator
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #E3F2FD; padding: 12px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <h5 style="color: #1565C0; margin: 0px 0px 6px 0px; font-size: 17px; font-weight: bold;">Grand Total KTP</h5>
            <h2 style="color: #0D47A1; margin: 0px; font-size: 32px; font-weight: 900;">{total_keseluruhan:,}</h2>
            <p style="color: #1e3a8a; font-size: 15px; font-weight: 600; margin: 6px 0px 0px 0px;">🔹 Keseluruhan Data</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        top_kec = kec_counts.index[0] if not kec_counts.empty else "-"
        kec_val = kec_counts.iloc[0] if not kec_counts.empty else 0
        st.markdown(f"""
        <div style="background-color: #E8F5E9; padding: 12px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <h5 style="color: #2E7D32; margin: 0px 0px 6px 0px; font-size: 17px; font-weight: bold;">Pusat Teraktif (Kec)</h5>
            <h2 style="color: #1B5E20; margin: 0px; font-size: 26px; font-weight: 900; line-height: 1.2;">{top_kec}</h2>
            <p style="color: #15803d; font-size: 15px; font-weight: 600; margin: 6px 0px 0px 0px;">▲ {kec_val} Pengambilan</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        top_desa = desa_counts.index[0] if not desa_counts.empty else "-"
        desa_val = desa_counts.iloc[0] if not desa_counts.empty else 0
        st.markdown(f"""
        <div style="background-color: #FFF3E0; padding: 12px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <h5 style="color: #E65100; margin: 0px 0px 6px 0px; font-size: 17px; font-weight: bold;">Titik Terpadat (Desa)</h5>
            <h2 style="color: #BF360C; margin: 0px; font-size: 24px; font-weight: 900; line-height: 1.2;">{top_desa}</h2>
            <p style="color: #b45309; font-size: 15px; font-weight: 600; margin: 6px 0px 0px 0px;">▲ {desa_val} Pengambilan</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        if not date_counts.empty:
            peak_dt = date_counts.index[0]
            hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            nama_hari = hari_indo[peak_dt.weekday()]
            peak_date_str = f"{nama_hari}, {peak_dt.strftime('%d-%m-%Y')}"
            peak_val = date_counts.iloc[0]
        else:
            peak_date_str = "-"
            peak_val = 0
            
        st.markdown(f"""
        <div style="background-color: #F3E5F5; padding: 12px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <h5 style="color: #6A1B9A; margin: 0px 0px 6px 0px; font-size: 17px; font-weight: bold;">Peak Day (Tersibuk)</h5>
            <h2 style="color: #4A148C; margin: 0px; font-size: 19px; font-weight: 900; line-height: 1.2;">{peak_date_str}</h2>
            <p style="color: #6d28d9; font-size: 15px; font-weight: 600; margin: 6px 0px 0px 0px;">▲ Lonjakan {peak_val} Jiwa</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)
    
    # ==============================================================================
    # [KODE BARU] 3 REKOMENDASI VISUALISASI EKSKLUSIF OVERVIEW (AMAN & ESTETIK)
    # ==============================================================================
    st.markdown("### 🗺️ Peta Hierarki & Analisis Kepadatan Wilayah")
    
    # --- 1. PETA HIERARKI WILAYAH (TREEMAP) ---
    st.markdown("### 🌳 1. Peta Hierarki Pengambilan KTP (Treemap)")
    
    # Menyiapkan data Treemap
    df_treemap = df.groupby(['Kecamatan', 'Desa']).size().reset_index(name='Jumlah')
    
    fig_tree = px.treemap(
        df_treemap, 
        path=[px.Constant("Total KTP"), 'Kecamatan', 'Desa'], 
        values='Jumlah',
        color='Jumlah',
        color_continuous_scale='Blues'
    )
    # Merapikan margin dan layout agar estetik
    fig_tree.update_traces(root_color="lightgrey")
    fig_tree.update_layout(margin=dict(t=20, l=10, r=10, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔥 Pola Kepadatan & Top Kontributor")
    
    # --- 2. PETA PANAS KEPADATAN (HEATMAP) ---
    st.markdown("### 🌡️ 2. Heatmap Kepadatan Harian per Kecamatan")
    
    # Heatmap sekarang dilepas dari kolom agar tampil Full Width (Lebar Penuh)
    df_heat = df.dropna(subset=['Tanggal']).copy()
    
    # Translasi nama hari dan memastikan urutan harinya paten (Senin -> Minggu)
    hari_dict = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
    df_heat['Hari_Angka'] = df_heat['Tanggal'].dt.weekday
    df_heat['Hari'] = df_heat['Hari_Angka'].map(hari_dict)
    
    # Mengumpulkan (grouping) data untuk pivot heatmap
    heatmap_data = df_heat.groupby(['Kecamatan', 'Hari']).size().reset_index(name='Jumlah')
    heatmap_pivot = heatmap_data.pivot_table(index='Kecamatan', columns='Hari', values='Jumlah', fill_value=0)
    
    # Menyortir manual nama kolom agar urut hari kalender, bukan urut abjad
    ordered_days = [h for h in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"] if h in heatmap_pivot.columns]
    heatmap_pivot = heatmap_pivot[ordered_days]
    
    fig_heat = px.imshow(
        heatmap_pivot,
        labels=dict(x="Hari Operasional", y="Kecamatan", color="Total KTP"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="YlOrRd", # Warnanya Kuning-Oranye-Merah
        aspect="auto"
    )
    # Menampilkan teks angka tebal di tengah-tengah kotak warna agar mudah dibaca
    fig_heat.update_traces(text=heatmap_pivot.values, texttemplate="%{text}", textfont=dict(color="black"))
    st.plotly_chart(fig_heat, use_container_width=True)
    
    # Garis pembatas tipis untuk memisahkan Heatmap dengan Tabel
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # --- 3. TABEL RINGKASAN EKSEKUTIF ---
    st.markdown("### 🏆 3. Ringkasan Eksekutif Wilayah Tertinggi")
    
    # Membuat 2 kolom sejajar khusus untuk meletakkan kedua tabel secara berdampingan
    col_tab_kec, col_tab_desa = st.columns(2)
    
    with col_tab_kec:
        # Tabel 1: Top 5 Kecamatan
        df_top_kec = kec_counts.reset_index().head(5)
        df_top_kec.columns = ['Kecamatan', 'Total KTP']
        df_top_kec['Persentase'] = (df_top_kec['Total KTP'] / total_keseluruhan * 100).round(1).astype(str) + '%'
        
        st.caption("📍 **Top 5 Kecamatan** Kontributor Terbesar")
        st.dataframe(df_top_kec, use_container_width=True, hide_index=True)
        
    with col_tab_desa:
        # Tabel 2: Top 5 Desa
        df_top_desa = desa_counts.reset_index().head(5)
        df_top_desa.columns = ['Desa', 'Total KTP']
        df_top_desa['Persentase'] = (df_top_desa['Total KTP'] / total_keseluruhan * 100).round(1).astype(str) + '%'
        
        st.caption("📍 **Top 5 Desa** Kontributor Terbesar")
        st.dataframe(df_top_desa, use_container_width=True, hide_index=True)

    # ==============================================================================
    # 4. VISUALISASI BARU: TREN PERTUMBUHAN KTP MINGGUAN (STACKED AREA CHART)
    # Gelombang berlapis yang menampilkan Top 5 Kecamatan dengan warna kalem
    # ==============================================================================
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🌊 4. Gelombang Dinamika Top 5 Kecamatan per Minggu")
    
    # Menyiapkan data untuk Grafik Area Mingguan
    df_minggu = df.copy()
    
    # Fungsi aman untuk mengelompokkan data ke dalam periode mingguan
    def kelompokkan_minggu(tgl_val):
        t = str(tgl_val)[:10]
        if '2026-01-19' <= t <= '2026-01-23': return 'Minggu 1'
        elif '2026-01-26' <= t <= '2026-01-30': return 'Minggu 2'
        elif '2026-02-02' <= t <= '2026-02-06': return 'Minggu 3'
        elif '2026-02-09' <= t <= '2026-02-13': return 'Minggu 4'
        elif '2026-02-16' <= t <= '2026-02-20': return 'Minggu 5'
        elif '2026-02-23' <= t <= '2026-02-27': return 'Minggu 6'
        elif '2026-03-02' <= t <= '2026-03-06': return 'Minggu 7'
        else: return 'Lainnya'
        
    df_minggu['Periode'] = df_minggu['Tanggal'].apply(kelompokkan_minggu)
    df_minggu = df_minggu[df_minggu['Periode'] != 'Lainnya'] # Buang data di luar periode
    
    # Filter HANYA Top 5 Kecamatan agar lapisan gelombang tidak terlalu padat
    top5_kec_list = df_top_kec['Kecamatan'].tolist()
    df_minggu_top5 = df_minggu[df_minggu['Kecamatan'].isin(top5_kec_list)]
    
    # Menghitung total KTP per minggu per kecamatan
    df_tren_mingguan = df_minggu_top5.groupby(['Periode', 'Kecamatan']).size().reset_index(name='Total KTP')
    
    # Membuat Grafik Area Berlapis (Stacked Area)
    fig_area = px.area(
        df_tren_mingguan, 
        x='Periode', 
        y='Total KTP',
        color='Kecamatan', # Memisahkan gelombang berdasarkan kecamatan
        title='Ombak Kontribusi Top 5 Kecamatan (Mingguan)',
        color_discrete_sequence=px.colors.qualitative.Pastel, # Menggunakan warna-warna pastel (kalem) agar tidak silau
        markers=True
    )
    
    # Membuat garisnya melengkung halus (spline)
    fig_area.update_traces(line_shape='spline')
    
    # Menyesuaikan layout, memindahkan legenda ke bawah agar grafik punya ruang lebar
    fig_area.update_layout(
        margin=dict(l=0, r=0, t=40, b=10),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.2, 
            xanchor="center", 
            x=0.5,
            title=None
        )
    )
    
    st.plotly_chart(fig_area, use_container_width=True, config={'displaylogo': False})
    # ==============================================================================
    # 5. VISUALISASI BARU: ANALISIS PROFIL & SEBARAN WILAYAH (BENTUK MELINGKAR)
    # Memecah kesan "kotak" dengan menghadirkan visualisasi bundar/gelembung
    # ==============================================================================
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🎯 5. Profil Sebaran & Beban Wilayah (Analisis Lanjutan)")

    # Membuat 2 kolom berdampingan
    col_sun, col_bub = st.columns(2)

    with col_sun:
        # --- 5.A. SUNBURST CHART (CINCIN HIERARKI) ---
        # Menyiapkan data hari dan memfilternya hanya untuk Top 5 Kecamatan agar chart rapi
        df_sun = df.dropna(subset=['Tanggal']).copy()
        hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
        df_sun['Hari'] = df_sun['Tanggal'].dt.weekday.map(hari_map)
        
        # Ambil nama Top 5 Kecamatan dari variabel yang sudah ada sebelumnya
        top5_kec_list = df_top_kec['Kecamatan'].tolist()
        df_sun_top = df_sun[df_sun['Kecamatan'].isin(top5_kec_list)]
        df_sun_group = df_sun_top.groupby(['Hari', 'Kecamatan']).size().reset_index(name='Jumlah')
        
        # Menggambar Sunburst
        fig_sun = px.sunburst(
            df_sun_group, 
            path=['Hari', 'Kecamatan'], 
            values='Jumlah',
            color='Jumlah',
            color_continuous_scale='Sunset', # Tema warna senja
            title="🍩 5.A. Cincin Distribusi (Hari vs Top Kecamatan)"
        )
        # Menampilkan teks persentase di dalam cincin
        fig_sun.update_traces(textinfo="label+percent parent")
        fig_sun.update_layout(margin=dict(t=40, l=10, r=10, b=10))
        st.plotly_chart(fig_sun, use_container_width=True, config={'displaylogo': False})

    with col_bub:
        # --- 5.B. BUBBLE CHART (GRAFIK GELEMBUNG) ---
        # Menghitung variasi jumlah desa dan total KTP per kecamatan
        df_bub = df.groupby('Kecamatan').agg(
            Total_KTP=('Desa', 'count'),
            Jumlah_Desa=('Desa', 'nunique')
        ).reset_index()
        
        # Ukuran gelembung ditentukan oleh rata-rata kepadatan per desa
        df_bub['Kepadatan_per_Desa'] = (df_bub['Total_KTP'] / df_bub['Jumlah_Desa']).round(1)
        
        # Menggambar Bubble Chart
        fig_bub = px.scatter(
            df_bub, 
            x='Jumlah_Desa', 
            y='Total_KTP', 
            size='Kepadatan_per_Desa', 
            color='Kecamatan',
            hover_name='Kecamatan',
            title="🫧 5.B. Peta Beban Wilayah (Bubble Chart)",
            size_max=45, # Memperbesar ukuran maksimal gelembung
            template="plotly_white"
        )
        # Merapikan tampilan dan menyembunyikan legend agar grafik leluasa
        fig_bub.update_layout(
            xaxis_title="Variasi Jumlah Desa Terlayani",
            yaxis_title="Total Volume KTP",
            showlegend=False, 
            margin=dict(t=40, l=10, r=10, b=10)
        )
        st.plotly_chart(fig_bub, use_container_width=True, config={'displaylogo': False})

# ------------------------------------------------------------------------------
# 5. LOGIKA HALAMAN FILTER PERIODE 
# ------------------------------------------------------------------------------
elif menu == "Filter Data (Periode)":
    st.markdown("### 📅 Analisis Berdasarkan Periode Waktu")
    st.caption("💡 Tip: Anda bisa mengunduh setiap grafik di bawah ini menjadi file gambar (.png) dengan mengarahkan kursor ke pojok kanan atas grafik lalu klik ikon 📷 (Kamera).")
    
    opsi_waktu = {
        "Keseluruhan Data (19 Jan - 6 Mar 2026)": "all",
        "Minggu 1 (19 Jan - 23 Jan 2026)": "p1",
        "Minggu 2 (26 Jan - 30 Jan 2026)": "p2",
        "Minggu 3 (02 Feb - 06 Feb 2026)": "p3",
        "Minggu 4 (09 Feb - 13 Feb 2026)": "p4",
        "Minggu 5 (16 Feb - 20 Feb 2026)": "p5",
        "Minggu 6 (23 Feb - 27 Feb 2026)": "p6",
        "Minggu 7 (02 Mar - 06 Mar 2026)": "p7"
    }
    
    pilihan_label = st.selectbox("Pilih Rentang Periode Analisis:", list(opsi_waktu.keys()))
    pilihan_id = opsi_waktu[pilihan_label]
    
    # Filter Data
    data_target = df.copy()
    if pilihan_id == "p1": data_target = df[(df['Tanggal'] >= '2026-01-19') & (df['Tanggal'] <= '2026-01-23')]
    elif pilihan_id == "p2": data_target = df[(df['Tanggal'] >= '2026-01-26') & (df['Tanggal'] <= '2026-01-30')]
    elif pilihan_id == "p3": data_target = df[(df['Tanggal'] >= '2026-02-02') & (df['Tanggal'] <= '2026-02-06')]
    elif pilihan_id == "p4": data_target = df[(df['Tanggal'] >= '2026-02-09') & (df['Tanggal'] <= '2026-02-13')]
    elif pilihan_id == "p5": data_target = df[(df['Tanggal'] >= '2026-02-16') & (df['Tanggal'] <= '2026-02-20')]
    elif pilihan_id == "p6": data_target = df[(df['Tanggal'] >= '2026-02-23') & (df['Tanggal'] <= '2026-02-27')]
    elif pilihan_id == "p7": data_target = df[(df['Tanggal'] >= '2026-03-02') & (df['Tanggal'] <= '2026-03-06')]
    
    stats = hitung_deskriptif(data_target, total_keseluruhan)
    
    if stats is None:
        st.warning("Maaf, tidak ada rekaman data pada periode waktu ini.")
    else:
        rata_rata = stats['total'] / stats['hari_unik'] if stats['hari_unik'] > 0 else 0
        
        # ==============================================================================
        # [KODE BARU] ANALISIS DESKRIPTIF & TABEL RINCIAN PRESISI (FILTER DATA)
        # ==============================================================================
        rata_rata_bulat = round(stats['total'] / stats['hari_unik']) if stats['hari_unik'] > 0 else 0

        st.markdown("### 📝 Analisis Deskriptif")
        
        # Hitung persentase untuk narasi (dibulatkan 1 angka di belakang koma)
        persentase_bulat = round(stats['persentase'], 1)
        
        # Logika kalimat persentase menyesuaikan pilihan filter
        if pilihan_id == "all":
            teks_persentase = "Ini menunjukkan **100%** data dari periode yang ada yaitu 19 Januari sampai dengan 6 Maret 2026."
        else:
            teks_persentase = f"Ini menunjukkan **{persentase_bulat}%** data dari keseluruhan."
        
        # Narasi dinamis yang sudah dilengkapi top wilayah (Kecamatan & Desa Tertinggi)
        st.info(
            f"Berdasarkan periode filter yang dipilih (**{pilihan_label}**), terdapat total **{stats['total']} KTP** yang dicetak. "
            f"{teks_persentase} Pelayanan di periode ini mencakup **{stats['variasi_desa']} variasi desa** "
            f"yang tersebar di **{stats['variasi_kec']} kecamatan** berbeda, dengan kontributor tertinggi berada di tingkat Kecamatan yaitu **{stats['kec_modus']}** dan tingkat Desa yaitu **{stats['desa_modus']}**. "
            f"Selama periode ini juga tercatat ada **{stats['hari_unik']} hari aktif** pelayanan, sehingga rata-rata volume cetak mencapai **{rata_rata_bulat} KTP per hari aktif**."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("🔍 Klik di sini untuk melihat Rincian Presisi Data"):
            col_det_kec, col_det_desa, col_det_hari = st.columns(3)
            
            with col_det_kec:
                st.markdown("**Rincian Variasi Kecamatan:**")
                df_rinci_kec = data_target['Kecamatan'].value_counts().reset_index()
                df_rinci_kec.columns = ['Kecamatan', 'Jumlah KTP']
                df_rinci_kec.index = range(1, len(df_rinci_kec) + 1)
                df_rinci_kec = df_rinci_kec.reset_index(names='No.')
                df_rinci_kec['No.'] = df_rinci_kec['No.'].astype(str)
                df_rinci_kec.loc[len(df_rinci_kec)] = ['-', 'TOTAL', stats['total']]
                st.dataframe(df_rinci_kec, hide_index=True, use_container_width=True)
                
            with col_det_desa:
                st.markdown("**Rincian Variasi Desa:**")
                df_rinci_desa = data_target['Desa'].value_counts().reset_index()
                df_rinci_desa.columns = ['Desa', 'Jumlah KTP']
                df_rinci_desa.index = range(1, len(df_rinci_desa) + 1)
                df_rinci_desa = df_rinci_desa.reset_index(names='No.')
                df_rinci_desa['No.'] = df_rinci_desa['No.'].astype(str)
                df_rinci_desa.loc[len(df_rinci_desa)] = ['-', 'TOTAL', stats['total']]
                st.dataframe(df_rinci_desa, hide_index=True, use_container_width=True)
                
            with col_det_hari:
                st.markdown("**Rincian Pelayanan Harian:**")
                
                # 1. Mengelompokkan data berdasarkan tanggal asli dari data_target
                df_rinci_hari = data_target.groupby('Tanggal').size().reset_index(name='Jumlah KTP')
                
                # 2. Proses Translate Hari & Tanggal ke Bahasa Indonesia (Aman & Presisi)
                hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                
                df_rinci_hari['Nama Hari'] = df_rinci_hari['Tanggal'].dt.weekday.map(lambda x: hari_indo[x])
                df_rinci_hari['Tgl Format'] = df_rinci_hari['Tanggal'].dt.day.astype(str) + " " + df_rinci_hari['Tanggal'].dt.month.map(lambda x: bulan_indo[x-1]) + " " + df_rinci_hari['Tanggal'].dt.year.astype(str)
                
                # 3. Menggabungkan Hari dan Tanggal ke dalam satu kolom "Tanggal"
                df_rinci_hari['Tanggal'] = df_rinci_hari['Nama Hari'] + ", " + df_rinci_hari['Tgl Format']
                
                # 4. Membuang kolom pembantu dan set penomoran baris
                df_rinci_hari = df_rinci_hari[['Tanggal', 'Jumlah KTP']]
                df_rinci_hari.index = range(1, len(df_rinci_hari) + 1)
                df_rinci_hari = df_rinci_hari.reset_index(names='No.')
                df_rinci_hari['No.'] = df_rinci_hari['No.'].astype(str)
                
                # 5. Menambahkan baris TOTAL di paling bawah tabel
                df_rinci_hari.loc[len(df_rinci_hari)] = ['-', 'TOTAL', stats['total']]
                
                # 6. Tampilkan ke dalam table dashboard
                st.dataframe(df_rinci_hari, hide_index=True, use_container_width=True)
        # ==============================================================================
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Grafik
        st.markdown("#### 📈 Visualisasi Interaktif")
        
        # Grafik 1: Tren (DIBERSIHKAN DARI FORMAT JAM 00:00)
        df_tren = data_target.groupby('Tanggal').size().reset_index(name='Jumlah').sort_values('Tanggal')
        fig_line = px.line(df_tren, x='Tanggal', y='Jumlah', title="1. Tren Dinamika Pengambilan KTP Harian", markers=True)
        # Paksa format tanggal bersih tanpa Jam
        fig_line.update_xaxes(dtick="D1", tickformat="%d %b %Y")
        st.plotly_chart(fig_line, use_container_width=True, config={'displaylogo': False})
        
        col_desa1, col_desa2 = st.columns(2)
        df_desa = data_target['Desa'].value_counts().reset_index(name='Jumlah').head(10)
        
        with col_desa1:
            fig_desa_bar = px.bar(df_desa, x='Jumlah', y='Desa', orientation='h', title="Top 10 Desa (Bar)", color_discrete_sequence=['indigo'])
            fig_desa_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_desa_bar, use_container_width=True, config={'displaylogo': False})
            
        with col_desa2:
            fig_desa_dot = go.Figure(go.Scatter(x=df_desa['Desa'], y=df_desa['Jumlah'], mode='markers', marker=dict(color='pink', size=14, line=dict(width=1.5, color='black'))))
            fig_desa_dot.update_layout(title="Top 10 Desa (Dot Plot)")
            st.plotly_chart(fig_desa_dot, use_container_width=True, config={'displaylogo': False})
            
        col_kec1, col_kec2 = st.columns(2)
        df_kec = data_target['Kecamatan'].value_counts().reset_index(name='Jumlah').head(10)
        
        with col_kec1:
            fig_kec_bar = px.bar(df_kec, x='Kecamatan', y='Jumlah', title="Top 10 Kecamatan (Bar)", color_discrete_sequence=['darkblue'])
            st.plotly_chart(fig_kec_bar, use_container_width=True, config={'displaylogo': False})
            
        with col_kec2:
            df_kec_sort = df_kec.sort_values('Kecamatan')
            fig_kec_area = px.area(df_kec_sort, x='Kecamatan', y='Jumlah', title="Top 10 Kecamatan (Area)", color_discrete_sequence=['orange'])
            st.plotly_chart(fig_kec_area, use_container_width=True, config={'displaylogo': False})

# ------------------------------------------------------------------------------
# 6. LOGIKA HALAMAN PENCARIAN HARIAN
# ------------------------------------------------------------------------------
elif menu == "Cari Data (Harian)":
    st.markdown("### 🔍 Mesin Pencarian Data Spesifik Harian")
    
    # GUI Modern Date Picker 
    tgl_input = st.date_input("Pilih Tanggal Pengambilan KTP:")
    
    if st.button("Cari Data", type="primary"):
        tgl_obj = pd.to_datetime(tgl_input)
        data_hari = df[df['Tanggal'] == tgl_obj]
        
        if len(data_hari) == 0:
            st.error("❌ Maaf data pada tanggal ini tidak tersedia, silakan cari data pada tanggal yang lain.")
        else:
            stats = hitung_deskriptif(data_hari, total_keseluruhan)
            
            # --- [KODE BARU] Translate Tanggal & Hari ke Bahasa Indonesia Manual (Aman & Anti Error) ---
            hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            
            # Mengambil nama hari dan bulan berdasarkan urutan angkanya
            nama_hari = hari_indo[tgl_obj.weekday()]
            nama_bulan = bulan_indo[tgl_obj.month - 1]
            
            # Menggabungkan hasil akhir: Contoh "Selasa, 11 Februari 2026"
            tgl_format_indo = f"{nama_hari}, {tgl_obj.day} {nama_bulan} {tgl_obj.year}"
            # -------------------------------------------------------------------------------------------
            
            # --- [PERBAIKAN KALIMAT] Memisahkan teks Desa dan Kecamatan agar tidak ambigu ---
            st.success(f"""
            ✅ **Hasil Pencarian untuk {tgl_format_indo}:**
            * Total Pengambilan: **{stats['total']} Jiwa**
            * Variasi Wilayah: **{stats['variasi_desa']} Desa** dan **{stats['variasi_kec']} Kecamatan**
            * Pusat Pengambilan Terbanyak: Untuk tingkat Desa yaitu **{stats['desa_modus']}**, sedangkan untuk tingkat Kecamatan yaitu **{stats['kec_modus']}**
            """)
            
            # 📈 KODE BARU: VISUALISASI TREN HARIAN KESELURUHAN DATA YANG MASUK
            st.markdown("#### 📈 Tren Pengambilan KTP Harian Keseluruhan")
            # Mengelompokkan seluruh data asli (df) untuk melihat tren total dari awal sampai akhir
            df_tren_total = df.groupby('Tanggal').size().reset_index(name='Jumlah').sort_values('Tanggal')
            fig_line_total = px.line(
                df_tren_total, 
                x='Tanggal', 
                y='Jumlah', 
                title="Dinamika Tren Pengambilan KTP Harian (Semua Data Masuk)", 
                markers=True,
                color_discrete_sequence=['#2563eb'] # Warna biru modern
            )
            
            # Menambahkan garis vertikal penanda posisi tanggal yang sedang dicari user
            fig_line_total.add_vline(x=tgl_obj, line_width=2, line_dash="dash", line_color="red")
            fig_line_total.add_annotation(x=tgl_obj, y=df_tren_total['Jumlah'].max(), text="Tanggal Dicari", showarrow=True, arrowhead=1, yshift=10)
            
            st.plotly_chart(fig_line_total, use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # 📊 VISUALISASI DATA TANGGAL YANG DICARI (DESA & KECAMATAN)
            st.markdown(f"#### 📊 Distribusi Wilayah pada {tgl_format_indo}") 
            
            # Grafik Desa (2 Jenis Macam)
            col_cari1, col_cari2 = st.columns(2)
            df_desa_hari = data_hari['Desa'].value_counts().reset_index(name='Jumlah')
            
            with col_cari1:
                # Jenis 1: Doughnut Chart
                fig_donut = px.pie(df_desa_hari, values='Jumlah', names='Desa', hole=0.4, title="1.A. Distribusi Desa (Doughnut)", color_discrete_sequence=px.colors.sequential.Teal)
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with col_cari2:
                # Jenis 2: Line Chart Desa
                df_desa_hari_sort = df_desa_hari.sort_values('Desa')
                fig_line_desa = px.line(df_desa_hari_sort, x='Desa', y='Jumlah', title="1.B. Volume Antar Desa (Line)", markers=True, color_discrete_sequence=['teal'])
                st.plotly_chart(fig_line_desa, use_container_width=True)
                
            # Grafik Kecamatan (2 Jenis Macam)
            col_cari3, col_cari4 = st.columns(2)
            df_kec_hari = data_hari['Kecamatan'].value_counts().reset_index(name='Jumlah').sort_values('Kecamatan')
            
            with col_cari3:
                # Jenis 1: Bar Chart Kecamatan
                fig_kec_bar = px.bar(df_kec_hari, x='Kecamatan', y='Jumlah', title="2.A. Distribusi Kecamatan (Bar)", color_discrete_sequence=['darkblue'])
                st.plotly_chart(fig_kec_bar, use_container_width=True)
                
            with col_cari4:
                # Jenis 2: Dot Plot Kecamatan
                fig_kec_dot = go.Figure(go.Scatter(x=df_kec_hari['Kecamatan'], y=df_kec_hari['Jumlah'], mode='markers', marker=dict(color='skyblue', size=13, line=dict(width=1.5, color='black'))))
                fig_kec_dot.update_layout(title="2.B. Sebaran Kecamatan (Dot Plot)")
                st.plotly_chart(fig_kec_dot, use_container_width=True)
            
            # ==============================================================================
            # 📋 TABEL RINCIAN PRESISI DENGAN BARIS 'TOTAL' (CARI DATA HARIAN)
            # ==============================================================================
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 📋 Rincian Presisi Data Wilayah")
            
            col_cari_kec_tab, col_cari_desa_tab = st.columns(2)
            
            with col_cari_kec_tab:
                st.markdown("**Rincian per Kecamatan:**")
                df_cari_kec_tab = data_hari['Kecamatan'].value_counts().reset_index()
                df_cari_kec_tab.columns = ['Kecamatan', 'Jumlah KTP']
                df_cari_kec_tab.index = range(1, len(df_cari_kec_tab) + 1)
                df_cari_kec_tab = df_cari_kec_tab.reset_index(names='No.')
                df_cari_kec_tab['No.'] = df_cari_kec_tab['No.'].astype(str)
                df_cari_kec_tab.loc[len(df_cari_kec_tab)] = ['-', 'TOTAL', stats['total']]
                st.dataframe(df_cari_kec_tab, use_container_width=True, hide_index=True)

            with col_cari_desa_tab:
                st.markdown("**Rincian per Desa:**")
                df_cari_desa_tab = data_hari['Desa'].value_counts().reset_index()
                df_cari_desa_tab.columns = ['Desa', 'Jumlah KTP']
                df_cari_desa_tab.index = range(1, len(df_cari_desa_tab) + 1)
                df_cari_desa_tab = df_cari_desa_tab.reset_index(names='No.')
                df_cari_desa_tab['No.'] = df_cari_desa_tab['No.'].astype(str)
                df_cari_desa_tab.loc[len(df_cari_desa_tab)] = ['-', 'TOTAL', stats['total']]
                st.dataframe(df_cari_desa_tab, use_container_width=True, hide_index=True) 