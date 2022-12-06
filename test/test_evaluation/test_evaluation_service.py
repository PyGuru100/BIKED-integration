import os.path
import unittest

import pandas_utility as pd_util
from main.evaluation.evaluation_service import EvaluationService
from main.request_adapter.scaler_wrapper import ScalerWrapper
from sklearn.model_selection import train_test_split

RESOURCES_PATH = "../../resources/"
BIKES_PATH = "../../resources/bikes/"

LABELS_PATH = os.path.join(os.path.dirname(__file__), RESOURCES_PATH + "labels.txt")
FIRST_BIKE_PATH = os.path.join(os.path.dirname(__file__), BIKES_PATH + "FullModel1.xml")
SECOND_BIKE_PATH = os.path.join(os.path.dirname(__file__), BIKES_PATH + "FullModel2.xml")
THIRD_BIKE_PATH = os.path.join(os.path.dirname(__file__), BIKES_PATH + "bike(1).xml")


class EvaluationServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.service = EvaluationService()
        self.x, self.y, request_scaler, result_scaler = self.prepare_x_y()
        self.request_scaler = ScalerWrapper(request_scaler, self.x.columns)
        self.result_scaler = ScalerWrapper(result_scaler, self.y.columns)
        self.sample_input = {'Material=Steel': -1.2089779626768866, 'Material=Aluminum': -0.46507861303022335,
                             'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
                             'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
                             'BB Drop': 0.19327064177679704, 'Stack': -0.036955840782382385,
                             'SS E': -0.4348758585162575, 'ST Angle': 1.203226228166099, 'BB OD': -0.14197615979296274,
                             'TT OD': -0.5711431568166616, 'HT OD': -0.879229453202825, 'DT OD': -0.8924125880651749,
                             'CS OD': -0.6971543225296617, 'SS OD': -0.7226114906751929, 'ST OD': -0.8962254490159303,
                             'CS F': 0.1664798679079193, 'HT LX': -0.5559202673887266, 'ST UX': -0.5875970924732736,
                             'HT UX': -0.1666775498399638, 'HT Angle': 1.5120924379123033,
                             'HT Length': 0.7032710935570091, 'ST Length': 0.980667290296069,
                             'BB Length': -0.25473226064604454, 'Dropout Offset': -0.0325700226355687,
                             'SSB OD': -2.1985552817712657, 'CSB OD': -0.279547847307574,
                             'SSB Offset': -0.09050848378506038, 'CSB Offset': 0.5823537937924539,
                             'SS Z': -0.06959536571235439, 'SS Thickness': 0.5180142556590571,
                             'CS Thickness': 1.7994950500929077, 'TT Thickness': 0.2855204217004274,
                             'BB Thickness': -0.11934492802927218, 'HT Thickness': -0.7465363724789722,
                             'ST Thickness': -0.5700521782698762, 'DT Thickness': -1.0553146425778421,
                             'DT Length': 0.10253602811555089}
        self.expected_output = {'Model Mass Magnitude': 3.189100876474357,
                                'Sim 1 Bottom Bracket X Disp. Magnitude': 0.012183772767391373,
                                'Sim 1 Bottom Bracket Y Disp. Magnitude': 0.012939156170363236,
                                'Sim 1 Dropout X Disp. Magnitude': 0.011111431121145088,
                                'Sim 1 Dropout Y Disp. Magnitude': 0.021787148423259715,
                                'Sim 2 Bottom Bracket Z Disp. Magnitude': 0.0023485019730819755,
                                'Sim 3 Bottom Bracket X Rot. Magnitude': 0.0063891630717543306,
                                'Sim 3 Bottom Bracket Y Disp. Magnitude': 0.01666142336216584,
                                'Sim 1 Safety Factor (Inverted)': 0.542653611374427,
                                'Sim 3 Safety Factor (Inverted)': 0.6966032103094124}

    def test_report_performance(self):
        with open(THIRD_BIKE_PATH, "r") as file:
            xml_as_string = file.read()
        xml_response = self.service.predict_from_xml(xml_as_string)

        scaled_response = pd_util.get_dict_from_row(self.service._predict_from_row(self.x.iloc[:1]))
        entry_response = self.result_scaler.unscale(scaled_response)

        report = ""

        for key, value in xml_response.items():
            report = self.add_to_report(key, report)
            report = self.add_to_report(f"Xml value: {value}", report)
            report = self.add_to_report(f"Entry value: {entry_response[key]}", report)
            report = self.add_to_report(
                f"Percent difference: {round(((value - entry_response[key]) / entry_response[key]) * 100, 3)}%", report)
            report = self.add_to_report("*" * 5, report)
        with open('performance_report.txt', "w") as file:
            file.write(report)

    def add_to_report(self, entry, report):
        report += entry + "\n"
        return report

    def test_can_predict_from_partial_request(self):
        self.sample_input = self.request_scaler.unscale(self.sample_input)
        print(self.service.predict_from_dict(self.sample_input))

    def test_can_get_labels(self):
        self.assertEqual({"Sim 1 Dropout X Disp. Magnitude",
                          "Sim 1 Dropout Y Disp. Magnitude",
                          "Sim 1 Bottom Bracket X Disp. Magnitude",
                          "Sim 1 Bottom Bracket Y Disp. Magnitude",
                          "Sim 2 Bottom Bracket Z Disp. Magnitude",
                          "Sim 3 Bottom Bracket Y Disp. Magnitude",
                          "Sim 3 Bottom Bracket X Rot. Magnitude",
                          "Sim 1 Safety Factor (Inverted)",
                          "Sim 3 Safety Factor (Inverted)", "Model Mass Magnitude"},
                         set(self.service.get_labels()))

    def test_model_and_scalers_loaded(self):
        predictions = self.service._predict_from_row(self.x)
        self.assert_correct_metrics(predictions, self.y)
        self.assert_correct_metrics(self.result_scaler.scaler.inverse_transform(predictions),
                                    self.result_scaler.scaler.inverse_transform(self.y))

    def test_can_predict_singular_row(self):
        model_input = self.get_first_row(self.x)
        prediction = self.service.predict_from_row(model_input)
        self.assertEqual(pd_util.get_dict_from_row(model_input), self.sample_input)
        self.assertEqual(prediction,
                         self.expected_output)
        model_input_from_dict = pd_util.get_row_from_dict(self.sample_input)
        self.assertEqual(self.service.predict_from_row(model_input_from_dict),
                         self.expected_output)

    def test_order_does_not_matter(self):
        input_in_different_order = {key: self.sample_input[key]
                                    for key in sorted(self.sample_input.keys())}
        self.assertEqual(self.service.predict_from_dict(self.sample_input),
                         self.service.predict_from_dict(input_in_different_order))

    def test_input_shape(self):
        self.assertEqual(list(self.x.columns.values), self.get_input_labels())

    def test_cannot_predict_from_partial_row(self):
        incomplete_model_input = pd_util.get_row_from_dict(
            {"Material=Steel": -1.2089779626768866, "Material=Aluminum": -0.46507861303022335,
             "Material=Titanium": 1.8379997074342262, "SSB_Include": 1.0581845284004865,
             "CSB_Include": -0.9323228669601348, "CS Length": -0.4947762070020683,
             "BB Drop": 0.19327064177679704})
        self.assertRaises(KeyError, self.service.predict_from_row,
                          incomplete_model_input)

    def assert_correct_metrics(self, predictions, actual):
        r2, mean_square_error, mean_absolute_error = self.service.get_metrics(predictions,
                                                                              actual)
        self.assertGreater(r2, 0.97)
        self.assertLess(mean_square_error, 0.025)
        self.assertLess(mean_absolute_error, 0.055)

    def first_row_index(self, dataframe):
        return dataframe.index.values[0]

    def get_first_row(self, dataframe):
        return dataframe[dataframe.index == self.first_row_index(dataframe)]

    def prepare_x_y(self):
        x_scaled, y_scaled, x_scaler, y_scaler = self.service.get_data()
        x_test, y_test = self.standard_split(x_scaled, y_scaled)
        return x_test, y_test, x_scaler, y_scaler

    def standard_split(self, x_scaled, y_scaled):
        x_train, x_test, y_train, y_test = train_test_split(x_scaled,
                                                            y_scaled,
                                                            test_size=0.2,
                                                            random_state=1950)
        return x_test, y_test

    def get_input_labels(self):
        with open(LABELS_PATH, "r") as file:
            return [line.strip() for line in file.readlines()]
