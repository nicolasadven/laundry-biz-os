import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Laundry Biz OS",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI LOGIN (UI DIPERBAIKI) ---
def check_password():
    """Manajemen Password dengan Tampilan Centered"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        # Membuat 3 kolom agar form ada di tengah
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True) # Spacer
            st.title("🔐 Laundry Biz OS")
            st.markdown("Silakan masukkan **Kode Lisensi** untuk mengakses aplikasi.")
            
            with st.form("login_form"):
                password = st.text_input("Kode Lisensi", type="password", placeholder="Masukkan kode di sini...")
                submit_btn = st.form_submit_button("Buka Aplikasi", use_container_width=True)
                
                if submit_btn:
                    if password == "LAUNDRY2025": # <--- GANTI PASSWORD DI SINI
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("⛔ Kode lisensi salah.")
            
            st.caption("© 2025 Laundry Biz OS. Licensed User Only.")
        return False
    return True

# --- APLIKASI UTAMA ---
if check_password():
    
    # --- HEADER ---
    st.title("👕 Laundry Biz OS: Dashboard Operasional")
    st.markdown("Kalkulator pintar untuk menghitung HPP (Harga Pokok Produksi) dan Profitabilitas Laundry.")
    st.divider()

    # --- INPUT DATA (MENGGUNAKAN EXPANDER AGAR RAPI) ---
    # Kita pindahkan input detail ke dalam Expander agar user tidak pusing melihat banyak kotak isian
    
    with st.sidebar:
        st.header("⚙️ Panel Kontrol")
        st.info("Atur parameter biaya laundry Anda di sini.")
        
        with st.expander("1. Biaya Energi & Utilitas", expanded=True):
            tarif_listrik = st.number_input("Listrik per kWh (Rp)", value=1444, step=100)
            harga_gas = st.number_input("Harga Gas 12kg (Rp)", value=215000, step=1000)

        with st.expander("2. Bahan Baku (Chemical)"):
            st.caption("Input harga per jerigen (5L) dan takaran pakai.")
            harga_deterjen = st.number_input("Hrg Deterjen 5L", value=85000)
            takaran_det = st.number_input("Takaran Det (ml)", value=50)
            
            harga_parfum = st.number_input("Hrg Parfum 5L", value=175000)
            takaran_par = st.number_input("Takaran Par (ml)", value=20)
            
            harga_plastik = st.number_input("Plastik per Baju (Rp)", value=500)

        with st.expander("3. Spesifikasi Mesin"):
            kapasitas_mesin = st.number_input("Kapasitas Mesin (Kg)", value=7)
            watt_cuci = st.number_input("Watt Mesin Cuci", value=450)
            durasi_cuci = st.number_input("Durasi Cuci (Menit)", value=45)
            st.markdown("---")
            durasi_kering = st.number_input("Durasi Dryer (Menit)", value=60)
            gas_per_cycle = st.slider("Gas per Cycle (kg)", 0.1, 1.0, 0.4)

        with st.expander("4. Biaya Tetap (Bulanan)"):
            biaya_tetap = st.number_input("Total Gaji + Sewa (Rp)", value=5000000, step=100000)

    # --- LOGIKA PERHITUNGAN (BACKEND) ---
    kwh_cuci = (watt_cuci / 1000) * (durasi_cuci / 60)
    kwh_dryer = (150 / 1000) * (durasi_kering / 60) # Asumsi motor dryer 150W
    biaya_listrik = (kwh_cuci + kwh_dryer) * tarif_listrik
    biaya_gas_cycle = (harga_gas / 12) * gas_per_cycle
    biaya_deterjen_cycle = (harga_deterjen / 5000) * takaran_det
    biaya_parfum_cycle = (harga_parfum / 5000) * takaran_par
    
    # Total HPP per Load
    hpp_per_load = biaya_listrik + biaya_gas_cycle + biaya_deterjen_cycle + biaya_parfum_cycle + harga_plastik
    
    # HPP per Kg (Asumsi mesin terisi 80%)
    kapasitas_efektif = kapasitas_mesin * 0.8
    hpp_per_kg = hpp_per_load / kapasitas_efektif

    # --- MAIN DASHBOARD (MENGGUNAKAN TABS) ---
    tab1, tab2 = st.tabs(["📊 Analisa HPP (Modal)", "💰 Simulasi Profit"])

    with tab1:
        st.subheader("Berapa modal yang keluar setiap kali mencuci?")
        
        # Menggunakan Metric Card bawaan Streamlit yang lebih rapi
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("HPP per Kg", f"Rp {int(hpp_per_kg):,}", help="Modal murni per Kg pakaian")
        col_m2.metric("HPP per Load (1x Putar)", f"Rp {int(hpp_per_load):,}", help="Total biaya sekali mesin jalan")
        col_m3.metric("Kapasitas Efektif", f"{kapasitas_efektif:.1f} Kg", help="Asumsi mesin terisi 80%")

        st.markdown("#### Rincian Biaya per Load")
        
        # Visualisasi sederhana dengan Progress Bar
        st.write(f"⚡ **Listrik:** Rp {int(biaya_listrik):,}")
        st.progress(biaya_listrik/hpp_per_load)
        
        st.write(f"🔥 **Gas Dryer:** Rp {int(biaya_gas_cycle):,}")
        st.progress(biaya_gas_cycle/hpp_per_load)
        
        st.write(f"🧼 **Sabun & Parfum:** Rp {int(biaya_deterjen_cycle + biaya_parfum_cycle):,}")
        st.progress((biaya_deterjen_cycle + biaya_parfum_cycle)/hpp_per_load)

    with tab2:
        st.subheader("Kalkulator Target Keuntungan")
        
        col_sim1, col_sim2 = st.columns([1, 2])
        
        with col_sim1:
            st.markdown("### 🎯 Atur Target")
            harga_jual = st.number_input("Harga Jual / Kg", value=6000, step=500)
            target_omzet = st.number_input("Target Omzet / Bulan", value=15000000, step=500000)
        
        with col_sim2:
            # Perhitungan Profit
            laba_kotor = target_omzet - ((target_omzet/harga_jual) * hpp_per_kg)
            laba_bersih = laba_kotor - biaya_tetap
            kg_per_hari_needed = (target_omzet / harga_jual) / 30
            
            st.markdown("### 📈 Hasil Simulasi")
            
            c_res1, c_res2 = st.columns(2)
            c_res1.metric("Estimasi Laba Bersih", f"Rp {int(laba_bersih):,}", delta="Net Profit")
            c_res2.metric("Target Load Cucian", f"{int(kg_per_hari_needed)} Kg / Hari", delta="Productivity")
            
            if laba_bersih < 0:
                st.error("⚠️ Peringatan: Target omzet ini belum menutup biaya operasional (Rugi).")
            else:
                st.success("✅ Bisnis Profitable! Target tercapai.")
