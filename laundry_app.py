import streamlit as st
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Laundry Biz OS Pro",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS (Dipercantik) ---
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #4CAF50;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2E7D32;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffeeba;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI UTILITAS ---
def format_rupiah(angka):
    return f"Rp {int(angka):,}".replace(",", ".")

def check_password():
    """Manajemen Password Sederhana dengan Session State"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("### 🔐 Akses Terbatas")
        # Password sebaiknya jangan di hardcode jika production serius, 
        # tapi untuk file tunggal ini, kita buat logic inputnya lebih rapi.
        pwd_input = st.text_input("Masukkan Kode Lisensi:", type="password")
        
        if st.button("Masuk"):
            # GANTI PASSWORD DI SINI ATAU GUNAKAN st.secrets
            if pwd_input == "LAUNDRY2025": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("⛔ Kode lisensi salah.")
        return False
    return True

# --- LOGIKA APLIKASI ---
if check_password():
    # Header
    st.title("👕 Laundry Biz OS: Smart Calculator")
    st.caption("Hitung HPP, Profitabilitas, dan Titik Impas (BEP) Laundry Anda.")
    
    # --- SIDEBAR: INPUT DATA ---
    with st.sidebar:
        st.header("⚙️ Parameter Bisnis")
        
        with st.expander("1. Biaya Energi & Utilitas", expanded=True):
            tarif_listrik = st.number_input("Tarif Listrik (Rp/kWh)", value=1444, step=100, help="Cek struk PLN untuk tarif per kWh")
            harga_gas = st.number_input("Harga Gas Elpiji (Rp/Tabung)", value=215000, step=1000)
            berat_tabung_gas = st.selectbox("Ukuran Tabung Gas", [3, 12, 50], index=1, format_func=lambda x: f"{x} Kg")

        with st.expander("2. Bahan Baku (Chemical)"):
            c1, c2 = st.columns(2)
            with c1:
                harga_deterjen = st.number_input("Hrg Deterjen (Rp)", value=85000, help="Harga beli per jerigen")
                vol_deterjen = st.number_input("Vol. Deterjen (Liter)", value=5)
            with c2:
                takaran_det = st.number_input("Takaran Det (ml)", value=50, help="Pemakaian per load")
            
            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                harga_parfum = st.number_input("Hrg Parfum (Rp)", value=175000)
                vol_parfum = st.number_input("Vol. Parfum (Liter)", value=5)
            with c4:
                takaran_par = st.number_input("Takaran Par (ml)", value=20)
            
            harga_plastik = st.number_input("Biaya Packing per Baju/Bungkus (Rp)", value=500)

        with st.expander("3. Spesifikasi Mesin", expanded=True):
            kapasitas_mesin = st.number_input("Kapasitas Mesin Tertulis (Kg)", value=7)
            load_factor = st.slider("Efektifitas Muatan (%)", 50, 100, 80, help="Mesin jarang diisi 100% penuh. Biasanya 80%.")
            
            st.caption("⚡ Konsumsi Daya")
            watt_cuci = st.number_input("Watt Mesin Cuci", value=450)
            durasi_cuci = st.number_input("Durasi Cuci (Menit)", value=45)
            
            st.caption("🔥 Konsumsi Dryer")
            tipe_dryer = st.radio("Tipe Pemanas Dryer", ["Gas", "Listrik"], horizontal=True)
            watt_dryer_motor = st.number_input("Watt Motor/Putaran Dryer", value=150, help="Listrik untuk memutar drum, bukan memanas.")
            durasi_kering = st.number_input("Durasi Dryer (Menit)", value=60)
            
            gas_per_cycle = 0.0
            watt_dryer_heater = 0.0
            
            if tipe_dryer == "Gas":
                gas_per_cycle = st.slider("Konsumsi Gas (kg/cycle)", 0.1, 1.0, 0.4)
            else:
                watt_dryer_heater = st.number_input("Watt Pemanas (Heater)", value=2000)

        with st.expander("4. Biaya Operasional (Fixed Cost)"):
            biaya_sewa = st.number_input("Sewa Tempat / Bulan (Rp)", value=1500000)
            biaya_gaji = st.number_input("Total Gaji Karyawan / Bulan (Rp)", value=3000000)
            biaya_lain = st.number_input("Internet & Lain-lain (Rp)", value=500000)
            biaya_tetap_total = biaya_sewa + biaya_gaji + biaya_lain
            st.write(f"**Total Fixed Cost: {format_rupiah(biaya_tetap_total)}**")

    # --- PERHITUNGAN LOGIKA (BACKEND) ---
    
    # 1. Validasi Pembagi Nol
    if kapasitas_mesin == 0 or vol_deterjen == 0 or vol_parfum == 0:
        st.error("⚠️ Kapasitas mesin atau volume bahan baku tidak boleh 0.")
        st.stop()

    # 2. Hitung Kapasitas Efektif
    kapasitas_efektif = kapasitas_mesin * (load_factor / 100) # Kg real per cycle

    # 3. Hitung Biaya Listrik
    # Rumus: (Watt / 1000) * (Menit / 60) * Tarif
    kwh_cuci = (watt_cuci / 1000) * (durasi_cuci / 60)
    
    if tipe_dryer == "Gas":
        # Dryer Gas: Listrik hanya untuk motor
        kwh_dryer = (watt_dryer_motor / 1000) * (durasi_kering / 60)
        biaya_gas_cycle = (harga_gas / berat_tabung_gas) * gas_per_cycle
    else:
        # Dryer Listrik: Motor + Heater
        total_watt_dryer = watt_dryer_motor + watt_dryer_heater
        kwh_dryer = (total_watt_dryer / 1000) * (durasi_kering / 60)
        biaya_gas_cycle = 0

    biaya_listrik_cycle = (kwh_cuci + kwh_dryer) * tarif_listrik

    # 4. Hitung Biaya Chemical
    # Konversi Liter ke ml -> * 1000
    biaya_det_cycle = (harga_deterjen / (vol_deterjen * 1000)) * takaran_det
    biaya_par_cycle = (harga_parfum / (vol_parfum * 1000)) * takaran_par
    
    # 5. Total HPP
    hpp_per_cycle = biaya_listrik_cycle + biaya_gas_cycle + biaya_det_cycle + biaya_par_cycle + harga_plastik
    hpp_per_kg = hpp_per_cycle / kapasitas_efektif

    # --- TAMPILAN UTAMA (TABS) ---
    
    tab1, tab2, tab3 = st.tabs(["💰 Analisa HPP", "📈 Simulasi Profit", "⚖️ Break Even Point"])

    with tab1:
        st.subheader("Analisa Harga Pokok Produksi (HPP)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">HPP Per Cycle (Load)</div>
                <div class="metric-value">{format_rupiah(hpp_per_cycle)}</div>
                <small>1x Cuci & Kering ({kapasitas_mesin}kg)</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 5px solid #2196F3;">
                <div class="metric-label">HPP Per Kg Real</div>
                <div class="metric-value">{format_rupiah(hpp_per_kg)}</div>
                <small>Asumsi isi {int(load_factor)}% ({kapasitas_efektif:.1f} Kg)</small>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 5px solid #FF9800;">
                <div class="metric-label">Total Cost Energy</div>
                <div class="metric-value">{format_rupiah(biaya_listrik_cycle + biaya_gas_cycle)}</div>
                <small>Listrik + Gas per cycle</small>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### 📋 Rincian Komponen Biaya per Cycle")
        # Menampilkan progress bar komposisi biaya
        total_c = hpp_per_cycle
        st.write(f"⚡ Listrik: **{format_rupiah(biaya_listrik_cycle)}** ({biaya_listrik_cycle/total_c:.1%})")
        st.progress(biaya_listrik_cycle/total_c)
        
        st.write(f"🔥 Gas: **{format_rupiah(biaya_gas_cycle)}** ({biaya_gas_cycle/total_c:.1%})")
        st.progress(biaya_gas_cycle/total_c)
        
        st.write(f"🧼 Chemical: **{format_rupiah(biaya_det_cycle + biaya_par_cycle)}** ({(biaya_det_cycle + biaya_par_cycle)/total_c:.1%})")
        st.progress((biaya_det_cycle + biaya_par_cycle)/total_c)

    with tab2:
        st.subheader("Simulasi Keuntungan Bulanan")
        
        col_input_sim, col_res_sim = st.columns([1, 2])
        
        with col_input_sim:
            harga_jual_kg = st.number_input("Harga Jual per Kg (Rp)", value=7000, step=500)
            target_kg_hari = st.number_input("Target Rata-rata Kg / Hari", value=50)
            hari_kerja = st.slider("Hari Buka per Bulan", 20, 31, 30)

        with col_res_sim:
            omzet_bulanan = harga_jual_kg * target_kg_hari * hari_kerja
            total_hpp_bulanan = hpp_per_kg * target_kg_hari * hari_kerja
            laba_kotor = omzet_bulanan - total_hpp_bulanan
            laba_bersih = laba_kotor - biaya_tetap_total
            margin_bersih = (laba_bersih / omzet_bulanan) * 100 if omzet_bulanan > 0 else 0
            
            st.info(f"📊 Estimasi Omzet: **{format_rupiah(omzet_bulanan)}** / bulan")
            
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.metric("Laba Kotor (Gross Profit)", format_rupiah(laba_kotor), delta="Sebelum potong gaji/sewa")
            with c_res2:
                color = "normal" if laba_bersih > 0 else "inverse"
                st.metric("Laba Bersih (Net Profit)", format_rupiah(laba_bersih), f"{margin_bersih:.1f}% Margin", delta_color=color)

            if laba_bersih < 0:
                st.warning("⚠️ Bisnis merugi dengan target volume ini. Tingkatkan volume atau harga jual, atau kurangi biaya tetap.")

    with tab3:
        st.subheader("⚖️ Titik Impas (Break Even Point)")
        st.write("Berapa Kg cucian yang harus didapat hanya untuk menutup biaya operasional (Gaji + Sewa)?")
        
        # Rumus BEP Unit = Fixed Cost / (Harga Jual - Variable Cost per Unit)
        margin_per_kg = harga_jual_kg - hpp_per_kg
        
        if margin_per_kg <= 0:
            st.error("⛔ Harga jual lebih rendah dari HPP! Anda rugi di setiap Kg cucian. Naikkan harga jual.")
        else:
            bep_kg_bulan = biaya_tetap_total / margin_per_kg
            bep_kg_hari = bep_kg_bulan / hari_kerja
            
            c_bep1, c_bep2 = st.columns(2)
            
            with c_bep1:
                st.markdown(f"""
                <div class="warning-box">
                    <h3>Target Bulanan</h3>
                    <h1>{math.ceil(bep_kg_bulan):,} Kg</h1>
                    <p>Minimal cucian per bulan agar Balik Modal.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with c_bep2:
                st.markdown(f"""
                <div class="warning-box">
                    <h3>Target Harian</h3>
                    <h1>{math.ceil(bep_kg_hari):,} Kg</h1>
                    <p>Minimal cucian per hari (selama {hari_kerja} hari).</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.write("---")
            st.write(f"Saat ini Anda menargetkan **{target_kg_hari} Kg/hari**.")
            if target_kg_hari > bep_kg_hari:
                st.success(f"✅ Target Anda sudah di atas titik impas (Safe Zone). Kelebihan {int(target_kg_hari - bep_kg_hari)} Kg adalah profit.")
            else:
                st.error(f"❌ Target Anda masih di bawah titik impas! Anda butuh {int(bep_kg_hari - target_kg_hari)} Kg lagi per hari.")

    # Footer
    st.markdown("---")
    st.caption("© 2025 Laundry Biz OS Pro. Generated by AI Assistant.")
