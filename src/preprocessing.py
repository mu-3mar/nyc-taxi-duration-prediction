"""Feature preprocessing for trip duration prediction."""

import pandas as pd
import numpy as np


class TripDataPreprocessor:
    """Preprocess NYC taxi trip data for duration prediction."""

    def __init__(self):
        self.fitted = False

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Radius of Earth in km
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c

    def extract_time_features(self, df):
        df = df.copy()
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
        df["pickup_hour"] = df["pickup_datetime"].dt.hour
        df["pickup_dayofweek"] = df["pickup_datetime"].dt.dayofweek
        df["pickup_day"] = df["pickup_datetime"].dt.day
        df["pickup_month"] = df["pickup_datetime"].dt.month
        return df

    def compute_distance(self, df):
        df = df.copy()
        df["distance"] = self.haversine_distance(
            df["pickup_latitude"],
            df["pickup_longitude"],
            df["dropoff_latitude"],
            df["dropoff_longitude"],
        )
        return df

    def log_transform(self, df, transform_target=True):
        df = df.copy()
        df["distance"] = np.log1p(df["distance"])
        if transform_target and "trip_duration" in df.columns:
            df["trip_duration"] = np.log1p(df["trip_duration"])
        return df

    def drop_columns(self, df):
        drop_cols = [
            "id",
            "vendor_id",
            "pickup_datetime",
            "store_and_fwd_flag",
            "pickup_day",
            "passenger_count",
        ]
        df = df.drop(
            columns=[col for col in drop_cols if col in df.columns], errors="ignore"
        )
        return df

    def fit(self, df):
        self.fitted = True
        return self

    def transform(self, df, is_train=True):
        if not self.fitted:
            raise ValueError("Call fit() before transform()")
        df = self.extract_time_features(df)
        df = self.compute_distance(df)
        df = self.log_transform(df, transform_target=is_train)
        df = self.drop_columns(df)
        return df

    def fit_transform(self, df, is_train=True):
        return self.fit(df).transform(df, is_train=is_train)
