
# ==================================================
# ENVIRONMENT CONFIGURATION
# ==================================================

from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / "Carbon_coach" / ".env"
load_dotenv(env_path, override=True)


# ==================================================
# IMPORTS
# ==================================================

import asyncio
import uuid
import sqlite3

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from Carbon_coach.agent import root_agent


# ==================================================
# ADK CONFIGURATION
# ==================================================

APP_NAME = "carbon_coach_app"
USER_ID = "carbon_coach_user"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DB_PATH = (
    Path(__file__).parent
    / "Carbon_coach"
    / "carbon_activities.db"
)


# ==================================================
# CREATE ADK SESSION
# ==================================================

def create_session():
    """Create a new conversation session."""

    session_id = str(uuid.uuid4())

    asyncio.run(
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )
    )

    return session_id


# ==================================================
# COMMUNICATE WITH CARBON COACH AI
# ==================================================

def ask_carbon_coach(message, session_id):
    """Send a message to the Gemini-powered agent."""

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=message)
        ]
    )

    async def run_agent():

        response_text = ""

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=content
        ):

            if event.is_final_response() and event.content:

                for part in event.content.parts:

                    if part.text:
                        response_text += part.text

        return response_text

    return asyncio.run(run_agent())


# ==================================================
# RETRIEVE PERMANENTLY SAVED ACTIVITIES
# ==================================================

def get_saved_activities(session_id=None):
    """
    Retrieve activities from permanent SQLite storage.
    The session_id argument is retained for compatibility.
    """

    if not DB_PATH.exists():
        return []

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        rows = connection.execute("""
            SELECT
                id,
                tracking_mode,
                category,
                quantity,
                unit,
                emissions_kg_co2e,
                source,
                created_at
            FROM activities
            ORDER BY id DESC
        """).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()
