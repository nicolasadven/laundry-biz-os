import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Laundry Biz OS",
    page_icon="👕",
    layout="wide"
)

# --- STYLE CSS ---
st.markdown("""
<style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; }
    .stNumberInput > label { font-weight: bold; color: #333; }
</style>
""", unsafe_allow_html=True)

# --- SISTEM KUNCI (LICENSING) ---
# Ini adalah gerbang utamanya.
# User harus memasukkan kode ini agar bisa melihat isinya.
# Tips: Anda bisa ganti kode ini tiap bulan dan kirim ke pelanggan.

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "LAUNDRY2025": # <--- GANTI PASSWORD DI SINI
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "🔑 Masukkan Kode Lisensi Produk", type="password", on_change=password_entered, key="password"
        )
        st.warning("Silakan masukkan kode lisensi yang Anda dapatkan saat pembelian.")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "🔑 Masukkan Kode Lisensi Produk", type="password", on_change=password_entered, key="password"
        )
        st.error("⛔ Kode salah atau sudah kadaluarsa.")
        return False
    else:
        # Password correct.
        return True

if check_password():
    # --- MULAI APLIKASI DI BAWAH INI ---
    
    # --- HEADER ---
    st.title("👕 Laundry Biz OS: Operasional Calculator")
    st.markdown("Aplikasi penghitung HPP dan Profitabilitas Laundry Anti-Boncos.")
    st.markdown("---")

    # --- SIDEBAR: INPUT DATA (SETUP) ---
    with st.sidebar:
        st.header("⚙️ Konfigurasi Biaya")
        
        st.subheader("1. Utilitas & Energi")
        tarif_listrik = st.number_input("Tarif Listrik per kWh (Rp)", value=1444, step=100)
        harga_gas = st.number_input("Harga Gas 12kg (Rp)", value=215000, step=1000)
        
        st.subheader("2. Bahan Baku (Chemical)")
        col_a, col_b = st.columns(2)
        with col_a:
            harga_deterjen = st.number_input("Hrg Deterjen 5L", value=85000)
            harga_parfum = st.number_input("Hrg Parfum 5L", value=175000)
        with col_b:
            takaran_det = st.number_input("Takaran (ml)", value=50)
            takaran_par = st.number_input("Takaran (ml)", value=20)
            
        harga_plastik = st.number_input("Biaya Plastik per Bungkus (Rp)", value=500)

        st.subheader("3. Spesifikasi Mesin")
        watt_cuci = st.number_input("Daya Mesin Cuci (Watt)", value=450)
        durasi_cuci = st.number_input("Durasi Cuci (Menit)", value=45)
        durasi_kering = st.number_input("Durasi Dryer (Menit)", value=60)
        gas_per_cycle = st.slider("Pemakaian Gas (kg/cycle)", 0.1, 1.0, 0.4)
        kapasitas_mesin = st.number_input("Kapasitas Mesin (Kg)", value=7)

        st.subheader("4. Operasional Bulanan")
        biaya_tetap = st.number_input("Total Fixed Cost (Gaji+Sewa) per Bulan", value=5000000, step=100000)

    # --- LOGIKA PERHITUNGAN ---
    kwh_cuci = (watt_cuci / 1000) * (durasi_cuci / 60)
    kwh_dryer = (150 / 1000) * (durasi_kering / 60)
    biaya_listrik = (kwh_cuci + kwh_dryer) * tarif_listrik
    biaya_gas_cycle = (harga_gas / 12) * gas_per_cycle
    biaya_deterjen_cycle = (harga_deterjen / 5000) * takaran_det
    biaya_parfum_cycle = (harga_parfum / 5000) * takaran_par
    hpp_per_load = biaya_listrik + biaya_gas_cycle + biaya_deterjen_cycle + biaya_parfum_cycle + harga_plastik
    kapasitas_efektif = kapasitas_mesin * 0.8
    hpp_per_kg = hpp_per_load / kapasitas_efektif

    # --- HALAMAN UTAMA ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("💰 Analisa HPP (Modal)")
        st.markdown(f"""
        <div class="metric-card">
            <h3>HPP Dasar Per Kg</h3>
            <h1 style="color: #D32F2F;">Rp {int(hpp_per_kg):,}</h1>
            <p>Modal murni (Listrik + Gas + Sabun) per Kg.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("---")
        st.write("**Rincian Biaya per Load:**")
        st.write(f"⚡ Listrik: Rp {int(biaya_listrik):,}")
        st.write(f"🔥 Gas Dryer: Rp {int(biaya_gas_cycle):,}")
        st.write(f"🧼 Deterjen/Parfum: Rp {int(biaya_deterjen_cycle + biaya_parfum_cycle):,}")

    with col2:
        st.subheader("📈 Simulasi Profit")
        harga_jual = st.number_input("Harga Jual per Kg (Rp)", value=6000, step=500)
        target_omzet = st.number_input("Target Omzet per Bulan (Rp)", value=15000000, step=500000)
        
        laba_kotor = target_omzet - ((target_omzet/harga_jual) * hpp_per_kg)
        laba_bersih = laba_kotor - biaya_tetap
        kg_per_hari_needed = (target_omzet / harga_jual) / 30
        
        st.markdown(f"""
        <div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32;">
            <h3>Estimasi Laba Bersih</h3>
            <h1 style="color: #2E7D32;">Rp {int(laba_bersih):,}</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write(f"Target: **{int(kg_per_hari_needed)} Kg / hari**")

    # --- FOOTER ---
    st.markdown("---")
    st.caption("© 2025 Laundry Biz OS. Licensed User Only.")