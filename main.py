import streamlit as st
import google.generativeai as genai
from groq import Groq
from mistralai.client import MistralClient # Library baru untuk Mistral
import base64
from PIL import Image
from io import BytesIO
from streamlit_cropper import st_cropper
import logging

# ==========================================
# 1. KONFIGURASI ENGINE & SECRETS
# ==========================================
# Membaca pilihan engine dari secrets.toml (Default ke GEMINI jika kosong)
ACTIVE_ENGINE = st.secrets.get("REASONING_ENGINE", "GEMINI").upper()

# SI MATA: Groq (Llama 4 Scout)
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
VISION_MODEL_GROQ = "meta-llama/llama-4-scout-17b-16e-instruct"

# SI OTAK 1: Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
brain_model = genai.GenerativeModel('gemini-2.5-flash')

# SI OTAK 2: Groq
REASONING_MODEL_GROQ = "llama-3.1-8b-instant"

# SI OTAK 3: Mistral
mistral_client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
REASONING_MODEL_MISTRAL = "mistral-large-latest" # Model reasoning terkuat dari Mistral

def encode_image_sapujagat(pil_image):
    """Konversi gambar ke Base64 dengan proteksi mode warna RGB."""
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# ==========================================
# 2. UI SETUP (MOBILE FRIENDLY)
# ==========================================
st.set_page_config(layout="wide", page_title="FF Chemistry")

st.markdown("""
    <style>
    .main .block-container { padding: 1.5rem 1rem; }
    .stButton button {
        height: 3.5em; font-weight: bold;
        background-color: #FF4B4B; color: white; border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 FF Chemistry")

# Menampilkan indikator kecil untuk Developer
st.caption(f"Tanya apa aja tentang kimia, Baginda Fatah pasti bisa")

# ==========================================
# 3. ALUR PIPELINE
# ==========================================
uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    
    st.markdown("### Fokuskan pada Soal")
    cropped_img = st_cropper(img, realtime_update=True, box_color='#FF4B4B', aspect_ratio=None)
    st.write("") # Spacer
    
    if st.button("ANALISIS SEKARANG", use_container_width=True):
        if cropped_img:
            # --- PHASE 1: SCANNING (GROQ VISION) ---
            with st.spinner("⚡ Iziinnn intip soal kamu..."):
                try:
                    base64_image = encode_image_sapujagat(cropped_img)
                    vision_response = groq_client.chat.completions.create(
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Salin ulang soal kimia dalam gambar ini menjadi teks dan LaTeX secara akurat. Jangan dijawab dulu, ambil teks soalnya saja."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }],
                        model=VISION_MODEL_GROQ,
                    )
                    soal_teks = vision_response.choices[0].message.content
                    
                    # with st.expander("Lihat teks hasil scan (Debugging)"):
                    #     st.markdown(soal_teks)
                        
                except Exception as e:
                    st.error("Gagal membaca gambar. Coba area potong yang lebih jelas.")
                    logging.error(f"[VISION ERROR] Gagal di Tahap Vision (Groq): {e}")
                    st.stop()

            # --- PHASE 2: REASONING (BERDASARKAN SECRETS.TOML) ---
            with st.spinner(f"Fatah lagi mikirrrr..."):
                try:
                    prompt_deep = (
                        f"SISTEM: Kamu adalah Fatah, mentor Kimia legendaris yang santai, humble, tapi jagonya minta ampun. "
                        f"Kamu sedang membantu adik favoritmu bernama Faura, siswi SMA cerdas. Gaya bicaramu harus seperti kakak tingkat yang suportif: "
                        f"menggunakan 'aku-kamu', sering memberikan semangat (affirmation), sedikit menggoda kalau ada yang mudah (playful teasing), "
                        f"dan selalu menganggap kimia itu gampang.\n\n"

                        f"TARGET AUDIENS: Faura (Siswa SMA). Jangan meremehkan kecerdasannya, tapi tetap bimbing pelan-pelan.\n\n"
                        f"TUGAS: Analisis dan selesaikan soal berikut dari hasil scan:\n"
                        f"SOAL: {soal_teks}\n\n"

                        f"INSTRUKSI KERJA (CHAIN OF THOUGHT):\n"
                        f"1. Verifikasi Soal: Cek angka-angka aneh hasil scan. Perbaiki pakai logika kimia.\n"
                        f"2. Berpikir Mendalam: Bedah hukum kimianya (Stoikiometri, Termokimia, dll).\n"
                        f"3. Perhitungan: Hitung langkah demi langkah dengan presisi tinggi, tapi jelaskan dengan bahasa yang manusiawi.\n\n"

                        f"FORMAT OUTPUT (STRICT):\n"

                        f"### IDENTIFIKASI\n"
                        f"Jelaskan topik dan data yang ada. Awali dengan sapaan hangat khas Fatah (misal: 'oke, kita bedah pelan-pelan ya...').\n\n"

                        f"### EKSEKUSI\n"
                        f"Uraikan penyelesaiannya. WAJIB gunakan blok LaTeX [ $...$ atau $$...$$ ] untuk semua simbol kimia (misal: $\\text{{H}}_2\\text{{SO}}_4$) "
                        f"dan perhitungan matematika agar rapi.\n\n"

                        f"### KESIMPULAN\n"
                        f"Berikan jawaban akhir yang tegas. Tambahkan sedikit apresiasi (misal: 'yeyy ketemu! gampang kannnn?').\n\n"
                    )
                    
                    # LOGIKA PERCABANGAN MULTI-ENGINE
                    if ACTIVE_ENGINE == "GROQ":
                        reasoning_res = groq_client.chat.completions.create(
                            model=REASONING_MODEL_GROQ,
                            messages=[{"role": "user", "content": prompt_deep}]
                        )
                        jawaban_final = reasoning_res.choices[0].message.content
                        
                    elif ACTIVE_ENGINE == "MISTRAL":
                        reasoning_res = mistral_client.chat.complete(
                            model=REASONING_MODEL_MISTRAL,
                            messages=[{"role": "user", "content": prompt_deep}]
                        )
                        jawaban_final = reasoning_res.choices[0].message.content
                        
                    else:
                        # Default ke Gemini jika diset GEMINI atau kosong
                        brain_response = brain_model.generate_content(prompt_deep)
                        jawaban_final = brain_response.text
                    
                    st.success("Analisis Selesai!")
                    st.markdown(jawaban_final)
                    
                except Exception as e:
                    error_message = str(e).lower()
                
                    if "429" in error_message or "quota" in error_message or "rate_limit" in error_message:
                        st.warning("⏳ Waduh Faura, kayanya si Fatah lagi pusing")
                        logging.warning(f"[QUOTA ERROR] Terjadi limitasi API pada {ACTIVE_ENGINE}: {e}")
                    else:
                        st.error("Gagal memproses gambar. Fatah lagi nge-debug sistemnya sebentar ya.")
                        logging.error(f"[SYSTEM ERROR] Gagal memproses request pada {ACTIVE_ENGINE}:", exc_info=True)
        else:
            st.warning("Pilih area soal terlebih dahulu!")
