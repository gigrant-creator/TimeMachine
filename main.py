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

st.title("CHRONOS V5.0")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 3. AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 4. HELPER FUNCTIONS ---
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def query_huggingface_manual(payload, api_key):
    # --- THE FIX IS HERE ---
    # We updated the URL from 'api-inference' to 'router' as requested by the server error.
    API_URL = "https://router.huggingface.co/models/timbrooks/instruct-pix2pix"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Wait-For-Model": "true" 
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

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
        st.image(original_image, caption="SUBJECT: PRESENT DAY", width=300)

        st.write("---")
        st.write("### 2. SET TEMPORAL COORDINATES")
        years = st.select_slider("Warp Forward By:", options=["10 Years", "30 Years", "50 Years", "80 Years"])

        prompts = {
            "10 Years": "make them look 10 years older, slight skin texture",
            "30 Years": "make them look 40 years older, grey hair, visible wrinkles",
            "50 Years": "make them look 70 years old, elderly, white hair, deep wrinkles",
            "80 Years": "make them look 100 years old, ancient, very old, detailed texture"
        }

        if st.button("INITIATE TIME WARP"):
            status_box = st.empty()
            
            # The Data Packet
            payload = {
                "inputs": prompts[years],
                "image": image_to_base64(original_image),
                "parameters": {
                    "guidance_scale": 7.5,
                    "image_guidance_scale": 1.5,
                }
            }

            for attempt in range(3):
                status_box.info(f"⚡ Attempt {attempt+1}/3: Establishing Link...")
                
                try:
                    response = query_huggingface_manual(payload, api_key)
                    
                    if response.status_code == 200:
                        edited_image = Image.open(io.BytesIO(response.content))
                        status_box.success("✔ TEMPORAL JUMP COMPLETE")
                        st.image(edited_image, caption=f"SUBJECT: +{years}")
                        break
                    
                    elif "loading" in response.text.lower() or response.status_code == 503:
                        status_box.warning(f"⚠ Server Warming Up... ({3-attempt} tries left)")
                        time.sleep(15) 
                        
                    else:
                        st.error("⚠️ CRITICAL FAILURE")
                        st.write(f"Server Response: {response.text}")
                        break

                except Exception as e:
                    st.error(f"Connection Error: {e}")
                    break

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
