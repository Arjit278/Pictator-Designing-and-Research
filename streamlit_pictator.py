import io
import requests
import streamlit as st
import json
import time
import re
from PIL import Image
from huggingface_hub import InferenceClient

# --------------------------------------
# 🔧 PAGE CONFIG & API
# --------------------------------------
st.set_page_config(page_title="Pictator Pro – Brake Design Suite", page_icon="🏎️", layout="wide")

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- CEO TRUSTED DOMAIN LIST (2026 Master List) ---
TRUSTED_DOMAINS = [
    "https://za.pinterest.com/search/pins/?q=seat%20covers", "brembo.com", "wilwood.com", "stoptech.com", "alcon.co.uk",
    "ferodo.com", "bosch.com", "zf.com", "trwaftermarket.com",
    "ap-racing.com", "mclaren.com", "pinterest.com",
    "amazon.in", "sa.made-in-china.com", "pinterest.com/search/pins/?q=seat%20covers", "pinterest.com", "carwale.com"
]

st.title("🛞 Pictator Pro – CNC Brake Design Engineering Suite")
st.caption("Strategic Parallel RCA | Disc Brake & Drum Brake Design | AI Concept + Market Intelligence")

# --------------------------------------
# 🔐 AUTHENTICATION
# --------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.title("🔐 Access Panel")
    if not st.session_state.authenticated:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Harmony" and pwd == "Harmony/Pictator123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    else:
        st.success("🟢 Logged in as Harmony")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.warning("🔐 Please login to continue")
    st.stop()

# --------------------------------------
# ⚡ FLASHMIND ENGINE (OPENROUTER)
# --------------------------------------
ANALYSIS_MODELS = [
    "Llama 3.3 70B Instruct (free)",
    "gpt-oss-20b",
    "Qwen3 Next 80B A3B Instruct (free)",
    "Qwen3 Coder 480B A35B (free)"
]

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in ANALYSIS_MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an automotive engineering expert."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=15
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except:
            continue
    return "Intelligence fallback active: Manual review required."

# --------------------------------------
# 🛠️ IMAGE & MARKET ENGINES
# --------------------------------------
def generate_ai_image(prompt, model_config):
    """GENERATE: Pure AI Design Concept"""
    try:
        if isinstance(model_config, str):
            model_id = model_config
            provider = "huggingface"
        else:
            model_id = model_config.get("id")
            provider = model_config.get("provider", "huggingface")

        if provider == "google-imagen":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "instances": [{"prompt": prompt}],
                "parameters": {"sampleCount": 1}
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                import base64
                data = response.json()
                img_b64 = data["predictions"][0]["bytesBase64Encoded"]
                img_bytes = base64.b64decode(img_b64)
                return Image.open(io.BytesIO(img_bytes))
            else:
                st.error(f"Gemini Generation Failed: HTTP {response.status_code}")
                return None
        else:
            client = InferenceClient(model=model_id, token=HF_TOKEN)
            return client.text_to_image(prompt, width=1024, height=768)
    except Exception as e:
        st.error(f"Generation Failed: {e}")
        return None

# ==========================================
# 🌐 PATCH 1: DATA ACQUISITION ENGINE
# Replace your existing def fetch_market_references(query): function with this:
# ==========================================
def fetch_market_references(query):
    try:
        # 1. Broaden Pinterest query to ensure it always returns high-quality aesthetic anchors
        pin_params = {
            "engine": "google_images",
            "q": "automotive disc brake caliper rotor drum brake design site:pinterest.com",
            "api_key": SERP_API_KEY,
            "num": 20
        }
        try:
            pin_r = requests.get("https://serpapi.com/search", params=pin_params, timeout=10)
            pin_results = pin_r.json().get("images_results", [])
        except:
            pin_results = []
        
        # 2. Main vehicle market query
        params = {
            "engine": "google_images", 
            "q": f"{query} automotive disc brake rotor caliper drum brake", 
            "api_key": SERP_API_KEY, 
            "num": 40
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        
        pinterest_refs = []
        trusted_refs = []
        used_images = set()

        # Extract 3 unique Pinterest design inspirations
        for i in pin_results:
            img_url = i.get("original")
            if img_url and img_url not in used_images:
                if len(pinterest_refs) < 3:
                    pinterest_refs.append({
                        "img": img_url, 
                        "link": i.get("link", "https://za.pinterest.com/search/pins/?q=seat%20covers"), 
                        "src": "Pinterest"
                    })
                    used_images.add(img_url)

        # Process general trusted domains for the factory specifications row
        for i in results:
            source_name = i.get("source", "").strip()
            link = i.get("link", "").lower()
            img_url = i.get("original")
            
            if not img_url or img_url in used_images:
                continue
                
            is_pinterest = "pinterest" in link or "pinterest" in source_name.lower()
            
            if is_pinterest:
                if len(pinterest_refs) < 3:
                    pinterest_refs.append({
                        "img": img_url, 
                        "link": i["link"], 
                        "src": "Pinterest"
                    })
                    used_images.add(img_url)
            else:
                is_trusted = any(td in link for td in TRUSTED_DOMAINS)
                if is_trusted and len(trusted_refs) < 3:
                    trusted_refs.append({
                        "img": img_url, 
                        "link": i["link"], 
                        "src": source_name
                    })
                    used_images.add(img_url)
            
            if len(pinterest_refs) >= 3 and len(trusted_refs) >= 3:
                break
        
        # Absolute fallback fill if thresholds are still missing entries
        if len(pinterest_refs) < 3 or len(trusted_refs) < 3:
            for i in results:
                img_url = i.get("original")
                source_name = i.get("source", "").strip()
                link = i.get("link", "").lower()
                
                if not img_url or img_url in used_images:
                    continue
                    
                is_pinterest = "pinterest" in link or "pinterest" in source_name.lower()
                if is_pinterest and len(pinterest_refs) < 3:
                    pinterest_refs.append({
                        "img": img_url,
                        "link": i["link"],
                        "src": "Pinterest"
                    })
                    used_images.add(img_url)
                elif not is_pinterest and len(trusted_refs) < 3:
                    trusted_refs.append({
                        "img": img_url,
                        "link": i["link"],
                        "src": source_name
                    })
                    used_images.add(img_url)
                    
                if len(pinterest_refs) >= 3 and len(trusted_refs) >= 3: 
                    break
                
        return pinterest_refs + trusted_refs
    except Exception as e:
        st.sidebar.error(f"Search Fallback Engaged: {e}")
        return []

                           
# --------------------------------------
# 🎯 UI: SMART BRAKE DESIGN CONFIGURATOR
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": {"id": "black-forest-labs/FLUX.1-schnell", "provider": "huggingface"},
    "🔥 FLUX.1 Dev": {"id": "black-forest-labs/FLUX.1-dev", "provider": "huggingface"},
}
selected_model = st.sidebar.selectbox("Choose AI Model", list(MODEL_OPTIONS.keys()))

with st.expander("🧠 Smart Brake Design Configurator", expanded=True):
    a, b, c = st.columns(3)
    with a:
        vehicle = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Custom Vehicle"])
        brake_type = st.selectbox("Brake Type", [
            "Disc Brake", "Drum Brake", "Front Disc + Rear Drum",
            "Front & Rear Disc", "Custom / Prompt Based"
        ])
        axle = st.selectbox("Axle", ["Front", "Rear", "Front & Rear", "Custom"])
    with b:
        rotor = st.selectbox("Rotor / Drum Design", [
            "Solid Rotor", "Vented Rotor", "Cross-Drilled Rotor",
            "Slotted Rotor", "Drilled + Slotted Rotor",
            "OEM Drum", "Performance Drum", "Custom / Prompt Based"
        ])
        caliper = st.selectbox("Caliper / Hardware", [
            "OEM Single-Piston", "Floating Caliper", "Fixed Multi-Piston",
            "Performance 4-Piston", "Performance 6-Piston",
            "Drum Shoe Assembly", "Custom / Prompt Based"
        ])
        material = st.selectbox("Material", [
            "Cast Iron", "High-Carbon Cast Iron", "Forged Aluminium",
            "Steel", "Aluminium + Steel", "Composite / Custom"
        ])
    with c:
        finish = st.selectbox("Finish", [
            "OEM Satin", "Brushed Metal", "Machined", "Gloss",
            "Matte", "Anodized", "Powder Coated", "Custom"
        ])
        lighting = st.selectbox("Photography / Visualization", [
            "Studio Product Photography", "Blueprint / CAD Presentation",
            "Cinematic Showroom", "Wheel-On Vehicle Photography",
            "Exploded Engineering View", "Custom"
        ])

    design_prompt = st.text_area(
        "✍️ Design Prompt / Idea",
        placeholder="Describe the brake design you want: rotor geometry, caliper style, color, finish, wheel visibility, cooling concept, branding, etc.",
        height=130
    )
    custom_instruction = st.text_area(
        "Additional Engineering Instructions",
        placeholder="Add dimensions, ventilation direction, slot pattern, mounting concept, thermal features, wheel clearance, or visual requirements.",
        height=100
    )

# ==========================================
# 🛠️ BRAKE DETAIL / DESIGN PATCHES
# ==========================================
st.markdown("### 🛠️ Brake Design Enhancements")
p1, p2 = st.columns(2)
with p1:
    component_focus = st.selectbox("Design Focus", [
        "Full Brake Assembly",
        "Brake Disc / Rotor Only",
        "Brake Drum Only",
        "Steering Knuckle Only",
        "Brake Plate / Pressure Plate Only",
        "Rotor + Caliper",
        "Drum + Backing Plate",
        "Custom-Prompt Based"
    ])
    details = st.multiselect("Component Details", [
        "Ventilation Channels",
        "Cross-Drilled Holes",
        "Directional Slots",
        "Curved Vanes",
        "Floating Two-Piece Rotor",
        "Machined Hat",
        "Cooling Fins",
        "Brake Shoe Detail",
        "Backing Plate Detail",
        "Pressure Plate Detail",
        "Casting / Machining Detail",
        "Custom-Prompt Based"
    ], default=["Ventilation Channels"])
with p2:
    features = st.multiselect("Engineering / Visual Features", [
        "Lightweight Design", "High Thermal Capacity", "Performance Appearance",
        "OEM+ Appearance", "Low-Dust Visual Concept",
        "Corrosion-Resistant Finish", "Wheel Clearance Focus",
        "Premium Machined Details", "Custom-Prompt Based"
    ], default=["OEM+ Appearance"])
st.divider()


# ==========================================
# 🖼️ GENERATION SETTINGS
# ==========================================
st.markdown("### 🖼️ Concept Generation Matrix")
num_images = st.select_slider("Number of Concept Variations to Generate", options=[1, 3, 5], value=1)

# --------------------------------------
# 🎯 STRICT IMAGE SUBJECT CONTROL
# --------------------------------------
st.info(
    "Image generation follows the selected Design Focus. "
    "Unrelated products or accessories are excluded unless explicitly requested "
    "in the design prompt."
)

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE BRAKE DESIGN SUITE"):
    brake_prompt = f"""
Create a professional automotive engineering design concept for {vehicle}.

PRIMARY COMPONENT — STRICT:
The image must primarily and clearly show ONLY the selected Design Focus:
{component_focus}.

Brake architecture: {brake_type}.
Axle: {axle}.
Rotor / drum specification: {rotor}.
Caliper / hardware specification: {caliper}.
Material: {material}.
Finish: {finish}.
Component details: {", ".join(details) if details else "standard"}.
Engineering / visual features: {", ".join(features) if features else "standard"}.
User design idea: {design_prompt or "Develop a premium OEM+ concept."}
Additional engineering instructions: {custom_instruction or "Maintain physically plausible automotive packaging."}
Visualization: {lighting}.

PRODUCT SCOPE:
If the selected focus is Brake Disc / Rotor Only, show the brake disc/rotor as the
hero product and do not introduce seat covers, upholstery, interior trim, piping,
threading, stitching, steering-wheel covers, or unrelated vehicle accessories.

If the selected focus is Brake Drum Only, show the brake drum as the hero product.
If the selected focus is Steering Knuckle Only, show the steering knuckle as the hero
product. If the selected focus is Brake Plate / Pressure Plate Only, show that plate
component as the hero product.

If the user prompt explicitly requests a specific component, follow that component
and do not substitute a different product. Do not add unrelated automotive products.

SUPPORTED PRODUCT CATEGORIES:
Automotive braking components include:
- Brake Discs: high-performance ventilated and solid brake rotors.
- Brake Drums: heavy-duty rear brake components.
- Steering Knuckles: precision-engineered suspension parts.
- Brake Plates & Pressure Plates: thermal-stable cast-iron plate components.

Non-automotive casting categories may be referenced only when explicitly requested:
- Cylinder Blocks: cast-condition engine blocks.
- Cylinder Heads: precision-cast components for machinery and engines.
- Crank Cases: castings primarily applied in compressors for the consumer durable sector.

VISUAL QUALITY:
Show realistic automotive manufacturing details, credible geometry, mounting
relationships, wheel clearance where relevant, ventilation/cooling features where
applicable, machined/cast surfaces, and professional product visualization.
For disc brakes, show credible rotor, hub/hat and caliper relationships only when
they are necessary to explain the selected design. For drum brakes, show credible
drum, backing plate, shoes and hardware only when relevant to the selected focus.

This is a concept visualization and not a certified safety-critical engineering drawing.
"""

    st.write(f"🎨 Generating {num_images} AI Brake Design Concept(s)...")
    progress = st.progress(0)
    generated_images = []

    for i in range(num_images):
        iteration_prompt = brake_prompt + f"\nDesign variation: {i + 1}"
        img = generate_ai_image(
            iteration_prompt,
            MODEL_OPTIONS[selected_model]
        )

        if img:
            generated_images.append(img)
            st.image(img, caption=f"Brake Design Concept {i + 1}", use_container_width=True)

        progress.progress((i + 1) / num_images)

    st.write("🌐 Fetching Real-World Market References...")
    market_refs = fetch_market_references(
        f"{vehicle} {brake_type} {rotor} {caliper}"
    )

    st.write("📊 Analyzing Brake Design Trends...")
    analysis = call_openrouter(
        f"Briefly analyze high-level 2026 trends for {brake_type}, "
        f"{rotor}, {caliper}, {material}, cooling, thermal management, "
        f"manufacturing and OEM+ automotive design."
    )

    if market_refs:
        st.markdown("### 🌐 Market References")
        for ref in market_refs:
            st.write(ref)

    if analysis:
        st.markdown("### 📊 Design & Market Analysis")
        st.write(analysis)

    if generated_images:
        st.success(f"Generated {len(generated_images)} brake design concept(s).")
    else:
        st.warning("No AI design image was generated. Check the selected AI model and credentials.")
