import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from groq import Groq

# Secure API Key Storage
API_KEY = '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'
if not API_KEY:
    st.error("API key not found. Please set the 'GROQ_API_KEY' environment variable.")
    st.stop()

# Initialize Groq Client
client = Groq(api_key=API_KEY)

# Function to get response from LLM model with enforced "Phase" format
def question_answering_system(query):
    try:
        formatted_query = f"""
        Create a structured product roadmap for '{st.session_state.product_name}'.
        **Format the roadmap in "Phase X" style** (e.g., Phase 1, Phase 2).
        Each phase should include:
        - **Phase Name**: (e.g., Phase 1: Research and Planning)
        - **Timeline**: (Format: "Week X-Y, YYYY-MM-DD to YYYY-MM-DD")
        - **Tasks**: (List of key tasks with assigned roles)
        - **Deliverables**: (Expected outputs from this phase)
        - **Ensure correct date formatting in YYYY-MM-DD to YYYY-MM-DD**
        - **Ensure phase names are meaningful (e.g., Research and Planning, Development, Testing, etc.)**

        Project starts on {st.session_state.start_date} and ends on {st.session_state.end_date}.
        Team: {st.session_state.team}.
        """
        
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[{'role': 'user', 'content': formatted_query}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit Page Configuration
st.set_page_config(page_title="AI Product Manager", page_icon="🤖", layout="wide")

# Initialize session state variables
if 'product_name' not in st.session_state:
    st.session_state.product_name = ""
if 'start_date' not in st.session_state:
    st.session_state.start_date = None
if 'end_date' not in st.session_state:
    st.session_state.end_date = None
if 'team' not in st.session_state:
    st.session_state.team = ""
if 'roadmap_generated' not in st.session_state:
    st.session_state.roadmap_generated = False

# Input Page
def input_page():
    st.title("🤖 AI Product Manager")
    st.write("Enter the details below to generate a **structured product roadmap**.")

    # Input Fields
    with st.form("product_details"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.product_name = st.text_input("Product Name:", value=st.session_state.product_name)
            st.session_state.start_date = st.date_input("📅 Start Date:", value=st.session_state.start_date)
            st.session_state.end_date = st.date_input("📅 End Date:", value=st.session_state.end_date)
        with col2:
            product_description = st.text_area("📝 Product Description:")

        # Validate dates (only if both dates are selected)
        if st.session_state.start_date and st.session_state.end_date:
            if st.session_state.end_date < st.session_state.start_date:
                st.error("🚨 End date cannot be earlier than start date.")
        
        # Team Building Section
        st.subheader("👥 Build Your Team")
        roles = ["Backend Developer", "Frontend Developer", "Tester", "UI/UX Designer", "Data Analyst", "DevOps Engineer"]
        selected_roles = [role for role in roles if st.checkbox(role)]

        # ✅ Submit Button (ONLY ONE)
        submit_button = st.form_submit_button("🚀 Generate Roadmap")

    # ✅ If Submit Button is Clicked, Process Input
    if submit_button:
        if st.session_state.product_name and product_description and st.session_state.start_date and st.session_state.end_date:
            st.session_state.team = ", ".join(selected_roles) if selected_roles else "No team selected"
            st.session_state.roadmap_generated = True
            st.experimental_rerun()

# Roadmap Page
def roadmap_page():
    st.title("📌 Generated Roadmap")
    query = f"Create a product roadmap for '{st.session_state.product_name}'. Project starts on {st.session_state.start_date} and ends on {st.session_state.end_date}. Team: {st.session_state.team}."

    # Get roadmap response from LLM (formatted correctly)
    answer = question_answering_system(query)

    # Display LLM-generated roadmap
    st.write(answer)

    # **Check if the output contains "Phase X"**
    if "Phase" in answer:
        # **Extract milestones & generate Gantt chart**
        milestones = []
        start_dates = []
        end_dates = []
        roadmap_lines = answer.split("\n")

        for i, line in enumerate(roadmap_lines):
            if "Phase" in line:
                # Extract phase name
                phase_name = line.strip()
                
                # Find the timeline in the next line
                if i + 1 < len(roadmap_lines) and "Timeline:" in roadmap_lines[i + 1]:
                    timeline_line = roadmap_lines[i + 1]
                    date_range = timeline_line.split(", ")[-1]  # Extract date part

                    try:
                        start, end = date_range.split(" to ")
                        start_dates.append(datetime.strptime(start.strip(), "%Y-%m-%d"))
                        end_dates.append(datetime.strptime(end.strip(), "%Y-%m-%d"))
                        milestones.append(phase_name)
                    except ValueError:
                        continue  # Skip if date format is incorrect

        # Convert extracted data to DataFrame
        df = pd.DataFrame({
            "Milestone": milestones,
            "Start Date": start_dates,
            "End Date": end_dates
        })

        # **Sort phases by Start Date instead of milestone number**
        df = df.sort_values(by="Start Date", ascending=True)

        # **📊 Generate Gantt Chart**
        if not df.empty:
            fig = px.timeline(
                df,
                x_start="Start Date",
                x_end="End Date",
                y="Milestone",
                title="📅 Project Gantt Chart",
                color="Milestone",
                labels={"Milestone": "Project Phases"}
            )

            # Enable grid for better visualization
            fig.update_layout(
                xaxis=dict(showgrid=True),
                yaxis=dict(categoryorder="total ascending"),  # Ensure correct phase order
                legend_title="Project Phases"
            )

            # **Display Gantt Chart**
            st.subheader("📊 Gantt Chart for Project Timeline")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Could not extract phases correctly. Please check the LLM output.")
    else:
        st.warning("⚠️ No structured phases found in the roadmap. Displaying text only.")

# Main App Logic
if not st.session_state.roadmap_generated:
    input_page()  # Show the input page
else:
    roadmap_page()  # Show the roadmap page
