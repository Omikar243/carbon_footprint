import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page title and configuration
st.set_page_config(page_title="Transport Carbon Footprint Calculator", layout="wide")

# Title and introduction
st.title("Transport Carbon Footprint Calculator")
st.markdown("""
This application helps you calculate your monthly carbon footprint based on your daily commute and transportation choices.
Compare different transportation modes and receive personalized sustainability recommendations.
""")

# Initialize session state variables if they don't exist
if 'calculated' not in st.session_state:
    st.session_state.calculated = False
if 'total_emissions' not in st.session_state:
    st.session_state.total_emissions = 0
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'emissions_data' not in st.session_state:
    st.session_state.emissions_data = {}

# Define emission factors (approximate values)
emission_factors = {
    # Two wheelers
    "two_wheeler": {
        "Scooter": {
            "petrol": {"min": 0.03, "max": 0.06},
            "diesel": {"min": 0.04, "max": 0.07},
            "electric": {"min": 0.01, "max": 0.02}
        },
        "Motorcycle": {
            "petrol": {"min": 0.05, "max": 0.09},
            "diesel": {"min": 0.06, "max": 0.10},
            "electric": {"min": 0.01, "max": 0.02}
        }
    },
    
    # Three wheelers
    "three_wheeler": {
        "petrol": {"min": 0.07, "max": 0.12},
        "diesel": {"min": 0.08, "max": 0.13},
        "electric": {"min": 0.02, "max": 0.03},
        "cng": {"min": 0.05, "max": 0.09}
    },
    
    # Four wheelers
    "four_wheeler": {
        "small": {
            "petrol": {"base": 0.12, "uplift": 1.1},
            "diesel": {"base": 0.14, "uplift": 1.1},
            "cng": {"base": 0.10, "uplift": 1.05},
            "electric": {"base": 0.05, "uplift": 1.0}
        },
        "hatchback": {
            "petrol": {"base": 0.15, "uplift": 1.1},
            "diesel": {"base": 0.17, "uplift": 1.1},
            "cng": {"base": 0.12, "uplift": 1.05},
            "electric": {"base": 0.06, "uplift": 1.0}
        },
        "premium_hatchback": {
            "petrol": {"base": 0.18, "uplift": 1.15},
            "diesel": {"base": 0.20, "uplift": 1.15},
            "cng": {"base": 0.14, "uplift": 1.10},
            "electric": {"base": 0.07, "uplift": 1.0}
        },
        "compact_suv": {
            "petrol": {"base": 0.21, "uplift": 1.2},
            "diesel": {"base": 0.23, "uplift": 1.2},
            "cng": {"base": 0.16, "uplift": 1.15},
            "electric": {"base": 0.08, "uplift": 1.0}
        },
        "sedan": {
            "petrol": {"base": 0.20, "uplift": 1.2},
            "diesel": {"base": 0.22, "uplift": 1.2},
            "cng": {"base": 0.16, "uplift": 1.15},
            "electric": {"base": 0.08, "uplift": 1.0}
        },
        "suv": {
            "petrol": {"base": 0.25, "uplift": 1.25},
            "diesel": {"base": 0.28, "uplift": 1.25},
            "cng": {"base": 0.20, "uplift": 1.2},
            "electric": {"base": 0.10, "uplift": 1.0}
        },
        "hybrid": {
            "petrol": {"base": 0.14, "uplift": 1.05},
            "diesel": {"base": 0.16, "uplift": 1.05},
            "electric": {"base": 0.07, "uplift": 1.0}
        }
    },
    
    # Public transport
    "public_transport": {
        "taxi": {
            "small": {
                "petrol": {"base": 0.12, "uplift": 1.1},
                "diesel": {"base": 0.14, "uplift": 1.1},
                "cng": {"base": 0.10, "uplift": 1.05},
                "electric": {"base": 0.05, "uplift": 1.0}
            },
            "hatchback": {
                "petrol": {"base": 0.15, "uplift": 1.1},
                "diesel": {"base": 0.17, "uplift": 1.1},
                "cng": {"base": 0.12, "uplift": 1.05},
                "electric": {"base": 0.06, "uplift": 1.0}
            },
            "sedan": {
                "petrol": {"base": 0.20, "uplift": 1.2},
                "diesel": {"base": 0.22, "uplift": 1.2},
                "cng": {"base": 0.16, "uplift": 1.15},
                "electric": {"base": 0.08, "uplift": 1.0}
            },
            "suv": {
                "petrol": {"base": 0.25, "uplift": 1.25},
                "diesel": {"base": 0.28, "uplift": 1.25},
                "cng": {"base": 0.20, "uplift": 1.2},
                "electric": {"base": 0.10, "uplift": 1.0}
            }
        },
        "bus": {
            "electric": 0.025,
            "petrol": 0.05,
            "diesel": 0.045,
            "cng": 0.035
        },
        "metro": 0.015
    }
}

# Create input form in the main area
st.header("Your Commute Details")

# Universal commute details
col1, col2, col3 = st.columns(3)
with col1:
    distance = st.number_input("Daily one-way distance (km)", min_value=0.1, value=10.0, step=0.5)
with col2:
    days_per_week = st.number_input("Commuting days per week", min_value=1, max_value=7, value=5, step=1)
with col3:
    weeks_per_month = st.number_input("Commuting weeks per month", min_value=1, max_value=5, value=4, step=1)

# Calculate total monthly distance
total_monthly_km = distance * 2 * days_per_week * weeks_per_month
st.metric("Total monthly commute distance", f"{total_monthly_km:.1f} km")

# Transport category selection
st.header("Select Your Transport Category")
transport_category = st.selectbox(
    "Transport Category",
    ["Private Transport", "Public Transport", "Both Private and Public"]
)

# Define variable to store emission factors
emission_factor = 0
people_count = 1
vehicle_type = ""
vehicle_name = ""

# Dynamic form based on transport category
if transport_category == "Private Transport" or transport_category == "Both Private and Public":
    st.subheader("Private Transport Details")
    col1, col2 = st.columns([1, 2])
    with col1:
        private_vehicle_type = st.selectbox(
            "Vehicle Type",
            ["Two Wheeler", "Three Wheeler", "Four Wheeler"],
            key="private_vehicle"
        )

    # Dynamic form based on private vehicle type
    if private_vehicle_type == "Two Wheeler":
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox("Category", ["Scooter", "Motorcycle"])
        with col2:
            engine_cc = st.number_input("Engine (cc)", 50, 1500, 150)
        with col3:
            fuel_type = st.selectbox("Fuel Type", ["petrol", "diesel", "electric"])
        
        # Calculate emission factor based on engine size
        if engine_cc <= 150:
            emission_factor = emission_factors["two_wheeler"][category][fuel_type]["min"]
        else:
            # Linear interpolation based on engine size
            min_ef = emission_factors["two_wheeler"][category][fuel_type]["min"]
            max_ef = emission_factors["two_wheeler"][category][fuel_type]["max"]
            ratio = min(1.0, (engine_cc - 150) / 1350)  # Normalize to 0-1
            emission_factor = min_ef + ratio * (max_ef - min_ef)
        
        col1, col2 = st.columns(2)
        with col1:
            rideshare = st.checkbox("Rideshare")
        with col2:
            if rideshare:
                people_count = st.slider("Number of people sharing", 1, 2, 1)
            else:
                people_count = 1
        
        vehicle_type = "Two Wheeler"
        vehicle_name = f"{category} ({fuel_type}, {engine_cc}cc)"
        if rideshare:
            vehicle_name += f" with {people_count} people"

    elif private_vehicle_type == "Three Wheeler":
        col1, col2 = st.columns(2)
        with col1:
            engine_cc = st.slider("Engine (cc)", 50, 1000, 200)
        with col2:
            fuel_type = st.selectbox("Fuel Type", ["petrol", "diesel", "electric", "cng"])
        
        # Calculate emission factor based on engine size
        min_ef = emission_factors["three_wheeler"][fuel_type]["min"]
        max_ef = emission_factors["three_wheeler"][fuel_type]["max"]
        ratio = min(1.0, (engine_cc - 50) / 950)  # Normalize to 0-1
        emission_factor = min_ef + ratio * (max_ef - min_ef)
        
        col1, col2 = st.columns(2)
        with col1:
            rideshare = st.checkbox("Rideshare")
        with col2:
            if rideshare:
                people_count = st.slider("Number of people sharing", 1, 3, 1)
            else:
                people_count = 1
        
        vehicle_type = "Three Wheeler"
        vehicle_name = f"Three Wheeler ({fuel_type}, {engine_cc}cc)"
        if rideshare:
            vehicle_name += f" with {people_count} people"

    elif private_vehicle_type == "Four Wheeler":
        col1, col2 = st.columns(2)
        with col1:
            car_type = st.selectbox(
                "Car Type", 
                ["small", "hatchback", "premium_hatchback", "compact_suv", "sedan", "suv", "hybrid"]
            )
        with col2:
            engine_cc = st.slider("Engine (cc)", 600, 4000, 1200)
        
        fuel_options = ["petrol", "diesel", "cng", "electric"]
        if car_type == "hybrid":
            fuel_options = ["petrol", "diesel", "electric"]
        
        col1, col2 = st.columns(2)
        with col1:
            fuel_type = st.selectbox("Fuel Type", fuel_options)
        
        # Calculate emission factor with uplift
        base_ef = emission_factors["four_wheeler"][car_type][fuel_type]["base"]
        uplift = emission_factors["four_wheeler"][car_type][fuel_type]["uplift"]
        
        # Adjust for engine size (larger engines emit more)
        if fuel_type != "electric":
            engine_factor = 1.0 + min(1.0, (engine_cc - 600) / 3400) * 0.5  # Up to 50% more for largest engines
        else:
            engine_factor = 1.0  # Electric doesn't scale with engine size in the same way
            
        emission_factor = base_ef * uplift * engine_factor
        
        col1, col2 = st.columns(2)
        with col1:
            rideshare = st.checkbox("Rideshare")
        with col2:
            if rideshare:
                people_count = st.slider("Number of people sharing", 1, 5, 1)
            else:
                people_count = 1
        
        vehicle_type = "Four Wheeler"
        vehicle_name = f"{car_type.replace('_', ' ').title()} ({fuel_type}, {engine_cc}cc)"
        if rideshare:
            vehicle_name += f" with {people_count} people"

if transport_category == "Public Transport" or transport_category == "Both Private and Public":
    st.subheader("Public Transport Details")
    col1, col2 = st.columns(2)
    with col1:
        transport_mode = st.selectbox("Mode", ["Taxi", "Bus", "Metro"], key="public_mode")
    
    if transport_mode == "Taxi":
        col1, col2 = st.columns(2)
        with col1:
            car_type = st.selectbox(
                "Car Type", 
                ["small", "hatchback", "sedan", "suv"],
                key="taxi_type"
            )
        with col2:
            fuel_type = st.selectbox("Fuel Type", ["petrol", "diesel", "cng", "electric"], key="taxi_fuel")
        
        base_ef = emission_factors["public_transport"]["taxi"][car_type][fuel_type]["base"]
        uplift = emission_factors["public_transport"]["taxi"][car_type][fuel_type]["uplift"]
        public_emission_factor = base_ef * uplift
        
        public_people_count = st.slider("Number of people sharing", 1, 4, 1, key="taxi_people")
        
        # Only update main variables if only using public transport
        if transport_category == "Public Transport":
            emission_factor = public_emission_factor
            people_count = public_people_count
            vehicle_type = "Public Transport"
            vehicle_name = f"Taxi - {car_type.replace('_', ' ').title()} ({fuel_type})"
            if public_people_count > 1:
                vehicle_name += f" with {public_people_count} people"
    
    elif transport_mode == "Bus":
        public_fuel_type = st.selectbox("Fuel Type", ["diesel", "cng", "electric", "petrol"], key="bus_fuel")
        public_emission_factor = emission_factors["public_transport"]["bus"][public_fuel_type]
        # For buses, we assume a certain average occupancy already factored into emission factor
        public_people_count = 1
        
        # Only update main variables if only using public transport
        if transport_category == "Public Transport":
            emission_factor = public_emission_factor
            people_count = public_people_count
            vehicle_type = "Public Transport"
            vehicle_name = f"Bus ({public_fuel_type})"
    
    else:  # Metro
        public_emission_factor = emission_factors["public_transport"]["metro"]
        public_people_count = 1  # Already factored into emission factor
        
        # Only update main variables if only using public transport
        if transport_category == "Public Transport":
            emission_factor = public_emission_factor
            people_count = public_people_count
            vehicle_type = "Public Transport"
            vehicle_name = "Metro"

# Handle "Both" case by calculating combined emissions
if transport_category == "Both Private and Public":
    # Here we need to ask for usage ratio
    st.subheader("Usage Distribution")
    private_trips = st.number_input("Number of trips per day using private transport", min_value=0, max_value=10, value=2, step=1)
    total_trips = st.number_input("Total number of trips per day", min_value=1, max_value=10, value=4, step=1)
    private_ratio = private_trips / total_trips if total_trips > 0 else 0
    public_ratio = 1 - private_ratio
    
    # Calculate combined emission factor
    if private_ratio > 0 and public_ratio > 0:
        # Create a combined name for private transport
        if private_vehicle_type == "Two Wheeler":
            private_part = f"{category} ({fuel_type}, {engine_cc}cc)"
        elif private_vehicle_type == "Three Wheeler":
            private_part = f"Three Wheeler ({fuel_type}, {engine_cc}cc)"
        elif private_vehicle_type == "Four Wheeler":
            private_part = f"{car_type.replace('_', ' ').title()} ({fuel_type}, {engine_cc}cc)"
        
        # Create a combined name for public transport
        if transport_mode == "Taxi":
            public_part = f"Taxi - {car_type.replace('_', ' ').title()} ({fuel_type})"
        elif transport_mode == "Bus":
            public_part = f"Bus ({public_fuel_type})"
        else:  # Metro
            public_part = "Metro"
        
        # Calculate combined emission factor with proper division by people count
        combined_emission_factor = (emission_factor / people_count) * private_ratio + (public_emission_factor / public_people_count) * public_ratio
        emission_factor = combined_emission_factor
        people_count = 1  # Already factored in above
        
        vehicle_type = "Combined Transport"
        vehicle_name = f"{private_part} ({private_ratio*100:.0f}%) & {public_part} ({public_ratio*100:.0f}%)"

# Calculate button positioned prominently
if st.button("Calculate Carbon Footprint", type="primary", use_container_width=True):
    # Calculate total monthly emissions
    total_emissions = total_monthly_km * emission_factor
    
    # Store in session state
    st.session_state.calculated = True
    st.session_state.total_emissions = total_emissions
    
    # Generate alternative scenarios for comparison
    alternatives = {}
    
    # Add current vehicle
    alternatives[vehicle_name] = total_emissions
    
    # Generate alternatives for comparison
    # Add public transport options
    alternatives["Bus (Diesel)"] = (total_monthly_km * emission_factors["public_transport"]["bus"]["diesel"])
    alternatives["Bus (CNG)"] = (total_monthly_km * emission_factors["public_transport"]["bus"]["cng"])
    alternatives["Bus (Electric)"] = (total_monthly_km * emission_factors["public_transport"]["bus"]["electric"])
    alternatives["Metro"] = (total_monthly_km * emission_factors["public_transport"]["metro"])
    
    # Add car sharing options if not already selected
    if not (vehicle_type == "Four Wheeler" and "rideshare" in locals() and rideshare and people_count >= 3):
        alternatives["Car Pooling (4 people)"] = (total_monthly_km * emission_factors["four_wheeler"]["sedan"]["petrol"]["base"] * 
                                                emission_factors["four_wheeler"]["sedan"]["petrol"]["uplift"]) / 4
    
    # Add electric vehicle options if not already selected
    if not (vehicle_type == "Four Wheeler" and "fuel_type" in locals() and fuel_type == "electric"):
        alternatives["Electric Car"] = (total_monthly_km * emission_factors["four_wheeler"]["sedan"]["electric"]["base"] * 
                                      emission_factors["four_wheeler"]["sedan"]["electric"]["uplift"])
    
    if not (vehicle_type == "Two Wheeler" and "fuel_type" in locals() and fuel_type == "electric"):
        alternatives["Electric Scooter"] = (total_monthly_km * emission_factors["two_wheeler"]["Scooter"]["electric"]["min"])
    
    st.session_state.emissions_data = alternatives
    
    # Generate recommendations
    recommendations = []
    
    # Basic recommendation based on emissions
    if total_emissions > 100:
        recommendations.append("Your carbon footprint from commuting is quite high. Consider switching to more sustainable transport options.")
    elif total_emissions > 50:
        recommendations.append("Your carbon footprint is moderate. There's room for improvement by considering more sustainable options.")
    else:
        recommendations.append("Your carbon footprint is relatively low, but you can still make improvements.")
    
    # Specific recommendations
    if vehicle_type == "Four Wheeler" and people_count == 1:
        recommendations.append("Consider carpooling to reduce emissions. Sharing your ride with 3 other people could reduce your emissions by up to 75%.")
    
    if "fuel_type" in locals() and fuel_type in ["petrol", "diesel"] and vehicle_type != "Public Transport":
        recommendations.append("Consider switching to an electric vehicle to significantly reduce your carbon footprint.")
    
    # Compare with public transit options for personal vehicles
    if vehicle_type in ["Four Wheeler", "Two Wheeler"]:
        bus_emissions = total_monthly_km * emission_factors["public_transport"]["bus"]["electric"]
        metro_emissions = total_monthly_km * emission_factors["public_transport"]["metro"]
        
        if total_emissions > 2 * bus_emissions:
            recommendations.append(f"Using an electric bus could reduce your emissions by approximately {(total_emissions - bus_emissions) / total_emissions * 100:.1f}%.")
        
        if total_emissions > 2 * metro_emissions:
            recommendations.append(f"Using metro could reduce your emissions by approximately {(total_emissions - metro_emissions) / total_emissions * 100:.1f}%.")
    
    st.session_state.recommendations = recommendations

# Display results if calculation has been done
if st.session_state.calculated:
    st.divider()
    st.header("Carbon Footprint Results")
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display the total emissions with a metric and color coding
        total_kg = st.session_state.total_emissions
        total_tonnes = total_kg / 1000
        
        if total_kg > 100:
            emissions_color = "red"
        elif total_kg > 50:
            emissions_color = "orange"
        else:
            emissions_color = "green"
        
        st.metric(
            "Monthly CO₂ Emissions",
            f"{total_kg:.1f} kg CO₂e",
        )
        
        st.markdown(f"<div style='color:{emissions_color}; font-size:18px;'><strong>Sustainability Rating:</strong> {['Low', 'Moderate', 'High'][int(min(2, total_kg/50))]}</div>", unsafe_allow_html=True)
        
        # Context comparison
        avg_emissions = 200  # Example average emissions for commuting per person per month
        if total_kg < avg_emissions:
            st.success(f"Your emissions are {(1 - total_kg/avg_emissions) * 100:.1f}% lower than the average commuter.")
        else:
            st.warning(f"Your emissions are {(total_kg/avg_emissions - 1) * 100:.1f}% higher than the average commuter.")
    
    with col2:
        # Create a gauge chart for visual impact
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = total_kg,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Monthly CO₂ Emissions (kg)"},
            gauge = {
                'axis': {'range': [None, 300], 'tickwidth': 1},
                'bar': {'color': emissions_color},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 100], 'color': "yellow"},
                    {'range': [100, 300], 'color': "salmon"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': avg_emissions
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Show comparison chart of alternatives
    st.subheader("Comparison with Alternative Transport Options")
    
    # Create dataframe for plotting
    df = pd.DataFrame({
        'Transport Mode': list(st.session_state.emissions_data.keys()),
        'Monthly CO₂ Emissions (kg)': list(st.session_state.emissions_data.values())
    })
    
    # Sort by emissions for better visualization
    df = df.sort_values('Monthly CO₂ Emissions (kg)')
    
    # Create the comparison bar chart
    fig = px.bar(
        df, 
        y='Transport Mode', 
        x='Monthly CO₂ Emissions (kg)',
        orientation='h',
        color='Monthly CO₂ Emissions (kg)',
        color_continuous_scale='RdYlGn_r'
    )
    
    # Highlight the user's current transport mode
    current_mode = df['Transport Mode'].iloc[-1]  # Current mode should be the first one
    
    fig.update_layout(height=400, width=800)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display recommendations
    st.header("Sustainability Recommendations")
    for i, rec in enumerate(st.session_state.recommendations):
        st.markdown(f"**{i+1}. {rec}**")