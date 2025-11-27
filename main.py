import streamlit as st
import requests
from PIL import Image
import io
import base64
import time

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

st.title("CHRONOS V16 (MANUAL)")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 3. AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 4. HELPER: IMAGE TO BASE64 ---
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 5. MAIN LOGIC ---
if api_key:
    st.write("### 1. ACQUIRE BIOMETRIC DATA")
    input_method = st.radio("Select Input Source:", ["Activate Camera", "Upload File"])

    image_input = None
    if input_method == "Activate Camera":
        image_input = st.camera_input("Scanning Face...")
    else:
        image_input = st.file_uploader("Upload Image Data", type=["jpg", "png", "jpeg"])

    if image_input:
        original_image = Image.open(image_input)
        original_image = original_image.resize((512, 512)) # CRITICAL RESIZE
        
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
            with st.spinner("⚡ CONTACTING SERVER..."):
                try:
                    # --- THE FIX: MANUAL REQUESTS ---
                    # We do not use the 'InferenceClient' object. We use raw internet requests.
                    API_URL = "https://router.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    headers = {"Authorization": f"Bearer {api_key}"}
                    
                    payload = {
                        "inputs": prompts[years],
                        "parameters": {
                            "image": image_to_base64(original_image), 
                            "strength": 0.5,
                            "guidance_scale": 7.5
                        }
                    }
                    
                    # RETRY LOOP: If server is busy, wait and try again
                    for attempt in range(3):
                        response = requests.post(API_URL, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            # Success!
                            edited_image = Image.open(io.BytesIO(response.content))
                            st.success("✔ TEMPORAL JUMP COMPLETE")
                            st.image(edited_image, caption=f"SUBJECT: +{years}")
                            break # Exit the loop
                        
                        elif "loading" in response.text.lower() or response.status_code == 503:
                            st.warning(f"⚠ Server Warming Up... (Attempt {attempt+1}/3)")
                            time.sleep(10) # Wait 10 seconds
                        
                        else:
                            st.error(f"⚠️ SERVER ERROR: {response.status_code}")
                            st.code(response.text)
                            break # Stop trying if it's a real error

                except Exception as e:
                    st.error("⚠️ SYSTEM ERROR")
                    st.write(f"Details: {e}")

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
