import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI API GEMINI
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. PENGATURAN LAYOUT & CSS MOBILE
st.set_page_config(layout="wide", page_title="ChemCompute Pro")
st.markdown("""
    <style>
    .main .block-container { padding: 2rem 1rem; }
    .stButton button {
        height: 3.5em;
        font-weight: bold;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 ChemCompute Pro")
st.caption("Asisten Kimia AI - Powered by Maestro Routing")

# ==========================================
# 3. DATABASE PROMPT SPESIALIS (KUMPULAN AGEN)
# ==========================================
PROMPTS = {
    "KIMIA_FISIKA": (
        "Bertindaklah sebagai mentor Olimpiade Kimia (OSN) bernama Fatah. Target audiensmu adalah siswa SMA bernama Faura "
        "yang cerdas, analitis, dan terbiasa dengan soal hitungan tingkat lanjut. "
        "Fokuslah pada perhitungan Stoikiometri, Termokimia, Kesetimbangan, atau Elektrokimia. "
        "Struktur jawaban: 1. Parameter soal, 2. Reaksi/Rumus (LaTeX), 3. Langkah stoikiometri logis, 4. Jawaban akhir."
        "Berikan satu insight efisiensi dari Kak Fatah."
    ),
    "KIMIA_ORGANIK": (
        "Bertindaklah sebagai mentor Olimpiade Kimia (OSN) bernama Fatah. Target audiensmu adalah siswa SMA bernama Faura. "
        "Ini adalah soal Kimia Organik. Jangan fokus pada hitungan matematis, tapi fokuslah pada analisis struktur! "
        "Jelaskan identifikasi gugus fungsi, tatanama IUPAC, stereokimia, atau mekanisme reaksi (seperti SN1/SN2/Adisi) yang relevan secara logis. "
        "Gunakan gaya bahasa akademik profesional namun engaging. Berikan kesimpulan produk atau struktur yang benar."
    ),
    "DEFAULT": (
        "Bertindaklah sebagai mentor Olimpiade Kimia (OSN) bernama Fatah. Bantu Faura memahami dan menyelesaikan soal kimia ini "
        "dengan penjelasan yang taktis, efisien, dan presisi secara ilmiah."
    )
}

# ==========================================
# 4. LOGIKA UTAMA APLIKASI
# ==========================================
uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    # Resize untuk Mobile
    max_width_mobile = 400 
    if img.width > max_width_mobile:
        ratio = max_width_mobile / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width_mobile, new_height), Image.Resampling.LANCZOS)

    st.markdown("## Pilih Soal")
    cropped_img = st_cropper(img, realtime_update=True, box_color='#FF4B4B', aspect_ratio=None)
    
    st.write("")
    hitung_btn = st.button("🚀 Lakukan Perhitungan", use_container_width=True)
    st.divider()

    if hitung_btn:
        if cropped_img:
            st.markdown("## Analisis & Solusi")
            
            try:
                # --- PASS 1: ROUTING (KLASIFIKASI SOAL) ---
                with st.spinner("🔍 Mendeteksi jenis soal kimia..."):
                    router_prompt = (
                        "Analisis gambar ini dengan sangat singkat. Tentukan apakah ini soal hitungan (seperti stoikiometri/elektrokimia) "
                        "atau soal struktur molekul (kimia organik). "
                        "Jawab HANYA dengan satu kata persis dari pilihan ini: KIMIA_FISIKA, KIMIA_ORGANIK, atau DEFAULT. "
                        "Jangan tambahkan penjelasan apa pun."
                    )
                    kategori_response = model.generate_content([router_prompt, cropped_img])
                    kategori = kategori_response.text.strip().upper()
                    
                    # Validasi output router, jika aneh, lempar ke DEFAULT
                    if kategori not in PROMPTS:
                        kategori = "DEFAULT"
                        
                # Menampilkan badge kategori ke pengguna
                st.info(f"Kategori Terdeteksi: **{kategori.replace('_', ' ')}**")

                # --- PASS 2: SOLVING (MENGGUNAKAN PROMPT SPESIFIK) ---
                with st.spinner(f"🧠 Kak Fatah sedang menyusun strategi untuk {kategori.replace('_', ' ').lower()}..."):
                    final_prompt = PROMPTS[kategori]
                    
                    response = model.generate_content([final_prompt, cropped_img])
                    st.success("Selesai!")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Gagal memproses gambar: {e}")
