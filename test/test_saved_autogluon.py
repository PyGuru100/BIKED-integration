import unittest

from src import load_data
from src.MultilabelPredictor import MultilabelPredictor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import sklearn.metrics
import pandas as pd
import os
import __main__


class AutogluonLearningTest(unittest.TestCase):
    def setUp(self) -> None:
        __main__.MultilabelPredictor = MultilabelPredictor
        relative_path = "AutogluonModels/ag-20220911_073209"
        self.multi_predictor = MultilabelPredictor.load(os.path.abspath(relative_path))

    def test_can_get_labels(self):
        self.multi_predictor: MultilabelPredictor
        labels_from_predictor = list(self.multi_predictor.labels.values)
        assert labels_from_predictor == ['Sim 1 Dropout X Disp.', 'Sim 1 Dropout Y Disp.',
                                         'Sim 1 Bottom Bracket X Disp.', 'Sim 1 Bottom Bracket Y Disp.',
                                         'Sim 2 Bottom Bracket Z Disp.', 'Sim 3 Bottom Bracket Y Disp.',
                                         'Sim 3 Bottom Bracket X Rot.', 'Sim 1 Safety Factor',
                                         'Sim 3 Safety Factor', 'Model Mass']

    def test_can_predict(self):
        x_scaled, y, _, xscaler = self.get_data()

        y = self.filter_y(y)
        x_scaled = x_scaled.loc[y.index]

        y_scaled = self.standard_scaling(y)

        x_test, y_test = self.standard_split(x_scaled, y_scaled)

        predictions = self.multi_predictor.predict(x_test)
        r2, mse, mae = self.get_metrics(predictions, y_test)
        assert r2 > 0.93
        assert mse < 0.06
        assert mae < 0.11

    def filter_y(self, y):
        q = y.quantile(.95)
        for col in y.columns:
            y = y[y[col] <= q[col]]
        return y

    def get_data(self):
        return load_data.load_framed_dataset("r", onehot=True, scaled=True, augmented=True)

    def standard_split(self, x_scaled, y_scaled):
        x_train, x_test, y_train, y_test = train_test_split(x_scaled, y_scaled, test_size=0.2, random_state=2021)
        return x_test, y_test

    def get_metrics(self, predictions, y_test):
        r2 = sklearn.metrics.r2_score(y_test, predictions)
        mse = sklearn.metrics.mean_squared_error(y_test, predictions)
        mae = sklearn.metrics.mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def standard_scaling(self, data):
        data_scaler = StandardScaler()
        data_scaler.fit(data)
        data_scaled = data_scaler.transform(data)
        data_scaled = pd.DataFrame(data_scaled, columns=data.columns, index=data.index)
        return data_scaled

    def get_input_labels(self):
        with open("../resources/labels.txt", "r") as file:
            return file.readlines()
