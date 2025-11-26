import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Chronos: Time Machine", page_icon="⌛", layout="centered")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    .stBlock, div[data-testid="stVerticalBlock"] {
        background-color: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #00e5ff;
    }

    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        text-shadow: 0 0 10px #00e5ff;
        text-align: center;
    }
    h3, p, label {
        color: #ffffff !important;
        font-family: 'Courier New', monospace;
    }

    .stButton>button {
        background-color: #00e5ff;
        color: black;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        box-shadow: 0 0 15px #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.title("CHRONOS V3.0")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 4. AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 5. MAIN LOGIC ---
if api_key:
    # FIX #1: Initialize Client WITHOUT a model to prevent conflicts
    client = InferenceClient(token=api_key)

    st.write("### 1. ACQUIRE BIOMETRIC DATA")
    input_method = st.radio("Select Input Source:", ["Activate Camera", "Upload File"])

    image_input = None
    if input_method == "Activate Camera":
        image_input = st.camera_input("Scanning Face...")
    else:
        image_input = st.file_uploader("Upload Image Data", type=["jpg", "png", "jpeg"])

    if image_input:
        st.image(image_input, caption="SUBJECT: PRESENT DAY", width=300)
        original_image = Image.open(image_input)

        st.write("---")
        st.write("### 2. SET TEMPORAL COORDINATES")
        
        years = st.select_slider(
            "Warp Forward By:",
            options=["10 Years", "30 Years", "50 Years", "80 Years"]
        )

        prompts = {
            "10 Years": "make them look 10 years older, slight skin texture",
            "30 Years": "make them look 40 years older, grey hair, visible wrinkles",
            "50 Years": "make them look 70 years old, elderly, white hair, deep wrinkles",
            "80 Years": "make them look 100 years old, ancient, very old, detailed texture"
        }

        if st.button("INITIATE TIME WARP"):
            status_box = st.empty()
            
            # FIX #2: The Retry Loop for "Cold" models
            for attempt in range(3):
                try:
                    status_box.info(f"⚡ Attempt {attempt+1}/3: Establishing Neural Link...")
                    
                    # FIX #3: Pass image as the FIRST argument (positional)
                    # We also explicitly pass the model name HERE.
                    edited_image = client.image_to_image(
                        original_image,
                        model="timbrooks/instruct-pix2pix", 
                        prompt=prompts[years], 
                        guidance_scale=8.5,
                        image_guidance_scale=1.5
                    )
                    
                    status_box.success("✔ TEMPORAL JUMP COMPLETE")
                    st.image(edited_image, caption=f"SUBJECT: +{years}")
                    break
                    
                except Exception as e:
                    # FIX #4: Better Error Logging
                    error_text = str(e)
                    if "503" in error_text or "loading" in error_text.lower():
                        status_box.warning(f"⚠ Server Warming Up... ({3-attempt} tries left)")
                        time.sleep(5)
                    else:
                        st.error("⚠️ CRITICAL FAILURE")
                        # This prints the RAW error object so we can see hidden details
                        st.write(f"Debug Info: {repr(e)}")
                        break

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
