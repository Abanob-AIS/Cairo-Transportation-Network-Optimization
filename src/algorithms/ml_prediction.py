"""
ML-Based Traffic Prediction (Bonus)
======================================
Uses scikit-learn to predict traffic congestion from temporal data.
"""
import numpy as np
import time
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.data.cairo_data import TRAFFIC_FLOW, EXISTING_ROADS


class TrafficPredictor:
    """
    ML-based traffic congestion predictor trained on temporal traffic data.
    
    Features: time_period_encoded, road_distance, road_capacity, road_condition,
              distance × capacity (interaction term)
    Target: traffic_flow (vehicles/hour)
    """

    TIME_ENCODING = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.metrics = {}

    def _build_dataset(self):
        """Build training dataset from provided traffic flow data."""
        X, y = [], []
        road_lookup = {}
        for road in EXISTING_ROADS:
            key = (road["from"], road["to"])
            road_lookup[key] = road

        for (from_id, to_id), flows in TRAFFIC_FLOW.items():
            road = road_lookup.get((from_id, to_id)) or road_lookup.get((to_id, from_id))
            if not road:
                continue
            for period, flow in flows.items():
                features = [
                    self.TIME_ENCODING[period],
                    road["distance"],
                    road["capacity"],
                    road["condition"],
                    road["distance"] * road["capacity"],  # interaction feature
                ]
                X.append(features)
                y.append(flow)

        return np.array(X), np.array(y)

    def train(self, model_type="random_forest"):
        """Train the prediction model with proper train/test split to avoid data leakage."""
        start_time = time.perf_counter()
        X, y = self._build_dataset()

        if model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
        else:
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=5)

        # --- Proper train/test split to prevent data leakage ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features (fit on train only, transform both)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Cross-validation on training set
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='r2')

        # Train on training set
        self.model.fit(X_train_scaled, y_train)

        # Evaluate on held-out test set (no leakage)
        test_pred = self.model.predict(X_test_scaled)
        mse = float(mean_squared_error(y_test, test_pred))
        mae = float(mean_absolute_error(y_test, test_pred))
        r2 = float(r2_score(y_test, test_pred))

        # Refit on full dataset for production predictions
        X_scaled_full = self.scaler.fit_transform(X)
        self.model.fit(X_scaled_full, y)
        self.is_trained = True

        self.metrics = {
            "model_type": model_type,
            "cv_r2_mean": round(float(np.mean(cv_scores)), 4),
            "cv_r2_std": round(float(np.std(cv_scores)), 4),
            "test_r2": round(r2, 4),
            "test_mse": round(mse, 2),
            "test_mae": round(mae, 2),
            "test_rmse": round(float(np.sqrt(mse)), 2),
            "n_samples": len(y),
            "n_train": len(y_train),
            "n_test": len(y_test),
            "training_time": time.perf_counter() - start_time,
        }

        if hasattr(self.model, 'feature_importances_'):
            names = ["time_period", "distance", "capacity", "condition", "dist_x_cap"]
            self.metrics["feature_importance"] = dict(
                zip(names, [round(float(v), 4) for v in self.model.feature_importances_])
            )

        return self.metrics

    def predict(self, time_period, distance, capacity, condition):
        """Predict traffic flow for given conditions."""
        if not self.is_trained:
            self.train()
        features = np.array([[
            self.TIME_ENCODING.get(time_period, 0),
            distance, capacity, condition,
            distance * capacity,
        ]])
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        return {
            "predicted_flow": round(float(prediction), 0),
            "congestion_ratio": round(float(prediction / capacity), 3),
            "congestion_level": (
                "Low" if prediction / capacity < 0.5 else
                "Moderate" if prediction / capacity < 0.75 else
                "High" if prediction / capacity < 0.9 else "Severe"
            ),
        }

    def predict_all_roads(self, time_period="morning"):
        """Predict traffic for all existing roads at a given time."""
        if not self.is_trained:
            self.train()
        predictions = {}
        for road in EXISTING_ROADS:
            key = f"{road['from']}→{road['to']}"
            predictions[key] = self.predict(
                time_period, road["distance"], road["capacity"], road["condition"]
            )
            predictions[key]["road"] = road
        return predictions
