
import streamlit as st
from adk_connection import (
    create_session,
    ask_carbon_coach,
    get_saved_activities
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Carbon Coach",
    page_icon="🌱",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #F4F8F1;
}

h1, h2, h3 {
    color: #174D35;
}

[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #DCE8DC;
}

[data-testid="stSidebar"] {
    background-color: #E7F0E4;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION INITIALIZATION
# --------------------------------------------------

if "adk_session_id" not in st.session_state:
    st.session_state.adk_session_id = create_session()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🌱 Carbon Coach")

mode = st.sidebar.selectbox(
    "Tracking Mode",
    ["Individual", "Household"]
)

st.sidebar.markdown("---")
st.sidebar.write("🌍 Measure • Understand • Reduce")

st.sidebar.info(
    "Track your activities and discover ways "
    "to reduce your carbon footprint."
)

# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.title("🌱 Carbon Coach")

st.subheader(
    "Your AI-powered personal and household "
    "sustainability companion"
)

st.caption(f"Current tracking mode: {mode}")

# --------------------------------------------------
# RETRIEVE SAVED ACTIVITIES
# --------------------------------------------------

activities = get_saved_activities(
    st.session_state.adk_session_id
)

mode_key = mode.lower()

filtered_activities = [
    activity for activity in activities
    if activity.get("tracking_mode") == mode_key
]

# --------------------------------------------------
# CALCULATE DASHBOARD METRICS
# --------------------------------------------------

total_emissions = sum(
    activity.get("emissions_kg_co2e", 0)
    for activity in filtered_activities
)

activity_count = len(filtered_activities)

# Demo scoring rule
green_points = activity_count * 10

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

st.header("📊 Your Carbon Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Footprint",
    f"{total_emissions:.2f} kg CO₂e"
)

col2.metric(
    "Activities Logged",
    activity_count
)

col3.metric(
    "Green Points",
    green_points
)

st.divider()

# --------------------------------------------------
# CARBON CATEGORY BREAKDOWN
# --------------------------------------------------

st.subheader("📈 Your Carbon Breakdown")

category_totals = {}

for activity in filtered_activities:
    category = activity.get(
        "category", "Other"
    ).title()

    emissions = activity.get(
        "emissions_kg_co2e", 0
    )

    category_totals[category] = (
        category_totals.get(category, 0) + emissions
    )

if category_totals:
    st.bar_chart(category_totals)
else:
    st.info(
        "No activities recorded yet. "
        "Start tracking your carbon footprint!"
    )

# --------------------------------------------------
# RECENT ACTIVITY HISTORY
# --------------------------------------------------

st.subheader("📝 Recent Activities")

if filtered_activities:
    activity_table = [
        {
            "Category": item.get(
                "category", ""
            ).title(),

            "Quantity": (
                f"{item.get('quantity', 0)} "
                f"{item.get('unit', '')}"
            ),

            "Emissions (kg CO₂e)": item.get(
                "emissions_kg_co2e", 0
            )
        }
        for item in reversed(filtered_activities)
    ]

    st.dataframe(
        activity_table,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info(
        "Your activity history will appear here."
    )

st.divider()

# --------------------------------------------------
# AI ECO-COACH
# --------------------------------------------------

st.header("🤖 AI Eco-Coach")

st.write(
    "Ask questions, calculate emissions, "
    "save activities and receive sustainability advice."
)

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(
    "Ask Carbon Coach something..."
):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Carbon Coach is thinking..."):

            response = ask_carbon_coach(
                f"My tracking mode is {mode}. {prompt}",
                st.session_state.adk_session_id
            )

            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Refresh dashboard after AI saves an activity
    st.rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Carbon Coach | Measure • Understand • Reduce 🌍"
)
