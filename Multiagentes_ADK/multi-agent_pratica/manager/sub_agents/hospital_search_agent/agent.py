from google.adk.agents import Agent
from google.adk.tools import google_search

hospital_search_agent = Agent(
    name="hospital_search_agent",
    model="gemini-2.5-flash",
    description="Agent responsible for finding nearby health units such as hospitals, UPAs and clinics based on the user's location",
    instruction="""
                You are an agent specialized in finding health units.
                When activated, you must:
                1. Ask the user for their location (city and neighborhood if possible)
                2. Use google_search to find hospitals, UPAs and clinics near 
                the informed location
                3. Present the results in an organized way with name, address 
                and type of unit when available
                """,
    tools=[google_search],
)