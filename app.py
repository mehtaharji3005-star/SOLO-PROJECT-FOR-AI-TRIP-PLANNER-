import os
import requests
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# App Layout & Configuration
st.set_page_config(page_title="AI Trip Planner", page_icon="✈️", layout="wide")

st.sidebar.title("API Configuration")
st.title("AI TRIP PLANNER ✈️ 🚗")

# Sidebar - API Keys setup
st.sidebar.subheader("Provide Required API Keys")

GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API_KEY", type="password")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY", type="password")
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

OPENWEATHER_API_KEY = st.sidebar.text_input("OPENWEATHER_API_KEY", type="password")
os.environ["OPENWEATHER_API_KEY"] = OPENWEATHER_API_KEY

GOOGLE_PLACES_API_KEY = st.sidebar.text_input("GOOGLE_PLACES_API_KEY", type="password")
os.environ["GOOGLE_PLACES_API_KEY"] = GOOGLE_PLACES_API_KEY

all_API = [
    OPENWEATHER_API_KEY,
    TAVILY_API_KEY,
    GOOGLE_API_KEY,
    GOOGLE_PLACES_API_KEY,
]

if not all(all_API):
    st.error("❌ Please provide all API keys in the sidebar to proceed.")
    st.stop()
else:
    st.sidebar.success("✅ All API keys loaded successfully.")

# Main Form Inputs
st.header("Trip Details")
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Your Name")
    source = st.text_input("Source City")
    destination = st.text_input("Destination City")
    travel_date = st.date_input("Travel Date")
    return_date = st.date_input("Return Date")
    days = st.number_input("Number of Days", min_value=1, value=5)
    travelers = st.number_input("Number of Travelers", min_value=1, value=2)

with col2:
    budget = st.text_input("Budget (with currency))
    travel_style = st.selectbox("Travel Style", ["Relaxed", "Balanced", "Fast-paced", "Luxury", "Backpacker"])
    hotel_type = st.selectbox("Hotel Preference", ["Budget", "3-Star", "4-Star", "5-Star Luxury", "Hostel"])
    transport = st.selectbox("Transport Preference", ["Public Transport", "Rental Car", "Taxi/Uber", "Walking"])
    food = st.text_input("Food Preference", "Vegetarian / Local Cuisine")
    interests = st.text_input("Interests", "Museums, Architecture, Photography, Food")
    must_visit = st.text_input("Must Visit Places", "Eiffel Tower, Louvre Museum")
    special = st.text_input("Special Requirements", "Wheelchair accessibility, quiet nights")

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

if st.button("🚀 Generate Itinerary"):
    with st.spinner("Crafting your personalized trip itinerary..."):
        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=GOOGLE_API_KEY
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
                "interests": interests,
                "must_visit": must_visit,
                "special": special
            })

            st.markdown(trip_plan)

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

            st.success(f"Trip plan saved locally as {filename_txt} and {filename_pdf}!")

            # Streamlit Download Buttons
            st.download_button(
                label="📥 Download Itinerary (TXT)",
                data=trip_plan,
                file_name=filename_txt,
                mime="text/plain"
            )
            
            with open(filename_pdf, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Itinerary (PDF)",
                    data=pdf_file,
                    file_name=filename_pdf,
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"An error occurred while generating the itinerary: {e}")
