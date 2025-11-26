import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Chronos: Time Machine", page_icon="⌛", layout="centered")

# --- 2. THE DESIGN (CSS HACKS) ---
# This block injects "Cascading Style Sheets" to change the look
st.markdown("""
    <style>
    /* Import a sci-fi font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* The Main Background - A starry warp speed image */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Glassmorphism Effect for containers */
    .stBlock, div[data-testid="stVerticalBlock"] {
        background-color: rgba(0, 0, 0, 0.7); /* Semi-transparent black */
        border-radius: 15px;
        padding: 10px;
    }

    /* Typography - Neon Blue/Green */
    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        text-shadow: 0 0 10px #00e5ff, 0 0 20px #00e5ff;
        text-align: center;
    }
    h3, p, label {
        color: #ffffff !important;
        font-family: 'Courier New', monospace;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #00e5ff;
        color: black;
        font-family: 'Orbitron', sans-serif;
        border: none;
        border-radius: 5px;
        box-shadow: 0 0 10px #00e5ff;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        box-shadow: 0 0 20px #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. APP HEADER ---
st.title("CHRONOS V1.0")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 4. API SETUP ---
# It tries to find the secret automatically
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 5. MAIN LOGIC ---
if api_key:
    client = InferenceClient(token=api_key)

    # Input Method: Camera or Upload
    st.write("### 1. ACQUIRE BIOMETRIC DATA")
    input_method = st.radio("Select Input Source:", ["Activate Camera", "Upload File"])

    image_input = None

    if input_method == "Activate Camera":
        image_input = st.camera_input("Scanning Face...")
    else:
        image_input = st.file_uploader("Upload Image Data", type=["jpg", "png", "jpeg"])

    if image_input:
        # Show the user their current self
        st.image(image_input, caption="SUBJECT: PRESENT DAY", width=300)
        
        # Convert image for AI
        original_image = Image.open(image_input)

        st.write("---")
        st.write("### 2. SET TEMPORAL COORDINATES")
        
        # The Time Travel Slider
        years = st.select_slider(
            "Warp Forward By:",
            options=["10 Years", "30 Years", "50 Years", "80 Years"]
        )

        # Map options to AI prompts
        prompts = {
            "10 Years": "make them look 10 years older, slight skin texture",
            "30 Years": "make them look 40 years older, grey hair, visible wrinkles",
            "50 Years": "make them look 70 years old, elderly, white hair, deep wrinkles",
            "80 Years": "make them look 100 years old, ancient, very old, detailed texture"
        }

        if st.button("INITIATE TIME WARP"):
            with st.spinner("⚡ GENERATING TEMPORAL FIELD... PLEASE WAIT..."):
                try:
                    # Using Instruct-Pix2Pix (The best "Edit" model)
                    edited_image = client.image_to_image(
                        "timbrooks/instruct-pix2pix",
                        image=original_image,
                        prompt=prompts[years],
                        image_guidance_scale=1.5, # Keep the face recognizable
                        guidance_scale=8.0       # Follow the instruction strongly
                    )
                    
                    st.success("TEMPORAL JUMP COMPLETE")
                    st.image(edited_image, caption=f"SUBJECT: +{years}")
                    
                except Exception as e:
                    st.error("⚠️ SYSTEM FAILURE: TIME PARADOX DETECTED")
                    st.write(f"Error Log: {e}")
                    st.info("Try again in 30 seconds. The time vortex is busy.")

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
