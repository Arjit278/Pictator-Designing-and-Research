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
st.set_page_config(page_title="Pictator Pro 2026", page_icon="🏎️", layout="wide")

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- CEO TRUSTED DOMAIN LIST (2026 Master List) ---
TRUSTED_DOMAINS = [
    "https://za.pinterest.com/search/pins/?q=seat%20covers", "autofit.in", "autotextile.com", "cncstitching.com",
    "seatcoversunlimited.com", "foamvilla.com", "sa.made-in-china.com",
    "autoclint.com", "autoform.in", "coverking.com", "katzkin.com",
    "amazon.in", "autofurnish.com", "elegantautoretail.com", "carwale.com"
]

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

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
        # Increase num to 60 to ensure we have enough diversity to select 9 perfect links
        params = {
            "engine": "google_images", 
            "q": f"{query} car seat covers leather 2028 design", 
            "api_key": SERP_API_KEY, 
            "num": 60
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        
        pinterest_refs = []
        random_refs = []
        used_domains = set() # Tracks the 'source' name to prevent repetition

        for i in results:
            source_name = i.get("source", "").strip()
            link = i.get("link", "").lower()
            original_img = i.get("original")
            
            # Skip if crucial data is missing or we already have this domain
            if not original_img or not link or source_name in used_domains:
                continue
            
            # Identify source type
            is_pinterest = "pinterest" in link or "pinterest" in source_name.lower()
            
            ref_data = {
                "img": original_img, 
                "link": i.get("link"), 
                "src": source_name
            }

            # 📌 Bucket 1: Pinterest Trends (Strictly 3)
            if is_pinterest and len(pinterest_refs) < 3:
                pinterest_refs.append(ref_data)
                used_domains.add(source_name)
                
            # 🏢 Bucket 2: Non-Pinterest/Random Industry Domains (Strictly 6)
            elif not is_pinterest and len(random_refs) < 6:
                random_refs.append(ref_data)
                used_domains.add(source_name)
            
            # Stop once we have our perfect 9-image blend (6 Random, 3 Pinterest)
            if len(pinterest_refs) >= 3 and len(random_refs) >= 6:
                break
        
        # Merge lists, keeping Pinterest first for the layout
        merged_refs = pinterest_refs + random_refs
                
        return merged_refs
    except Exception as e:
        st.sidebar.error(f"Search Engine Timeout (9-Image Pipeline): {e}")
        return []

                           
# --------------------------------------
# 🎯 UI: SMART CONFIGURATOR
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": {"id": "black-forest-labs/FLUX.1-schnell", "provider": "huggingface"},
    "🔥 FLUX.1 Dev": {"id": "black-forest-labs/FLUX.1-dev", "provider": "huggingface"},
    "✨ Stable Diffusion XL": {"id": "stabilityai/stable-diffusion-xl-base-1.0", "provider": "huggingface"},
    "Gemini Imagen 3 (Google Precise Free)": {
        "id": "gemini-2.5-flash-image",
        "provider": "google-imagen",
        "negative_prompt": False
    }
}
selected_model = st.sidebar.selectbox("Choose AI Model", list(MODEL_OPTIONS.keys()))

with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
    colA, colB, colC = st.columns(3)
    with colA:
        car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Custom/Other"])
        pattern = st.selectbox("Stitching", ["Hex-Cell", "Puff", "Minimalist Flat", "Diamond Stitching", "Custom-Prompt Based"])
    with colB:
        material = st.selectbox("Material", ["1200 GSM Nappa", "Cotton", "Synthetic Leather", "Carbon Fiber Leather", "Custom-Prompt Based"])
        colors = st.text_input("Colorway", value="Tan & Charcoal")
    with colC:
        lighting = st.selectbox("Lighting", ["Studio", "Blueprint", "Cinematic Showroom", "Custom"])
        market = st.selectbox("Market Tier", ["Luxury", "Affordable", "Sports", "OEM Upgrade", "Custom"])
    
    custom_instruction = st.text_area("✍️ Custom Engineering Instructions", placeholder="Add specific details like contrast piping or perforation...")

# ==========================================
# 🪡 STRUCTURAL & PATCH SELECTION
# ==========================================
st.markdown("### 🪡 Structural Enhancements")
patch_cols = st.columns(2)
with patch_cols[0]:
    patch_loc = st.selectbox(
        "Patch Support Location", 
        ["None", "Shoulder Support", "Seat Back Bolsters", "Seat Base/Seat Pan", "Bolsters", "Back side Bolsters+base side Bolsters", "Custom-Prompt Based"], 
        help="Select structural accent location for the seat cover."
    )
    quilt_designs = st.multiselect(
        "Select Quilt Designs (Cycles through selections per generated image)", 
        ["Elongated Hexagons & Hex-Stitch", "Ultra-Quilt Diamond", "Minimalist Channel Tucks", "Perforated Micro-Quilting", "Custom-Prompt Based"], 
        default=["Elongated Hexagons & Hex-Stitch"]
    )
with patch_cols[1]:
    patch_color = st.selectbox(
        "Patch Color", 
        ["Ivory White", "Neon Lime/Cyber Yellow", "Beige", "Cream", "Slate Grey", "Silver", "Blue", "Crimson Red", "Black", "Tan/Saddle Brown", "Custom-Prompt Based"], 
        disabled=(patch_loc == "None")
    )

st.divider()

# ==========================================
# 🧵 PIPING & STITCHING DETAILS
# ==========================================
st.markdown("### 🧵 Accent Details (Piping & Stitching)")
accent_cols = st.columns(2)

with accent_cols[0]:
    enable_piping = st.toggle("Enable Dynamic Custom Piping", value=True)
    if enable_piping:
        piping_colors = st.multiselect(
            "Select Piping Colors (Cycles through selections per generated image)",
            ["Tarocco Orange", "Austin Gold", "Desert Sand/Peach", "Metallic Silver", "Sky Blue", "Gloss Black", "Chalk/Off-White", "Alabaster Cream", "Matching Contrast", "Magenta", "Custom"],
            # Fixed: The defaults now match the available options in the list above.
            default=["Tarocco Orange", "Austin Gold", "Desert Sand/Peach"],
            key="piping_colors_select"
        )
    else:
        piping_colors = []

with accent_cols[1]:
    enable_stitching = st.toggle("Enable Dynamic Custom Stitching", value=True)
    if enable_stitching:
        stitching_colors = st.multiselect(
            "Select Stitching Colors (Cycles through selections per generated image)",
            ["Burnt Orange", "Austin Gold/Kyalami Gold", "Metallic Silver", "Salmon Peach/Desert Sand", "Electric Blue", "Obsidian Black/Piano Gloss Black", "Yas Marina-Blue/Miami-Blue", "True White", "Racing Yellow", "Macadamia/Alabaster Cream", "Rubystone Magenta/Viola Parsifae"],
            # Fixed: The defaults now match the available options in the list above.
            default=["Burnt Orange", "Austin Gold/Kyalami Gold", "Metallic Silver"],
            key="stitching_colors_select"
        )
    else:
        stitching_colors = []

st.divider()

# ==========================================
# 🖼️ GENERATION SETTINGS
# ==========================================
st.markdown("### 🖼️ Concept Generation Matrix")
num_images = st.select_slider("Number of Concept Variations to Generate", options=[1, 3, 5], value=1)

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE FULL SUITE"):
    generated_concepts = []
    
    with st.status("Engineering Intelligence...") as status:
        st.write(f"🎨 Generating {num_images} AI Design Concept(s)...")
        
        for i in range(num_images):
            # 1. Determine Piping & Stitching Selection with Hyper-Isolated Prompt Guardrails
            current_piping = "Standard"
            current_stitching = "Standard"
            piping_phrase = ""
            stitching_phrase = ""
            
            if enable_piping and piping_colors:
                current_piping = piping_colors[i % len(piping_colors)]
                # Prevents color bleeding by strictly assigning the color ONLY to perimeter borders
                piping_phrase = f" The solid outer border edge piping must be colored strictly and exclusively in {current_piping}."
                
            if enable_stitching and stitching_colors:
                current_stitching = stitching_colors[i % len(stitching_colors)]
                # Forces the model to separate thread lines from edge leather piping
                stitching_phrase = f" Distinct from the piping, all interior seam stitching must be sewn explicitly with {current_stitching} colored thread."
                
            accent_phrase = f"{piping_phrase}{stitching_phrase}"
            
            # 1b. Determine Quilt Design for this iteration
            current_quilt = "Standard"
            quilt_phrase = ""
            if quilt_designs:
                current_quilt = quilt_designs[i % len(quilt_designs)]
                quilt_phrase = f" featuring premium {current_quilt} quilt elements on the center inserts,"
            
            # 2. Determine Strict Spatial Patch Logic
            patch_phrase = ""
            if patch_loc == "Shoulder Support":
                patch_phrase = f" broad {patch_color} structural side patches positioned exclusively on the upper shoulder bolsters (left and right edges only, keeping center clear),"
            elif patch_loc == "Seat Back Bolsters":
                patch_phrase = f" broad {patch_color} structural side strips positioned exclusively on the left and right vertical side bolsters of the seat back (keeping center clear),"
            elif patch_loc == "Seat Base/Seat Pan":
                patch_phrase = f" broad {patch_color} structural side strips positioned exclusively on the left and right horizontal base side bolsters of the seat base (keeping center clear),"
            elif patch_loc == "Bolsters":
                patch_phrase = f" broad {patch_color} padded side sections on the backrest and horizontal base center bolsters (keeping center inserts clear),"
            elif patch_loc == "Back side Bolsters+base side Bolsters":
                patch_phrase = f" broad {patch_color} structural side patches running exclusively along the full outer side bolsters of both the seat back and the seat base (left and right edges only, keeping center clear),"
            
            # 3. FINAL RE-ENGINEERED PROMPT: Notice structural separation
            iteration_prompt = (
                f"Professional close-up automotive interior photography, {car} custom seat covers. "
                f"CRITICAL DESIGN RULES:{patch_phrase}{accent_phrase}{quilt_phrase} "
                f"Base design template: {pattern} pattern layout, premium {material} fabrication, {colors} primary colorway. "
                f"{custom_instruction}. {lighting} lighting matrix, 8k ultra-realistic studio output, material macro fabric detail."
            )
            
            # Generate Image (Handling Dictionary Config)
            img = generate_ai_image(iteration_prompt, MODEL_OPTIONS[selected_model])
            if img:
                generated_concepts.append((img, current_piping, current_stitching, current_quilt))
                
            # Buffer for Gemini Free Tier limits to prevent 429 Too Many Requests errors
            if selected_model == "Gemini Imagen 3 (Google Precise Free)" and i < num_images - 1:
                time.sleep(6.5) 
                
        st.write("🌐 Fetching Real-World Market References...")
        market_refs = fetch_market_references(f"{car} {material} seat cover")
        
        st.write("📊 Analyzing Material Trends...")
        analysis = call_openrouter(f"Briefly analyze durability and 2026 trends for {material} with {pattern} stitching.")
        
        status.update(label="✅ Analysis & Generation Complete", state="complete")
        
    # --- MATRIX DISPLAY UI ---
    st.markdown("---")
    
    # Render generated images vertically for FULL native resolution inspection
    st.subheader("🎨 AI-Generated Design Matrix (High-Resolution Inspection)")
    if generated_concepts:
        for idx, (img, piping, stitching, quilt) in enumerate(generated_concepts):
            st.markdown(f"#### Variant {idx+1} | {piping} Piping | {stitching} Stitching | {quilt} Pattern")
            
            # Displaying directly in the main container forces maximum native size
            st.image(img, use_container_width=True)
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("💾 Save Concept", buf.getvalue(), f"design_2026_v{idx+1}.png", key=f"dl_btn_{idx}")
            st.divider()

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("🌍 Verified Market References & Live Shop Links (6 Random | 3 Pinterest)")
        if market_refs:
            # Re-separate for UI grouping
            pin_ui_refs = [r for r in market_refs if "pinterest" in r["src"].lower() or "pinterest" in r["link"].lower()]
            random_ui_refs = [r for r in market_refs if r not in pin_ui_refs]
            
            # 📌 Dedicated 3-Column Pinterest Trend Anchor Row
            if pin_ui_refs:
                st.markdown("#### 📌 Top Pinterest Design Anchors (Strict Prompt-Based)")
                cols_pin = st.columns(3)
                # Take exactly 3 or what's available if fewer found
                for idx, ref in enumerate(pin_ui_refs[:3]):
                    with cols_pin[idx]:
                        # Use a container so the link button stays attached to the image
                        with st.container():
                            st.image(ref["img"], caption=f"Trend Ref {idx+1}", use_container_width=True)
                            st.link_button("🔗 View on Pinterest", ref["link"], use_container_width=True)
                st.write("") # Spacer
            
            # 🏢 6-Image Random Industry/Factory Domain Grid (Strict Prompt-Based)
            if random_ui_refs:
                st.markdown("#### 🏢 Factory & Industry Live Market Specifications")
                # Use a 3-column grid for the 6 images, which creates 2 rows naturally
                cols_rand = st.columns(3)
                # Take exactly 6 or what's available
                for idx, ref in enumerate(random_ui_refs[:6]):
                    # Cycle through columns based on index
                    with cols_rand[idx % 3]:
                        with st.container():
                            st.image(ref["img"], caption=f"Market Ref {idx+1} from {ref['src']}", use_container_width=True)
                            st.link_button(f"🔗 View on {ref['src']}", ref["link"], use_container_width=True)
                            
    with col_right:
        st.subheader("📈 Flashmind Analysis")
        st.info(analysis)

    # Compliance & Legal Expansion
    with st.expander("📊 2026 Tech & Model Trends & Legal Governance"):
        st.write("- **AI Concepts:** Generated via Top Models are virtual prototype, customized and crafted by user, for prototype visualization.")
        st.write("- **Market Refs:** Sourced via SERP to ensure engineering feasibility.")
        st.markdown("""
            **Zero Data Retention (ZDR) & Compliance Commitment:**
            - **Non-Storage:** Prompts and generated designs are processed in volatile memory. 
            - **Zero Training:** Your proprietary design logic is never used to train Omnicore & Pictator.
            - **Encryption:** All API calls use TLS 1.3 encryption for end-to-end security.
            - **Intellectual Property:** All software architecture, customized tool outputs, and generated visual schemas remain exclusive IP.
            - **Jurisdiction:** All commercial and software liabilities are governed legally under the sole jurisdiction of the Gurugram Court, Haryana.
            """)
