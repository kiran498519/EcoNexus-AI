
import sqlite3
from pathlib import Path

from google.adk.tools import ToolContext


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DB_PATH = Path(__file__).parent / "carbon_activities.db"


def initialize_database():
    """Create the permanent activity database."""

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_mode TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            emissions_kg_co2e REAL NOT NULL,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


initialize_database()


# ==================================================
# ELECTRICITY EMISSION CALCULATOR
# ==================================================

ELECTRICITY_FACTOR = 0.779


def calculate_electricity_emissions(kwh: float) -> dict:
    """Calculate electricity-related carbon emissions."""

    if kwh < 0:
        return {
            "error": "Electricity consumption cannot be negative."
        }

    emissions = kwh * ELECTRICITY_FACTOR

    return {
        "category": "electricity",
        "consumption_kwh": kwh,
        "emission_factor": ELECTRICITY_FACTOR,
        "emissions_kg_co2": round(emissions, 3),
        "unit": "kg CO2",
        "source": "CEA CO2 Baseline Database Version 22.0"
    }


# ==================================================
# TRANSPORTATION EMISSION CALCULATOR
# ==================================================

def calculate_travel_emissions(
    distance_km: float,
    transport: str
) -> dict:
    """Calculate transportation-related emissions."""

    emission_factors = {
        "car": 0.171,
        "bus": 0.105,
        "train": 0.041,
        "motorcycle": 0.103
    }

    transport = transport.lower().strip()

    if distance_km < 0:
        return {
            "error": "Distance cannot be negative."
        }

    if transport not in emission_factors:
        return {
            "error": "Choose car, bus, train, or motorcycle."
        }

    factor = emission_factors[transport]
    emissions = distance_km * factor

    return {
        "category": "travel",
        "transport": transport,
        "distance_km": distance_km,
        "emission_factor": factor,
        "emissions_kg_co2e": round(emissions, 3),
        "unit": "kg CO2e",
        "source": (
            "Illustrative default factors; "
            "replace with verified source-specific factors "
            "before final deployment."
        )
    }


# ==================================================
# FOOD EMISSION CALCULATOR
# ==================================================

def calculate_food_emissions(
    meal: str,
    servings: float = 1
) -> dict:
    """Calculate food-related emissions."""

    factors = {
        "chicken": 6.9,
        "beef": 27.0,
        "rice": 2.7,
        "vegetables": 0.5,
        "eggs": 4.5,
        "milk": 3.2
    }

    meal = meal.lower().strip()

    if servings <= 0:
        return {
            "error": "Servings must be greater than zero."
        }

    if meal not in factors:
        return {
            "error": (
                "Choose chicken, beef, rice, vegetables, "
                "eggs, or milk."
            )
        }

    factor = factors[meal]
    emissions = factor * servings

    return {
        "category": "food",
        "food": meal,
        "servings": servings,
        "emission_factor": factor,
        "emissions_kg_co2e": round(emissions, 3),
        "unit": "kg CO2e",
        "source": (
            "Illustrative demonstration factors; "
            "verify before final deployment."
        )
    }


# ==================================================
# TOTAL CARBON FOOTPRINT CALCULATOR
# ==================================================

def calculate_total_footprint(
    electricity_kg: float,
    travel_kg: float,
    food_kg: float
) -> dict:
    """Calculate combined carbon footprint."""

    values = [
        electricity_kg,
        travel_kg,
        food_kg
    ]

    if any(value < 0 for value in values):
        return {
            "error": "Emissions cannot be negative."
        }

    total = sum(values)

    return {
        "electricity_kg": electricity_kg,
        "travel_kg": travel_kg,
        "food_kg": food_kg,
        "total_kg_co2e": round(total, 3),
        "suggestion": (
            "Try reducing electricity use, choosing public "
            "transport, and reducing high-emission foods."
        )
    }


# ==================================================
# SAVE ACTIVITY - SESSION + PERMANENT DATABASE
# ==================================================

def save_activity(
    tracking_mode: str,
    category: str,
    quantity: float,
    unit: str,
    emissions_kg_co2e: float,
    source: str,
    tool_context: ToolContext
) -> dict:
    """
    Save an activity in both ADK session memory
    and the permanent SQLite database.
    """

    tracking_mode = tracking_mode.lower().strip()

    if tracking_mode not in ["individual", "household"]:
        return {
            "error": "Choose individual or household mode."
        }

    if quantity < 0 or emissions_kg_co2e < 0:
        return {
            "error": "Values cannot be negative."
        }

    activity = {
        "tracking_mode": tracking_mode,
        "category": category.lower().strip(),
        "quantity": quantity,
        "unit": unit,
        "emissions_kg_co2e": emissions_kg_co2e,
        "source": source
    }

    # Save permanently in SQLite
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("""
            INSERT INTO activities (
                tracking_mode,
                category,
                quantity,
                unit,
                emissions_kg_co2e,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tracking_mode,
            activity["category"],
            quantity,
            unit,
            emissions_kg_co2e,
            source
        ))

        connection.commit()

    finally:
        connection.close()

    # Also save in current ADK session memory
    activities = list(
        tool_context.state.get("activities", [])
    )

    activities.append(activity)

    tool_context.state["activities"] = activities

    matching = [
        item for item in activities
        if item.get("tracking_mode") == tracking_mode
    ]

    session_total = sum(
        item.get("emissions_kg_co2e", 0)
        for item in matching
    )

    return {
        "saved": True,
        "permanent_storage": True,
        "tracking_mode": tracking_mode,
        "activities_count": len(matching),
        "total_emissions_kg_co2e": round(session_total, 3),
        "message": "Activity saved successfully."
    }
