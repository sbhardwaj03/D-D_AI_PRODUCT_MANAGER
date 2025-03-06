import streamlit as st

# Set page title
st.set_page_config(page_title="AI Product Manager", page_icon="🤖", layout="wide")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

st.title("🤖 AI Product Manager")
st.write("Enter the details below to generate a **structured product roadmap**.")

with st.form("product_details"):
    product_name = st.text_input("Product Name:")
    product_description = st.text_area("📝 Product Description:")
    start_date = st.date_input("📅 Start Date:")
    end_date = st.date_input("📅 End Date:")

    if end_date < start_date:
        st.error("🚨 End date cannot be earlier than start date.")

    roles = ["Backend Developer", "Frontend Developer", "Tester", "UI/UX Designer", "Data Analyst", "DevOps Engineer"]
    selected_roles = [role for role in roles if st.checkbox(role)]

    submit_button = st.form_submit_button("🚀 Generate Roadmap")

if submit_button:
    if product_name and product_description and start_date and end_date:
        # Store data in session state
        st.session_state.product_name = product_name
        st.session_state.product_description = product_description
        st.session_state.start_date = str(start_date)
        st.session_state.end_date = str(end_date)
        st.session_state.team = ", ".join(selected_roles) if selected_roles else "No team selected"
        st.session_state.page = "roadmap"  # Set page to roadmap

# Redirect to roadmap page using session state
if st.session_state.page == "roadmap":
    st.rerun()  # Refresh the app and go to roadmap
