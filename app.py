import json
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# -------------------------------------------------------------------
# 1. Define Structured Pydantic Output Models
# -------------------------------------------------------------------
class Activity(BaseModel):
    time_slot: str = Field(description="Morning, Afternoon, or Evening block (e.g., 09:00 AM - 11:30 AM)")
    place_name: str = Field(description="Name of the attraction or restaurant")
    category: str = Field(description="Historical, Food, Nature, Shopping, Relaxation, etc.")
    description: str = Field(description="Short summary of what to do here")
    estimated_cost_usd: float = Field(description="Estimated cost in USD per person")

class DayPlan(BaseModel):
    day_number: int = Field(description="Day number of the trip (1, 2, 3...)")
    theme: str = Field(description="Theme for the day (e.g., Historic Downtown Exploration)")
    activities: List[Activity] = Field(description="List of ordered daily activities")
    daily_budget_usd: float = Field(description="Total estimated budget for this day")

class TripItinerary(BaseModel):
    destination: str = Field(description="Target city or region")
    total_days: int = Field(description="Duration of the trip")
    travel_style: str = Field(description="Budget, Luxury, Adventure, Relaxed, Family")
    overall_budget_usd: float = Field(description="Total estimated trip cost")
    packing_tips: List[str] = Field(description="Essential items to pack")
    days: List[DayPlan] = Field(description="Day-by-day plan")

# -------------------------------------------------------------------
# 2. Initialize LLM
# -------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# -------------------------------------------------------------------
# 3. Define Specialized Agents
# -------------------------------------------------------------------
researcher = Agent(
    role="Destination Researcher",
    goal="Find top-rated local hidden gems, iconic landmarks, and dining options for {destination}.",
    backstory="You are a seasoned travel guide who knows every city's culture, food scene, and weather quirks.",
    verbose=True,
    llm=llm
)

logistics_expert = Agent(
    role="Logistics & Route Optimizer",
    goal="Cluster attractions geographically to ensure efficient routing and accurate time budgets.",
    backstory="An expert tour coordinator who ensures travelers spend time enjoying destinations rather than stuck in traffic.",
    verbose=True,
    llm=llm
)

concierge = Agent(
    role="Lead Travel Concierge",
    goal="Synthesize research and route logistics into a cohesive, structured JSON travel plan.",
    backstory="A luxury concierge known for creating seamless, tailored day-by-day itineraries.",
    verbose=True,
    llm=llm
)

# -------------------------------------------------------------------
# 4. Define Agent Tasks
# -------------------------------------------------------------------
research_task = Task(
    description=(
        "Research the destination '{destination}' for a {days}-day trip. "
        "Style: {travel_style}. Focus areas: {interests}."
    ),
    expected_output="A comprehensive list of top attractions, local spots, and meal recommendations.",
    agent=researcher
)

logistics_task = Task(
    description=(
        "Take the researched spots for {destination} and organize them into {days} daily schedules. "
        "Group nearby places together to eliminate unnecessary transit. "
        "Ensure realistic time windows (e.g., Morning, Afternoon, Evening)."
    ),
    expected_output="A logically ordered, daily clustered itinerary draft with estimated costs.",
    agent=logistics_expert,
    context=[research_task]
)

itinerary_task = Task(
    description=(
        "Convert the finalized daily schedule into the strictly structured format matching TripItinerary. "
        "Calculate accurate overall budget totals and include 3-4 specific packing tips."
    ),
    expected_output="A validated structured Pydantic object representing the full travel itinerary.",
    agent=concierge,
    context=[logistics_task],
    output_pydantic=TripItinerary
)

# -------------------------------------------------------------------
# 5. Execution Function
# -------------------------------------------------------------------
def generate_ai_trip(destination: str, days: int, travel_style: str, interests: str):
    trip_crew = Crew(
        agents=[researcher, logistics_expert, concierge],
        tasks=[research_task, logistics_task, itinerary_task],
        process=Process.sequential
    )

    result = trip_crew.kickoff(
        inputs={
            "destination": destination,
            "days": days,
            "travel_style": travel_style,
            "interests": interests
        }
    )
    
    return result

# -------------------------------------------------------------------
# 6. Run Example
# -------------------------------------------------------------------
if __name__ == "__main__":
    plan = generate_ai_trip(
        destination="Kyoto, Japan",
        days=2,
        travel_style="Cultural & Foodie (Mid-range Budget)",
        interests="Ancient temples, street food, traditional tea, bamboo forests"
    )
    
    # Access structured output directly
    itinerary_data: TripItinerary = plan.pydantic
    print("\n================ GENERATED ITINERARY ================")
    print(json.dumps(itinerary_data.model_dump(), indent=2))
