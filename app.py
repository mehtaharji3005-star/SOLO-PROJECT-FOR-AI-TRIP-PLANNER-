import os
import requests
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# App Layout & Configuration
st.set_page_config(
    page_title="AI Trip Planner Pro", 
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Advanced Luxury/Modern UI
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Header Container Styling */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Custom Card Style Containers */
    .custom-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    
    /* Custom Tab Formatting */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Stylish Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 14px 28px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.6);
    }
    
    /* Sidebar Aesthetics */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# Display background banner image
try:
    st.image("bg.png", use_container_width=True)
except Exception:
    pass

st.markdown('<h1 class="hero-title">AI TRIP PLANNER ✈️ 🚗</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Craft your luxury tailored itinerary powered by advanced AI</p>', unsafe_allow_html=True)

# Sidebar - API Keys setup
with st.sidebar:
    st.title("🔑 API Settings")
    st.caption("Provide required API credentials below")
    
    GOOGLE_API_KEY = st.text_input("GOOGLE_API_KEY", type="password", help="Required for Gemini Model")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

    TAVILY_API_KEY = st.text_input("TAVILY_API_KEY", type="password")
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

    OPENWEATHER_API_KEY = st.text_input("OPENWEATHER_API_KEY", type="password")
    os.environ["OPENWEATHER_API_KEY"] = OPENWEATHER_API_KEY

    GOOGLE_PLACES_API_KEY = st.text_input("GOOGLE_PLACES_API_KEY", type="password")
    os.environ["GOOGLE_PLACES_API_KEY"] = GOOGLE_PLACES_API_KEY

    all_API = [OPENWEATHER_API_KEY, TAVILY_API_KEY, GOOGLE_API_KEY, GOOGLE_PLACES_API_KEY]

    if not all(all_API):
        st.error("❌ Please provide all API keys to proceed.")
    else:
        st.success("✅ All API keys loaded successfully.")

# Main Form Inputs organized with Modern Tabs
tab1, tab2 = st.tabs(["📋 Trip Essentials", "🎨 Preferences & Customization"])

with tab1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("Basic Travel Information")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Your Name", value="Alex")
        source = st.text_input("Source City", placeholder="e.g., New York")
        destination = st.text_input("Destination City", placeholder="e.g., Paris")
        travel_date = st.date_input("Travel Date")
        
    with col2:
        language = st.selectbox(
            "Preferred Itinerary Language",
            ["English", "Spanish", "French", "German", "Italian", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
        )
        budget = st.text_input("Budget (with currency)", placeholder="e.g., $2000 USD, ₹50,000 INR")
        return_date = st.date_input("Return Date")
        
    c1, c2 = st.columns(2)
    with c1:
        days = st.number_input("Number of Days", min_value=1, value=5)
    with c2:
        travelers = st.number_input("Number of Travelers", min_value=1, value=2)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("Styles & Specific Preferences")
    col3, col4 = st.columns(2)

    with col3:
        travel_style = st.selectbox(
            "Travel Style", 
            ["Relaxed", "Balanced", "Fast-paced", "Luxury", "Backpacker"]
        )

        hotel_type = st.selectbox(
            "Hotel Preference", 
            ["Budget", "3-Star", "4-Star", "5-Star Luxury", "Hostel"]
        )

        transport = st.selectbox(
            "Transport Preference", 
            ["Public Transport", "Rental Car", "Taxi/Uber", "Walking"]
        )    

        food = st.text_input("Food Preference", placeholder="e.g., Vegetarian, Vegan, Halal, Local Cuisine")

    with col4:
        interests = st.multiselect(
            "Interests", 
            ["Museums", "Architecture", "Photography", "Food & Dining", "Nature & Hiking", "Shopping", "Nightlife", "History"],
            default=["Museums", "Architecture"]
        )

        must_visit = st.multiselect(
            "Must Visit Places", 
            ["Eiffel Tower", "Louvre Museum", "Colosseum", "Taj Mahal", "Statue of Liberty", "Central Park", "Custom Spot"],
            default=["Eiffel Tower"]
        )

        special = st.multiselect(
            "Special Requirements", 
            ["Wheelchair accessibility", "Quiet nights", "Pet friendly", "Kid friendly", "Senior friendly"],
            default=["Wheelchair accessibility"]
        )
    st.markdown('</div>', unsafe_allow_html=True)

# LangChain Prompt Template
trip_prompt = ChatPromptTemplate.from_template("""
You are an advanced AI Travel Planner and professional tour consultant. Generate a complete, personalized, realistic, and optimized travel itinerary based on the user's inputs.

User Details:
- Name: {name}
- Source: {source}
- Destination: {destination}
- Departure Date: {travel_date}
- Return Date: {return_date}
- Duration: {days} Days
- Travelers: {travelers}
- Budget: {budget}
- Travel Style: {travel_style}
- Hotel Category: {hotel_type}
- Transportation Preference: {transport}
- Food Preference: {food}
- Interests: {interests}
- Must Visit Places: {must_visit}
- Special Requirements: {special}
- Preferred Output Language: {language}

CRITICAL INSTRUCTION: Generate the ENTIRE itinerary in {language}. 

Generate:
- Day-wise itinerary (Day 1 to Last Day) with Morning, Afternoon, Evening, and Night schedules
- Top attractions and hidden gems
- Estimated travel time between locations
- Hotel and Restaurant recommendations
- Daily and total cost breakdown
- Packing checklist & Weather advice
- Safety tips and local customs
- Emergency contacts and nearby hospitals

Present the final itinerary using clean markdown headings, bullet points, and tables.
""")

st.write("")
if st.button("🚀 Generate Optimized Itinerary"):
    if not all(all_API):
        st.error("❌ Please provide all API keys in the sidebar to proceed.")
        st.stop()
        
    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.startswith("AIza"):
        st.error("❌ Invalid GOOGLE_API_KEY. Please provide a valid key starting with 'AIza' from Google AI Studio.")
        st.stop()
        
    with st.spinner(f"✨ Crafting your personalized trip itinerary in {language}..."):
        try:
            # Explicitly pass api_key and set vertexai=False
            model = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                google_api_key=GOOGLE_API_KEY,
                vertexai=False
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
                "language": language
            })

            # Display Itinerary in visual Card Container
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader(f"📍 Personalized Itinerary for {name}")
            st.markdown(trip_plan)
            st.markdown('</div>', unsafe_allow_html=True)

            # File Saving
            filename_txt = f"{name}_Trip_Plan.txt"
            with open(filename_txt, "w", encoding="utf-8") as f:
                f.write(trip_plan)

            # PDF Generation
            filename_pdf = f"{name}_Trip_Plan.pdf"
            doc = SimpleDocTemplate(filename_pdf)
            styles = getSampleStyleSheet()
            story = [Paragraph(trip_plan.replace("\n", "<br/>"), styles["BodyText"])]
            doc.build(story)

            st.success(f"🎉 Trip plan saved locally as {filename_txt} and {filename_pdf}!")

            # Downloads bar
            st.subheader("📥 Export Your Itinerary")
            d_col1, d_col2 = st.columns(2)
            
            with d_col1:
                st.download_button(
                    label="📄 Download Text File (.txt)",
                    data=trip_plan,
                    file_name=filename_txt,
                    mime="text/plain"
                )
            
            with d_col2:
                with open(filename_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="📕 Download PDF Document (.pdf)",
                        data=pdf_file,
                        file_name=filename_pdf,
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"An error occurred while generating the itinerary: {e}")
