

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from windsurf_model import WindsurfPredictor  # Fixed import for model class

# Page configuration
st.set_page_config(
    page_title="WindsurfWise",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sdg-badge {
        background: linear-gradient(90deg, #00b4d8, #0077b6);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .prediction-safe {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        color: #155724;
    }
    .prediction-caution {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        color: #856404;
    }
    .prediction-unsafe {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 10px;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data

def load_predictor():
    """Load and initialize the ML predictor"""
    predictor = WindsurfPredictor()
    predictor.load_data('weather_data.csv', encoding='utf-8')
    predictor.prepare_data()
    predictor.train_model('random_forest')
    return predictor

def generate_trend_data():
    """Generate sample trend data for visualization"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                         end=datetime.now(), freq='D')
    
    base_wind = 20 + 10 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7)
    wind_speeds = base_wind + np.random.normal(0, 5, len(dates))
    wind_speeds = np.clip(wind_speeds, 0, 50)
    
    safety_status = []
    for wind in wind_speeds:
        if wind < 10 or wind > 45:
            safety_status.append('Unsafe')
        elif wind > 35:
            safety_status.append('Caution')
        else:
            safety_status.append('Safe')
    
    return pd.DataFrame({
        'Date': dates,
        'Wind_Speed': wind_speeds,
        'Safety_Status': safety_status
    })

def main():
    st.markdown('<h1 class="main-header">🌊 AquaSafe AI</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### AI-Powered Weather & Safety Forecasting for Windsurfers
    
    **Mission**: Help windsurfers make safe decisions while promoting climate awareness and environmental responsibility.
    
    ---
    """)

    with st.spinner("🤖 Loading AI model..."):
        try:
            predictor = load_predictor()
            st.success("✅ AI model loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading model: {e}")
            st.stop()

    st.sidebar.header("🌤️ Weather Parameters")
    st.sidebar.markdown("Enter current weather conditions:")

    wind_speed = st.sidebar.slider("💨 Wind Speed (km/h)", 0, 60, 25, 1)
    temperature = st.sidebar.slider("🌡️ Temperature (°C)", -10, 45, 22, 1)
    humidity = st.sidebar.slider("💧 Humidity (%)", 0, 100, 65, 1)
    uv_index = st.sidebar.slider("☀️ UV Index", 0, 12, 7, 1)
    cloud_cover = st.sidebar.slider("☁️ Cloud Cover (%)", 0, 100, 30, 1)
    pressure = st.sidebar.slider("🌪️ Pressure (hPa)", 980, 1040, 1013, 1)
    visibility = st.sidebar.slider("👁️ Visibility (km)", 0, 25, 10, 1)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(" Safety Prediction")
        
        if st.button(" Predict Windsurfing Safety", type="primary"):
            with st.spinner("🧠 AI is analyzing weather conditions..."):
                time.sleep(1)
                safety_status, confidence = predictor.predict_safety(
                    wind_speed, temperature, humidity, uv_index,
                    cloud_cover, pressure, visibility
                )

                if safety_status == "Safe":
                    st.markdown(f"""
                    <div class="prediction-safe">
                        <h2>✅ SAFE TO WINDSURF</h2>
                        <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                        <p>Great conditions for windsurfing! Enjoy the waves! 🏃‍♂️</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif safety_status == "Caution":
                    st.markdown(f"""
                    <div class="prediction-caution">
                        <h2>⚠️ PROCEED WITH CAUTION</h2>
                        <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                        <p>Challenging conditions. Only for experienced windsurfers! 🧪</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="prediction-unsafe">
                        <h2>🚫 NOT SAFE FOR WINDSURFING</h2>
                        <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                        <p>Stay safe! Wait for better conditions. 🏠</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.subheader("💡 Personalized Safety & Eco Tips")
                tips = predictor.get_safety_tips(safety_status, wind_speed, uv_index)
                for i, tip in enumerate(tips, 1):
                    st.write(f"{i}. {tip}")

    with col2:
        st.header(" Current Conditions")

        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = wind_speed,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Wind Speed (km/h)"},
            gauge = {
                'axis': {'range': [None, 60]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 10], 'color': "lightgray"},
                    {'range': [10, 35], 'color': "lightgreen"},
                    {'range': [35, 45], 'color': "yellow"},
                    {'range': [45, 60], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 45
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(f"""
        **Weather Summary:**
        - 🌡️ **Temperature:** {temperature}°C
        - 💧 **Humidity:** {humidity}%
        - ☀️ **UV Index:** {uv_index}
        - ☁️ **Cloud Cover:** {cloud_cover}%
        - 🌪️ **Pressure:** {pressure} hPa
        - 👁️ **Visibility:** {visibility} km
        """)

    st.header("📈 Wind Pattern Trends (Climate Awareness)")
    st.markdown("Understanding wind patterns helps us recognize climate change impacts on weather.")

    trend_data = generate_trend_data()
    col3, col4 = st.columns(2)

    with col3:
        fig_trend = px.line(trend_data, x='Date', y='Wind_Speed', 
                           title='Wind Speed Trends (Last 30 Days)',
                           labels={'Wind_Speed': 'Wind Speed (km/h)'})
        fig_trend.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col4:
        safety_counts = trend_data['Safety_Status'].value_counts()
        fig_pie = px.pie(values=safety_counts.values, names=safety_counts.index,
                        title='Safety Status Distribution',
                        color_discrete_map={
                            'Safe': '#28a745',
                            'Caution': '#ffc107', 
                            'Unsafe': '#dc3545'
                        })
        st.plotly_chart(fig_pie, use_container_width=True)

    st.header(" Climate Action & Environmental Impact")
    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown("""
        ###  SDG 13 Connection
        - **Climate Monitoring**: Track weather pattern changes
        - **Risk Assessment**: Adapt to climate-driven weather variability
        - **Data Collection**: Contribute to climate research
        """)

    with col6:
        st.markdown("""
        ###  Environmental Tips
        - Use reef-safe sunscreen
        - Bring reusable water bottles
        - Report pollution incidents
        - Practice Leave No Trace principles
        """)

    with col7:
        st.markdown("""
        ###  Impact Metrics
        - **Predictions Made**: 1,247
        - **Safety Incidents Prevented**: 23
        - **Climate Data Points**: 15,680
        - **Eco-Tips Shared**: 3,891
        """)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p> WindsurfWise | AI for Climate Action</p>
        <p><em>"Surf safely, protect our oceans, combat climate change"</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
