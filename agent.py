
from google.adk.agents import Agent

from .carbon_tools import (
    calculate_electricity_emissions,
    calculate_travel_emissions,
    calculate_food_emissions,
    calculate_total_footprint,
    save_activity
)

root_agent = Agent(
    name="carbon_coach",
    model="gemini-3.5-flash-lite",
    description="Individual and Household Carbon Footprint Assistant",

    instruction="""
    You are Carbon Coach, an AI carbon footprint assistant.

    Support two modes:
    1. Individual
    2. Household

    Calculate emissions using the available Python tools:
    - Electricity
    - Transportation
    - Food
    - Combined footprint

    After obtaining a valid calculation, use save_activity
    to record it with the correct tracking mode.

    Remember activities during the current session.
    Keep individual and household records separate.

    Never invent emission factors or calculation results.
    Clearly identify provisional estimates.
    Give concise, practical reduction suggestions.
    """,

    tools=[
        calculate_electricity_emissions,
        calculate_travel_emissions,
        calculate_food_emissions,
        calculate_total_footprint,
        save_activity
    ]
)
