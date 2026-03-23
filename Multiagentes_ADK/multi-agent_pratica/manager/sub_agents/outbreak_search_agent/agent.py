from google.adk.agents import Agent
from google.adk.tools import google_search

outbreak_search_agent = Agent(
    name="outbreak_search_agent",
    model="gemini-2.5-flash",
    description="Agent responsible for searching for active disease outbreaks or health alerts in the user's region, based on the condition identified by the health analysis agent.",
    instruction="""
                You are an agent specialized in monitoring disease outbreaks and 
                health alerts.

                When activated, you must:
                1. Ask the user for their location (city and state)
                2. Use google_search to find active outbreaks or health alerts 
                related to the identified condition in the informed region
                3. Present the results in an organized way, informing:
                - Whether there are active alerts in the region
                - The severity level of the outbreak if available
                - Any official recommendations from health authorities

                If no outbreaks or alerts are found, clearly inform the user that 
                there are no active alerts for the region at the moment.
                """,
    tools=[google_search],
)