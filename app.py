import os
import requests
from IPython.display import Markdown, display
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
print("Module Loaded Successfully ji")

import os
os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6IUtK4yFgD5K_YRNvd8YLsuPeH2Rl_ubqQl1OV3nNVltA"
os.environ["TAVILY_API_KEY"] = "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"
os.environ["OPENWEATHER_API_KEY"] = "585ffe080f9537ffdbecceda8cba7e88"
os.environ["GOOGLE_PLACES_API_KEY"] = "AIzaSyAUBJVyEQnpImB6d-1kPT_cdFIuwd_pTaE"
print("Done Paji")

model = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    google_api_key = os.environ["GOOGLE_API_KEY"]
)
response=model.invoke("hello buddy")
print(response.content)



trip_prompt = ChatPromptTemplate.from_template("""
You are an advanced AI Travel Planner and professional tour consultant. Generate a complete, personalized, realistic, and optimized travel itinerary based on the user's inputs.

Collect the following information:
- Name
- Source
- Destination
- Departure Date
- Return Date
- Number of Days
- Number of Travelers
- Adults, Children, Seniors
- Budget
- Currency
- Travel Style
- Hotel Category
- Transportation Preference
- Food Preference
- Interests
- Activity Level
- Special Requirements
- Languages Spoken
- Passport/Visa Status (if international)
- Weather Preference
- Maximum Daily Budget
- Medical Conditions
- Check-in Time
- Check-out Time
- Places to Avoid

Plan the trip by considering:
- Current season and weather
- Best time to visit attractions
- Opening and closing hours
- Travel distance and duration
- Traffic conditions where possible
- User budget and preferences

Generate:
- Day-wise itinerary (Day 1 to Last Day)
- Morning, Afternoon, Evening, and Night schedule
- Top attractions and hidden gems
- Estimated travel time between locations
- Best transport for each route
- Hotel recommendations
- Restaurant recommendations
- Local food suggestions
- Daily and total cost breakdown
- Packing checklist
- Weather advice
- Safety tips
- Local customs and etiquette
- Useful local phrases (if international)
- Shopping markets and souvenirs
- Nearby attractions for extra time
- Emergency contacts and nearby hospitals
- Google Maps route order
- Walking distances where applicable
- Top 10 must-visit places with ratings
- Money-saving tips

Present the final itinerary in a clean, professional format using headings, tables, bullet points, emojis, and a trip summary with the total estimated budget, travel distance, and personalized recommendations.
""")

trip_chain = (
    trip_prompt
    | model
    | StrOutputParser()

)
name = input("Name : ")
source = input("Source City : ")
destination = input("Destination : ")
travel_date = input("Travel Date : ")
return_date = input("Return Date : ")
days = input("Trip Days : ")
budget = input("Budget : ")
travelers = input("Number of Travelers : ")
travel_style = input("Travel Style : ")
hotel_type = input("Hotel Preference : ")
transport = input("Transport : ")
food = input("Food Preference : ")
interests = input("Interests : ")
must_visit = input("Must Visit Places : ")
special = input("Special Requirements : ")


trip_plan = trip_chain.invoke({

    "name": name,

    "source": source,

    "destination": destination,

    "travel_date": travel_date,

    "return_date": return_date,

    "days": days,

    "budget": budget,

    "travelers": travelers,

    "travel_style": travel_style,

    "hotel_type": hotel_type,

    "transport": transport,

    "food": food,

    "interests": interests,

    "must_visit": must_visit,

    "special": special

})

display(Markdown(trip_plan))

filename = f"{name}_Trip_Plan.txt"

with open(filename, "w", encoding="utf-8") as f:

    f.write(trip_plan)

print("Trip plan saved successfully.")

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate(f"{name}_Trip_Plan.pdf")

styles = getSampleStyleSheet()

story = [Paragraph(trip_plan.replace("\n", "<br/>"), styles["BodyText"])]

doc.build(story)

print("PDF Saved Successfully")
