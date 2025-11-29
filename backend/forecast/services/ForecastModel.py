# forecast/services/forecast_model.py  ← CHA
from abc import ABC, abstractmethod
from typing import Dict, Any
import time


class ForecastModel(ABC):
    def __init__(self, name: str):
        self.name = name
        self.train_time = 0.0
        self.predict_time = 0.0

    @abstractmethod
    def fit(self, train_data):
        pass

    @abstractmethod
    def predict(self, future_data):
        pass

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "model": self.name,
            "train_time": round(self.train_time, 3),
            "predict_time": round(self.predict_time, 3)
        }