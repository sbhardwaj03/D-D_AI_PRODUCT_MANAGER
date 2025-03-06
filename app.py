import streamlit as st

# Set page title and layout
st.set_page_config(page_title="AI Product Manager", page_icon="🤖", layout="wide")

st.title("🤖 AI Product Manager")
st.write("Enter the details below to generate a **structured product roadmap**.")

# Input Form
with st.form("product_details"):
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("Product Name:")
        start_date = st.date_input("📅 Start Date:")
        end_date = st.date_input("📅 End Date:")
    with col2:
        product_description = st.text_area("📝 Product Description:")        

    if end_date < start_date:
        st.error("🚨 End date cannot be earlier than start date.")

    st.subheader("👥 Build Your Team")
    roles = ["Backend Developer", "Frontend Developer", "Tester", "UI/UX Designer", "Data Analyst", "DevOps Engineer"]
    selected_roles = [role for role in roles if st.checkbox(role)]

    submit_button = st.form_submit_button("🚀 Generate Roadmap")

# Store data in session and navigate
if submit_button:
    if product_name and product_description and start_date and end_date:
        st.session_state.product_name = product_name
        st.session_state.product_description = product_description
        st.session_state.start_date = str(start_date)
        st.session_state.end_date = str(end_date)
        st.session_state.team = ", ".join(selected_roles) if selected_roles else "No team selected"
        
        st.switch_page("output.py")  # Redirect to output page
    else:
        st.warning("⚠️ Please fill in all fields before submitting.")
