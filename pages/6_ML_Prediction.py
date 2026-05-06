"""Page 6: ML-Based Traffic Prediction (Bonus)"""
import streamlit as st
from src.algorithms.ml_prediction import TrafficPredictor
from src.visualization.charts import plot_prediction_results
from src.data.cairo_data import TIME_PERIOD_LABELS, EXISTING_ROADS, get_all_nodes
import plotly.graph_objects as go

st.set_page_config(page_title="ML Prediction", page_icon="🤖", layout="wide")
st.markdown("# 🤖 ML-Based Traffic Prediction")
st.markdown("Predict congestion using **Random Forest / Gradient Boosting** trained on temporal traffic data.")

nodes = get_all_nodes()

st.sidebar.header("🧠 ML Settings")
model_type = st.sidebar.selectbox("Model", ["random_forest", "gradient_boosting"])
time_period = st.sidebar.selectbox("Predict for", list(TIME_PERIOD_LABELS.keys()),
                                    format_func=lambda x: TIME_PERIOD_LABELS[x])

# ── Train Model ─────────────────────────────────────────────────────────────
predictor = TrafficPredictor()
with st.spinner("Training model..."):
    metrics = predictor.train(model_type)

tab1, tab2, tab3 = st.tabs(["📊 Predictions", "🎯 Model Performance", "🔍 Custom Prediction"])

with tab1:
    st.markdown(f"### Traffic Predictions — {TIME_PERIOD_LABELS[time_period]}")
    predictions = predictor.predict_all_roads(time_period)
    st.plotly_chart(plot_prediction_results(predictions), use_container_width=True)

    st.markdown("#### Congestion Levels")
    for road_key, pred in sorted(predictions.items(),
                                  key=lambda x: x[1]["congestion_ratio"], reverse=True):
        road = pred["road"]
        from_name = nodes.get(road["from"], {}).get("name", road["from"])
        to_name = nodes.get(road["to"], {}).get("name", road["to"])
        level = pred["congestion_level"]
        icon = {"Low": "🟢", "Moderate": "🟡", "High": "🟠", "Severe": "🔴"}.get(level, "⚪")
        st.write(f"{icon} **{from_name} → {to_name}**: {pred['predicted_flow']:.0f} veh/h "
                f"({pred['congestion_ratio']:.0%} capacity) — {level}")

with tab2:
    st.markdown("### 🎯 Model Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CV R² Score", f"{metrics['cv_r2_mean']:.4f}")
    col2.metric("Test MAE", f"{metrics['test_mae']:.1f}")
    col3.metric("Test RMSE", f"{metrics['test_rmse']:.1f}")
    col4.metric("Test R²", f"{metrics['test_r2']:.4f}")

    st.caption(f"Trained on {metrics['n_train']} samples, evaluated on {metrics['n_test']} held-out samples "
               f"(training time: {metrics['training_time']*1000:.1f} ms)")

    if "feature_importance" in metrics:
        st.markdown("#### Feature Importance")
        fi = metrics["feature_importance"]
        fig = go.Figure(go.Bar(
            x=list(fi.values()), y=list(fi.keys()), orientation="h",
            marker_color="#4FC3F7",
        ))
        fig.update_layout(
            title="Feature Importance",
            plot_bgcolor="#1a1a2e", paper_bgcolor="#16213e",
            font=dict(color="white"), height=300,
            xaxis=dict(color="white"), yaxis=dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🔍 Custom Road Prediction")
    col1, col2 = st.columns(2)
    with col1:
        pred_period = st.selectbox("Time Period", list(TIME_PERIOD_LABELS.keys()),
                                   format_func=lambda x: TIME_PERIOD_LABELS[x], key="pred_period")
        distance = st.number_input("Road Distance (km)", 1.0, 100.0, 10.0, 0.5)
    with col2:
        capacity = st.number_input("Road Capacity (veh/h)", 1000, 5000, 3000, 100)
        condition = st.slider("Road Condition", 1, 10, 7)

    pred = predictor.predict(pred_period, distance, capacity, condition)
    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted Flow", f"{pred['predicted_flow']:.0f} veh/h")
    col2.metric("Congestion Ratio", f"{pred['congestion_ratio']:.0%}")
    col3.metric("Level", pred['congestion_level'])
