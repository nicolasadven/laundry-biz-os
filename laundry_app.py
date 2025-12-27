import streamlit as st
import json
import os

# --- KONFIGURASI FILE PENYIMPANAN ---
CONFIG_FILE = 'laundry_config.json'

def load_config():
    """Membaca konfigurasi dari file JSON jika ada"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(data):
    """Menyimpan konfigurasi ke file JSON"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Laundry Biz OS",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.title("🔐 Laundry Biz OS")
            st.markdown("Silakan masukkan **Kode Lisensi** untuk mengakses aplikasi.")
            with st.form("login_form"):
                password = st.text_input("Kode Lisensi", type="password", placeholder="Masukkan kode...")
                submit_btn = st.form_submit_button("Buka Aplikasi", use_container_width=True)
                if submit_btn:
                    if password == "LAUNDRY2025":
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("⛔ Kode lisensi salah.")
            st.caption("© 2025 Laundry Biz OS. Licensed User Only.")
        return False
    return True

# --- APLIKASI UTAMA ---
if check_password():
    
    # 1. LOAD DATA TERSIMPAN
    defaults = load_config()
    
    # --- HEADER ---
    st.title("👕 Laundry Biz OS: Dashboard Operasional")
    st.markdown("Kalkulator pintar untuk menghitung HPP dan Profitabilitas.")
    st.divider()

    # --- INPUT DATA ---
    with st.sidebar:
        st.header("⚙️ Panel Kontrol")
        
        with st.expander("1. Biaya Energi & Utilitas", expanded=True):
            tarif_listrik = st.number_input("Listrik per kWh (Rp)", value=defaults.get('tarif_listrik', 1444), step=100)
            harga_gas = st.number_input("Harga Gas 12kg (Rp)", value=defaults.get('harga_gas', 215000), step=1000)

        with st.expander("2. Bahan Baku (Chemical)"):
            harga_deterjen = st.number_input("Hrg Deterjen 5L", value=defaults.get('harga_deterjen', 85000))
            takaran_det = st.number_input("Takaran Det (ml)", value=defaults.get('takaran_det', 50))
            
            harga_parfum = st.number_input("Hrg Parfum 5L", value=defaults.get('harga_parfum', 175000))
            takaran_par = st.number_input("Takaran Par (ml)", value=defaults.get('takaran_par', 20))
            
            harga_plastik = st.number_input("Plastik per Baju (Rp)", value=defaults.get('harga_plastik', 500))

        with st.expander("3. Spesifikasi Mesin"):
            kapasitas_mesin = st.number_input("Kapasitas Mesin (Kg)", value=defaults.get('kapasitas_mesin', 7.0))
            watt_cuci = st.number_input("Watt Mesin Cuci", value=defaults.get('watt_cuci', 450))
            durasi_cuci = st.number_input("Durasi Cuci (Menit)", value=defaults.get('durasi_cuci', 45))
            durasi_kering = st.number_input("Durasi Dryer (Menit)", value=defaults.get('durasi_kering', 60))
            gas_per_cycle = st.slider("Gas per Cycle (kg)", 0.1, 1.0, defaults.get('gas_per_cycle', 0.4))

        with st.expander("4. Biaya Tetap (Bulanan)"):
            biaya_tetap = st.number_input("Total Gaji + Sewa (Rp)", value=defaults.get('biaya_tetap', 5000000), step=100000)

        st.markdown("---")
        # TOMBOL SIMPAN KONFIGURASI
        if st.button("💾 Simpan Konfigurasi Saat Ini", use_container_width=True):
            current_config = {
                'tarif_listrik': tarif_listrik,
                'harga_gas': harga_gas,
                'harga_deterjen': harga_deterjen,
                'takaran_det': takaran_det,
                'harga_parfum': harga_parfum,
                'takaran_par': takaran_par,
                'harga_plastik': harga_plastik,
                'kapasitas_mesin': kapasitas_mesin,
                'watt_cuci': watt_cuci,
                'durasi_cuci': durasi_cuci,
                'durasi_kering': durasi_kering,
                'gas_per_cycle': gas_per_cycle,
                'biaya_tetap': biaya_tetap
            }
            if save_config(current_config):
                st.success("✅ Pengaturan berhasil disimpan!")
            
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

    # --- MAIN DASHBOARD ---
    tab1, tab2 = st.tabs(["📊 Analisa HPP", "💰 Simulasi Profit"])

    with tab1:
        st.subheader("Berapa modal yang keluar setiap kali mencuci?")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("HPP per Kg", f"Rp {int(hpp_per_kg):,}", help="Modal murni per Kg pakaian")
        col_m2.metric("HPP per Load", f"Rp {int(hpp_per_load):,}", help="Total biaya sekali mesin jalan")
        col_m3.metric("Kapasitas Efektif", f"{kapasitas_efektif:.1f} Kg", help="Asumsi mesin terisi 80%")

        st.markdown("#### Rincian Biaya per Load")
        st.write(f"⚡ **Listrik:** Rp {int(biaya_listrik):,}")
        st.progress(biaya_listrik/hpp_per_load)
        
        st.write(f"🔥 **Gas Dryer:** Rp {int(biaya_gas_cycle):,}")
        st.progress(biaya_gas_cycle/hpp_per_load)
        
        st.write(f"🧼 **Sabun & Parfum:** Rp {int(biaya_deterjen_cycle + biaya_parfum_cycle):,}")
        st.progress((biaya_deterjen_cycle + biaya_parfum_cycle)/hpp_per_load)

    with tab2:
        st.subheader("Kalkulator Target Keuntungan")
        
        col_sim1, col_sim2 = st.columns([1, 2])
        
        # Kita juga bisa menyimpan target ini jika mau, tapi saat ini saya pisahkan dulu
        # agar user bisa simulasi bebas tanpa merusak settingan utama.
        with col_sim1:
            st.markdown("### 🎯 Atur Target")
            harga_jual = st.number_input("Harga Jual / Kg", value=defaults.get('harga_jual', 6000), step=500)
            target_omzet = st.number_input("Target Omzet / Bulan", value=defaults.get('target_omzet', 15000000), step=500000)
            
            # Tambahan: Tombol simpan kecil khusus untuk tab simulasi (opsional)
            if st.button("Simpan Target"):
                 current_config_update = load_config()
                 current_config_update['harga_jual'] = harga_jual
                 current_config_update['target_omzet'] = target_omzet
                 save_config(current_config_update)
                 st.toast("Target disimpan!", icon="✅")

        with col_sim2:
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
