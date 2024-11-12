import os
import pandas as pd
import streamlit as st
from openai import OpenAI

# Set Streamlit page config to wide layout
st.set_page_config(layout="wide")

# Disclaimer: Throughout making this code we did use ChatGPT to aid us in understanding and using different Streamlit functions that we otherwise did not understand

# Initialize the OpenAI client using the API key from the environment variable
api_key = "MY-API-KeY"
client = OpenAI(api_key=api_key)

# Define the get_completion function using the client.chat.completions.create format
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an environmental specialist. Provide personalized water-saving advice based on the user's input and data."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# Function to analyze uploaded faucet data and generate a summary
def summarize_faucet_data(df):
    # Ensure timestamp is datetime type
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate total and daily usage
    total_usage = df.groupby("faucet_id")["usage_liters"].sum()
    daily_usage = df.groupby([df['timestamp'].dt.date, "faucet_id"])["usage_liters"].sum().unstack()

    # Average daily usage
    avg_daily_usage = daily_usage.mean()

    # Peak usage times
    peak_usage = df.groupby(df['timestamp'].dt.hour)["usage_liters"].sum().idxmax()

    # Create a summary for the prompt
    summary = f"Total usage per faucet:\n{total_usage}\n\n"
    summary += f"Average daily usage per faucet:\n{avg_daily_usage}\n\n"
    summary += f"Peak usage hour across all faucets: {peak_usage}:00\n\n"
    return summary

# Function to generate a summary based on farmer's responses
def summarize_farm_data(crop_type, irrigation_method, soil_type, avg_rainfall):
    farm_summary = f"""
    The farmer has provided the following details:
    - Crop Type: {crop_type}
    - Irrigation Method: {irrigation_method}
    - Soil Type: {soil_type}
    - Average Annual Rainfall: {avg_rainfall} inches
    
    Provide advice on optimal water usage and irrigation practices considering the type of crop, irrigation method, soil type, and rainfall.
    """
    return farm_summary

def water_usage_calculator():
    st.markdown("<h2 class='header'>Water Usage Calculator</h2>", unsafe_allow_html=True)
    
    # Input fields
    shower_time = st.number_input("How many minutes do you shower daily?", min_value=0)
    dishwashing_loads = st.number_input("How many loads of dishes do you wash per week?", min_value=0)
    laundry_loads = st.number_input("How many loads do you do laundry per week?", min_value=0)
    watering_time = st.number_input("How many minutes do you water the garden daily?", min_value=0)

    # Constants for average usage
    shower_usage_per_minute = 2.1  # gallons
    dishwashing_usage_per_load = 6   # gallons
    laundry_usage_per_load = 15      # gallons
    watering_usage_per_minute = 3     # gallons

    # Calculating total usage
    daily_usage = (shower_time * shower_usage_per_minute +
                   (dishwashing_loads * dishwashing_usage_per_load / 7) +
                   (laundry_loads * laundry_usage_per_load / 7) +
                   (watering_time * watering_usage_per_minute))
    
    monthly_usage = daily_usage * 30  # Approximate monthly usage

    # Display results
    st.subheader("Estimated Water Usage")
    st.write(f"Daily Water Usage: {daily_usage:.2f} gallons")
    st.write(f"Monthly Water Usage: {monthly_usage:.2f} gallons")

# Custom CSS for font sizes and styles in the sidebar
st.markdown(
    """
    <style>
    /* Apply to the sidebar's main container */
    section[data-testid="stSidebar"] .css-1aumxhk {
        font-size: 24px !important;
    }
    
    /* Specific sidebar navigation title */
    section[data-testid="stSidebar"] h1 {
        font-size: 26px !important;
        color: #4CAF50;
    }

    /* Sidebar radio button labels */
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 24px !important;
        color: #333;
    }

    /* Sidebar radio button options */
    section[data-testid="stSidebar"] .stRadio > div > label > div {
        font-size: 20px !important;
        color: #333;
    }

    /* Apply font size to all sidebar elements as a fallback */
    section[data-testid="stSidebar"] * {
        font-size: 20px !important;
    }

    /* Increase main container width */
    .main .block-container {
        max-width: 90%;
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App
def main():
    # Add a title with custom class
    st.markdown("<h1 class='title'>Water Usage Application</h1>", unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to", 
        ["Questionnaire & AI Advice", "Upload & Analyze Faucet Data", "Farmer's Water Usage", "Water Usage Calculator"]
    )

    # Existing page selection logic
    if page == "Questionnaire & AI Advice":
        st.markdown("<h2 class='header'>Water Usage Questionnaire - San Jose, CA</h2>", unsafe_allow_html=True)
        
        # Questionnaire
        household_size = st.selectbox("How many people live in your household?", ["1", "2", "3", "4", "5+"])
        water_intensive_activities = st.selectbox("How often do you do water-intensive activities (e.g., laundry, car washing, gardening)?", ["Daily", "Several times a week", "Weekly", "Rarely"])
        water_saving_practices = st.multiselect("Do you already follow any water-saving practices?", ["Low-flow showerheads", "Faucet aerators", "Reusing water", "Reducing shower time", "None"])
        
        # Additional questions
        household_type = st.selectbox("What type of home do you live in?", ["Apartment", "House", "Townhouse", "Other"])
        awareness_level = st.radio("How would you rate your awareness of water usage?", ["Low", "Medium", "High"])
        motivation = st.selectbox("Why are you interested in saving water?", ["Environmental concern", "Reducing bills", "Water scarcity", "Other"])

        # Generate prompt based on questionnaire responses
        prompt = f"""
        The user has provided the following details:
        - Household Size: {household_size}
        - Frequency of Water-Intensive Activities: {water_intensive_activities}
        - Existing Water-Saving Practices: {', '.join(water_saving_practices)}
        - Household Type: {household_type}
        - Awareness Level: {awareness_level}
        - Motivation for Saving Water: {motivation}
        
        Based on this information and any available data from the smart faucet, provide personalized advice on how the user can reduce water usage effectively.
        """
        
        # When user submits, generate AI advice
        if st.button("Get Water-Saving Advice"):
            advice = get_completion(prompt)
            st.subheader("Personalized Water-Saving Advice")
            st.write(advice)
    
    elif page == "Upload & Analyze Faucet Data":
        st.markdown("<h2 class='header'>Smart Faucet Water Usage Analytics - Upload Data</h2>", unsafe_allow_html=True)

        # File upload
        uploaded_file = st.file_uploader("Upload a CSV file with your water usage data", type="csv")
        
        if uploaded_file is not None:
            # Load the uploaded data
            df = pd.read_csv(uploaded_file)
            
            # Summarize the faucet data and generate prompt
            data_summary = summarize_faucet_data(df)
            st.write("Data Summary:")
            st.text(data_summary)  # Display the summary for transparency
            
            # Combine data summary with the advice prompt
            combined_prompt = f"""
            Here is the faucet usage data summary:
            {data_summary}
            
            Based on this data and the user's questionnaire responses, provide detailed and practical water-saving advice tailored to their usage patterns and household details.
            """

            # Get advice based on the faucet data and display it
            advice = get_completion(combined_prompt)
            st.subheader("Water Conservation Advice Based on Faucet Data")
            st.write(advice)

    elif page == "Farmer's Water Usage":
        st.markdown("<h2 class='header'>Farmer's Water Usage and Irrigation Advice</h2>", unsafe_allow_html=True)

        # Farmer's Questionnaire
        crop_type = st.selectbox("Type of crop:", ["Wheat", "Corn", "Rice", "Soybeans", "Other"])
        irrigation_method = st.selectbox("Irrigation method:", ["Drip", "Sprinkler", "Flood", "Furrow", "Other"])
        soil_type = st.selectbox("Soil type:", ["Clay", "Sandy", "Loamy", "Silty", "Peaty", "Other"])
        avg_rainfall = st.number_input("Average annual rainfall (inches):", min_value=0.0, max_value=200.0, step=0.1)
        
        # Generate summary and prompt based on questionnaire responses
        farm_summary = summarize_farm_data(crop_type, irrigation_method, soil_type, avg_rainfall)

        # When user submits, generate AI advice
        if st.button("Get Water Usage Advice for Farming"):
            advice = get_completion(farm_summary)
            st.subheader("Personalized Water-Saving Advice for Farmers")
            st.write(advice)
    
    elif page == "Water Usage Calculator":
        water_usage_calculator()

if __name__ == "__main__":
    main()
