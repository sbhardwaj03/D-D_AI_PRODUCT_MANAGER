import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from groq import Groq

# Secure API Key Storage
API_KEY = 'your_api_key_here'
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="Generated Roadmap", page_icon="📌", layout="wide")
st.title("📌 Generated Roadmap")

# Validate if session data exists
if "product_name" not in st.session_state:
    st.warning("⚠️ No project data found. Please go back and enter details.")
    st.stop()

# Extract stored data
product_name = st.session_state.product_name
product_description = st.session_state.product_description
start_date = st.session_state.start_date
end_date = st.session_state.end_date
team = st.session_state.team

# Function to generate roadmap from LLM
def question_answering_system():
    query = f"""
    Create a structured product roadmap for '{product_name}'.
    **Format the roadmap in "Phase X" style** (e.g., Phase 1, Phase 2).
    Each phase should include:
    - **Phase Name**: (e.g., Phase 1: Research and Planning)
    - **Timeline**: (Format: "Week X-Y, YYYY-MM-DD to YYYY-MM-DD")
    - **Tasks**: (List of key tasks with assigned roles)
    - **Deliverables**: (Expected outputs from this phase)

    Project starts on {start_date} and ends on {end_date}.
    Team: {team}.
    """

    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[{'role': 'user', 'content': query}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Fetch roadmap
roadmap_text = question_answering_system()

# Display roadmap text
st.subheader("📄 Roadmap Details")
st.write(roadmap_text)

# Extract phases and generate Gantt Chart
milestones = []
start_dates = []
end_dates = []
roadmap_lines = roadmap_text.split("\n")

for i, line in enumerate(roadmap_lines):
    if "Phase" in line:
        phase_name = line.strip()
        
        if i + 1 < len(roadmap_lines) and "Timeline:" in roadmap_lines[i + 1]:
            timeline_line = roadmap_lines[i + 1]
            date_range = timeline_line.split(", ")[-1]

            try:
                start, end = date_range.split(" to ")
                start_dates.append(datetime.strptime(start.strip(), "%Y-%m-%d"))
                end_dates.append(datetime.strptime(end.strip(), "%Y-%m-%d"))
                milestones.append(phase_name)
            except ValueError:
                continue

df = pd.DataFrame({"Milestone": milestones, "Start Date": start_dates, "End Date": end_dates})
df = df.sort_values(by="Start Date", ascending=True)

# Generate and display Gantt Chart
if not df.empty:
    fig = px.timeline(
        df,
        x_start="Start Date",
        x_end="End Date",
        y="Milestone",
        title="📅 Project Gantt Chart",
        color="Milestone"
    )
    fig.update_layout(xaxis=dict(showgrid=True), yaxis=dict(categoryorder="total ascending"))

    st.subheader("📊 Gantt Chart")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Could not extract phases correctly. Please check the LLM output.")
