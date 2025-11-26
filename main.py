import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io
import traceback # <--- The X-Ray Tool

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chronos: Time Machine", page_icon="⌛", layout="centered")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    .stBlock, div[data-testid="stVerticalBlock"] {
        background-color: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #00e5ff;
    }
    h1 { font-family: 'Orbitron', sans-serif; color: #00e5ff; text-align: center; }
    h3, p, label { color: #ffffff !important; font-family: 'Courier New', monospace; }
    .stButton>button {
        background-color: #00e5ff; color: black; font-family: 'Orbitron', sans-serif;
        border: none; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("CHRONOS V14 (X-RAY)")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 3. AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 4. MAIN LOGIC ---
if api_key:
    # We use the generic client (no model specified yet)
    client = InferenceClient(token=api_key)

    st.write("### 1. ACQUIRE BIOMETRIC DATA")
    input_method = st.radio("Select Input Source:", ["Activate Camera", "Upload File"])

    image_input = None
    if input_method == "Activate Camera":
        image_input = st.camera_input("Scanning Face...")
    else:
        image_input = st.file_uploader("Upload Image Data", type=["jpg", "png", "jpeg"])

    if image_input:
        original_image = Image.open(image_input)
        original_image = original_image.resize((512, 512)) # Resize to prevent timeout
        
        st.image(original_image, caption="SUBJECT: PRESENT DAY (512x512)", width=300)

        st.write("---")
        st.write("### 2. SET TEMPORAL COORDINATES")
        years = st.select_slider("Warp Forward By:", options=["10 Years", "30 Years", "50 Years", "80 Years"])

        prompts = {
            "10 Years": "photo of a person, slightly older, 10 years later, realistic, 8k",
            "30 Years": "photo of a person, middle aged, 50 years old, grey hair, wrinkles, realistic",
            "50 Years": "photo of a person, 70 years old, grandmother grandfather, white hair, elderly, detailed",
            "80 Years": "photo of a person, 100 years old, ancient, deep wrinkles, very old, detailed portrait"
        }

        if st.button("INITIATE TIME WARP"):
            with st.spinner("⚡ WARPING TIME..."):
                try:
                    # Explicitly using the image_to_image function
                    edited_image = client.image_to_image(
                        image=original_image,
                        prompt=prompts[years],
                        model="runwayml/stable-diffusion-v1-5",
                        strength=0.5,
                        guidance_scale=7.5
                    )
                    
                    st.success("✔ TEMPORAL JUMP COMPLETE")
                    st.image(edited_image, caption=f"SUBJECT: +{years}")

                except Exception:
                    # --- X-RAY VISION ---
                    st.error("⚠️ SYSTEM CRASH DETECTED")
                    st.write("Here is the exact technical error:")
                    # This prints the FULL ugly error message so we know exactly what is wrong
                    st.code(traceback.format_exc())

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
