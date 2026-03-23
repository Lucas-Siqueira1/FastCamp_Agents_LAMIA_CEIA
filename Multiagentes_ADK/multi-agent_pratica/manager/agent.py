from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.analyst_agent.agent import analyst_agent
from .sub_agents.hospital_search_agent.agent import hospital_search_agent
from .sub_agents.outbreak_search_agent.agent import outbreak_search_agent

root_agent = Agent(
    name="manager",
    model="gemini-2.5-flash",
    description="Manager agent",
    instruction="""
                You are a health assistant coordinator responsible for managing 
                and orchestrating a team of specialized agents to help users who 
                are experiencing health issues.

                When the user describes their symptoms, you must follow this flow:

                1. Delegate to the health analysis agent to identify possible 
                conditions related to the reported symptoms

                2. After receiving the analysis, delegate to the outbreak search 
                agent to check for active health alerts related to the 
                identified conditions in the user's region

                3. Finally, delegate to the health units agent to find nearby 
                hospitals, UPAs and clinics where the user can seek treatment

                Always wait for each agent to complete their task before proceeding 
                to the next step. Compile all the information received and present 
                a clear and organized final summary to the user, containing:
                - Possible identified conditions
                - Active outbreak alerts in the region
                - Nearby health units available for treatment

                Remember to always be empathetic and remind the user that the 
                information provided does not replace a professional medical 
                consultation.
                """,
    tools=[
        AgentTool(hospital_search_agent),
        AgentTool(outbreak_search_agent),
    ],
)