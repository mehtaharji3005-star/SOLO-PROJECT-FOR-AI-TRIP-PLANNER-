import io
import os
import urllib.parse
from PIL import Image as PILImage
import requests
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Enterprise AI Trip Planner Pro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. SIDEBAR CONFIGURATION & THEME SELECTOR
# ==========================================
with st.sidebar:
    st.markdown("### 🎨 UI Color Theme")
    theme_choice = st.selectbox(
        "Choose Theme Style",
        ["Midnight Executive", "Emerald Luxe", "Royal Amethyst", "Minimal Light"],
    )

    st.markdown("---")
    st.markdown("### 🔑 API Configuration")
    st.caption("Enter enterprise keys below to enable LLM & search integration.")

    GOOGLE_API_KEY = st.text_input(
        "Google Gemini API Key", type="password", help="Required for Gemini Model"
    )
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

    TAVILY_API_KEY = st.text_input("Tavily Search API Key", type="password")
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

    OPENWEATHER_API_KEY = st.text_input("OpenWeather API Key", type="password")
    os.environ["OPENWEATHER_API_KEY"] = OPENWEATHER_API_KEY

    GOOGLE_PLACES_API_KEY = st.text_input("Google Places API Key", type="password")
    os.environ["GOOGLE_PLACES_API_KEY"] = GOOGLE_PLACES_API_KEY

    all_API = [
        OPENWEATHER_API_KEY,
        TAVILY_API_KEY,
        GOOGLE_API_KEY,
        GOOGLE_PLACES_API_KEY,
    ]

    st.markdown("---")
    if not all(all_API):
        st.info("ℹ️ Fill in all API keys to start planning.")
    else:
        st.success("✅ System Ready")


# ==========================================
# 3. DYNAMIC COLOR THEME ENGINE
# ==========================================
THEMES = {
    "Midnight Executive": {
        "bg": "#090d16",
        "card_bg": "rgba(15, 23, 42, 0.7)",
        "text": "#e2e8f0",
        "subtext": "#94a3b8",
        "title_grad": "linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%)",
        "btn_grad": "linear-gradient(90deg, #0284c7 0%, #2563eb 100%)",
        "btn_hover": "linear-gradient(90deg, #0369a1 0%, #1d4ed8 100%)",
        "tab_active": "#0284c7",
        "input_bg": "rgba(30, 41, 59, 0.5)",
        "border": "rgba(255, 255, 255, 0.08)",
        "sidebar_bg": "#0b0f19",
    },
    "Emerald Luxe": {
        "bg": "#06140e",
        "card_bg": "rgba(11, 33, 24, 0.75)",
        "text": "#ecfdf5",
        "subtext": "#6ee7b7",
        "title_grad": "linear-gradient(90deg, #34d399 0%, #a7f3d0 50%, #fef08a 100%)",
        "btn_grad": "linear-gradient(90deg, #059669 0%, #10b981 100%)",
        "btn_hover": "linear-gradient(90deg, #047857 0%, #059669 100%)",
        "tab_active": "#059669",
        "input_bg": "rgba(16, 185, 129, 0.1)",
        "border": "rgba(52, 211, 153, 0.15)",
        "sidebar_bg": "#030c08",
    },
    "Royal Amethyst": {
        "bg": "#0f0c1b",
        "card_bg": "rgba(28, 20, 50, 0.75)",
        "text": "#f5f3ff",
        "subtext": "#c084fc",
        "title_grad": "linear-gradient(90deg, #c084fc 0%, #f472b6 50%, #38bdf8 100%)",
        "btn_grad": "linear-gradient(90deg, #7c3aed 0%, #9333ea 100%)",
        "btn_hover": "linear-gradient(90deg, #6d28d9 0%, #7e22ce 100%)",
        "tab_active": "#7c3aed",
        "input_bg": "rgba(124, 58, 237, 0.15)",
        "border": "rgba(192, 132, 252, 0.15)",
        "sidebar_bg": "#0a0712",
    },
    "Minimal Light": {
        "bg": "#f8fafc",
        "card_bg": "#ffffff",
        "text": "#0f172a",
        "subtext": "#475569",
        "title_grad": "linear-gradient(90deg, #0284c7 0%, #4f46e5 100%)",
        "btn_grad": "linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)",
        "btn_hover": "linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%)",
        "tab_active": "#2563eb",
        "input_bg": "#f1f5f9",
        "border": "rgba(15, 23, 42, 0.1)",
        "sidebar_bg": "#f1f5f9",
    },
}

active_theme = THEMES[theme_choice]

st.markdown(
    f"""
<style>
    /* Dynamic Enterprise Theme */
    .stApp {{
        background-color: {active_theme['bg']};
        color: {active_theme['text']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .hero-container {{
        padding: 1.5rem 0 2rem 0;
        text-align: center;
        border-bottom: 1px solid {active_theme['border']};
        margin-bottom: 2rem;
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: {active_theme['title_grad']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    .hero-subtitle {{
        color: {active_theme['subtext']};
        font-size: 1.05rem;
        font-weight: 400;
    }}
    
    .custom-card {{
        background: {active_theme['card_bg']};
        border: 1px solid {active_theme['border']};
        border-radius: 14px;
        padding: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
    }}
    
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stMultiSelect > div {{
        background-color: {active_theme['input_bg']} !important;
        border: 1px solid {active_theme['border']} !important;
        color: {active_theme['text']} !important;
        border-radius: 8px !important;
    }}
    
    .stButton > button {{
        width: 100%;
        background: {active_theme['btn_grad']};
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.2);
        transition: all 0.25s ease-in-out;
    }}
    .stButton > button:hover {{
        background: {active_theme['btn_hover']};
        transform: translateY(-1px);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background-color: {active_theme['card_bg']};
        padding: 6px;
        border-radius: 10px;
        border: 1px solid {active_theme['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        color: {active_theme['subtext']};
        padding: 8px 18px;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {active_theme['tab_active']} !important;
        color: #ffffff !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {active_theme['sidebar_bg']};
        border-right: 1px solid {active_theme['border']};
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def generate_ai_image(destination_name):
    prompt = f"A high-end luxury architectural travel photograph of {destination_name}, 8k resolution, photorealistic, vibrant color grading, scenic lighting"
    encoded_prompt = urllib.parse.quote(prompt)
    return f"https://pollinations.ai/p/{encoded_prompt}?width=1200&height=675&seed=42&model=flux"


# ==========================================
# 5. MAIN HEADER & FORM INTERFACE
# ==========================================
st.markdown(
    """
<div class="hero-container">
    <div class="hero-title">ENTERPRISE AI TRIP PLANNER</div>
    <div class="hero-subtitle">Bespoke, Data-Driven Itineraries Powered by Advanced Generative Intelligence</div>
</div>
""",
    unsafe_allow_html=True,
)

input_tab1, input_tab2 = st.tabs(["📌 Core Trip Parameters", "🎯 Personalization & Preferences"])

with input_tab1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("##### ✈️ Primary Route & Details")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Client / Traveler Name", value="Alex")
        source = st.text_input("Departure City", placeholder="e.g., London, UK")
        destination = st.text_input("Destination City", placeholder="e.g., Kyoto, Japan")
        travel_date = st.date_input("Departure Date")

    with col2:
        language = st.selectbox(
            "Output Language",
            [
                "English",
                "Spanish",
                "French",
                "German",
                "Italian",
                "Hindi",
                "Japanese",
                "Chinese",
                "Portuguese",
                "Arabic",
            ],
        )
        budget = st.text_input("Budget Estimate", placeholder="e.g., $3,500 USD")
        return_date = st.date_input("Return Date")

    c1, c2 = st.columns(2)
    with c1:
        days = st.number_input("Duration (Days)", min_value=1, value=5)
    with c2:
        travelers = st.number_input("Travelers Count", min_value=1, value=2)
    st.markdown("</div>", unsafe_allow_html=True)

with input_tab2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("##### 🎨 Custom Experience Filters")
    col3, col4 = st.columns(2)

    with col3:
        travel_style = st.selectbox(
            "Pacing & Style",
            ["Balanced", "Relaxed", "Fast-paced", "Luxury", "Backpacker"],
        )
        hotel_type = st.selectbox(
            "Accommodation Level",
            ["5-Star Luxury", "4-Star", "3-Star", "Boutique", "Hostel"],
        )
        transport = st.selectbox(
            "Transit Preference",
            ["Private Chauffeur/Taxi", "Public Transport", "Rental Car", "Walking"],
        )
        food = st.text_input("Dietary Preferences", placeholder="e.g., Fine Dining, Vegetarian, Local Street Food")

    with col4:
        interests = st.multiselect(
            "Key Focus Areas",
            [
                "Architecture",
                "Culture & Museums",
                "Fine Dining",
                "Nature & Hiking",
                "Shopping",
                "Nightlife",
                "History",
                "Photography",
            ],
            default=["Culture & Museums", "Fine Dining"],
        )
        must_visit = st.multiselect(
            "Priority Attractions",
            [
                "Eiffel Tower",
                "Louvre Museum",
                "Colosseum",
                "Taj Mahal",
                "Fushimi Inari Shrine",
                "Custom Spot",
            ],
            default=["Louvre Museum"],
        )
        special = st.multiselect(
            "Special Requests",
            [
                "Wheelchair Accessibility",
                "Kid Friendly",
                "Senior Friendly",
                "Quiet Evenings",
                "Pet Friendly",
            ],
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 6. LLM PROMPT & GENERATION EXECUTION
# ==========================================
trip_prompt = ChatPromptTemplate.from_template("""
You are an executive travel manager. Generate a highly detailed, premium travel itinerary for:

User Profile:
- Name: {name} | Route: {source} to {destination}
- Dates: {travel_date} to {return_date} ({days} Days) | Travelers: {travelers}
- Budget: {budget} | Style: {travel_style} | Hotel: {hotel_type}
- Transport: {transport} | Dietary: {food}
- Interests: {interests} | Must Visit: {must_visit} | Special Requirements: {special}
- Preferred Language: {language}

CRITICAL INSTRUCTION: Write the ENTIRE response strictly in {language}. Use modern Markdown tables and bold headers.

Structure the itinerary:
1. Executive Summary & Trip Overview
2. Day-by-Day Detailed Itinerary (Morning, Afternoon, Evening, Night)
3. Dining & Hotel Recommendations
4. Cost & Budget Breakdown Table
5. Essential Travel Tips (Weather, Safety, Logistics)
""")

st.markdown("###")
if st.button("🚀 Generate Itinerary"):
    if not all(all_API):
        st.error("❌ Please fill in all required API credentials in the left sidebar.")
        st.stop()

    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.startswith:
        st.error("❌ Invalid GOOGLE_API_KEY format. Please check your credentials.")
        st.stop()

    with st.spinner("⏳ Synthesizing itinerary and generating AI visual assets..."):
        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                google_api_key=GOOGLE_API_KEY,
                vertexai=False,
            )
            trip_chain = trip_prompt | model | StrOutputParser()

            trip_plan = trip_chain.invoke({
                "name": name,
                "source": source,
                "destination": destination,
                "travel_date": str(travel_date),
                "return_date": str(return_date),
                "days": str(days),
                "budget": budget,
                "travelers": str(travelers),
                "travel_style": travel_style,
                "hotel_type": hotel_type,
                "transport": transport,
                "food": food,
                "interests": ", ".join(interests),
                "must_visit": ", ".join(must_visit),
                "special": ", ".join(special),
                "language": language,
            })

            dest_query = destination if destination else "Luxury Travel Destination"
            image_url = generate_ai_image(dest_query)

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(label="Passenger", value=name)
            m2.metric(label="Destination", value=dest_query)
            m3.metric(label="Duration", value=f"{days} Days")
            m4.metric(label="Estimated Budget", value=budget if budget else "N/A")

            out_tab1, out_tab2, out_tab3 = st.tabs(["🗓️ Full Itinerary", "🖼️ Destination Visual", "📥 Export Options"])

            with out_tab1:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown(trip_plan)
                st.markdown("</div>", unsafe_allow_html=True)

            with out_tab2:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.image(
                    image_url,
                    caption=f"AI Generated Visual Preview for {dest_query}",
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            filename_txt = f"{name}_{dest_query}_Itinerary.txt"
            with open(filename_txt, "w", encoding="utf-8") as f:
                f.write(trip_plan)

            filename_pdf = f"{name}_{dest_query}_Itinerary.pdf"
            doc = SimpleDocTemplate(filename_pdf)
            styles = getSampleStyleSheet()
            story = []

            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(image_url, headers=headers, timeout=10)

                if response.status_code == 200:
                    image_bytes = io.BytesIO(response.content)
                    pil_img = PILImage.open(image_bytes)
                    pil_img.verify()

                    image_bytes.seek(0)
                    pil_img = PILImage.open(image_bytes)

                    if pil_img.mode in ("RGBA", "P"):
                        pil_img = pil_img.convert("RGB")

                    temp_img_path = "temp_ai_image.jpg"
                    pil_img.save(temp_img_path, format="JPEG")

                    story.append(RLImage(temp_img_path, width=6.5 * inch, height=3.6 * inch))
                    story.append(Spacer(1, 15))
            except Exception:
                pass

            formatted_text = trip_plan.replace("\n", "<br/>")
            story.append(Paragraph(formatted_text, styles["BodyText"]))
            doc.build(story)

            with out_tab3:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown("##### Download Generated Reports")
                d_col1, d_col2 = st.columns(2)

                with d_col1:
                    st.download_button(
                        label="📄 Download Raw Text Report (.txt)",
                        data=trip_plan,
                        file_name=filename_txt,
                        mime="text/plain",
                    )

                with d_col2:
                    with open(filename_pdf, "rb") as pdf_file:
                        st.download_button(
                            label="📕 Download Executive PDF Document (.pdf)",
                            data=pdf_file,
                            file_name=filename_pdf,
                            mime="application/pdf",
                        )
                st.markdown("</div>", unsafe_allow_html=True)

            st.balloons()

        except Exception as e:
            st.error(f"An error occurred while generating the itinerary: {e}")
