import unittest
from sample_request import request
from main.evaluation.evaluation_service import DefaultAdapterSettings, EvaluationService

SAFETY_3_INVERTED = 'Sim 3 Safety Factor (Inverted)'

SAFETY_1_INVERTED = 'Sim 1 Safety Factor (Inverted)'

SIM_1_DEFLECTIONS = ['Sim 1 Bottom Bracket Y Disp. Magnitude',
                     'Sim 1 Dropout X Disp. Magnitude',
                     'Sim 1 Bottom Bracket X Disp. Magnitude',
                     'Sim 1 Dropout Y Disp. Magnitude']
SIM_2_DEFLECTIONS = ['Sim 2 Bottom Bracket Z Disp. Magnitude']
SIM_3_DEFLECTIONS = ['Sim 3 Bottom Bracket X Rot. Magnitude',
                     'Sim 3 Bottom Bracket Y Disp. Magnitude']
DEFLECTIONS = SIM_1_DEFLECTIONS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS

DIAMETER_PARAMETERS = ['BB OD', 'TT OD', 'HT OD', 'DT OD', 'CS OD', 'SS OD', 'ST OD', 'SSB OD', 'CSB OD']
THICKNESS_PARAMETERS = ['SS Thickness', 'CS Thickness', 'TT Thickness', 'BB Thickness', 'HT Thickness', 'ST Thickness',
                        'DT Thickness']
DOWN_TUBE_LENGTH_PARAMETERS = ['DT Length']
SAFETY_INVERTED_PARAMETERS = [SAFETY_1_INVERTED, SAFETY_3_INVERTED]
MODEL_MASS_PARAMETERS = ['Model Mass Magnitude']

CHAIN_STAY_BRIDGE = ['CSB_Include']
SEAT_STAY_BRIDGE = ['SSB_Include']
STAY_BRIDGES = CHAIN_STAY_BRIDGE + SEAT_STAY_BRIDGE


def build_inner_dict(keys, values):
    return {"keys": keys, "values": values}


PROPORTIONAL = [
    build_inner_dict(DIAMETER_PARAMETERS, MODEL_MASS_PARAMETERS),
    build_inner_dict(DOWN_TUBE_LENGTH_PARAMETERS, MODEL_MASS_PARAMETERS + SIM_2_DEFLECTIONS + SIM_3_DEFLECTIONS),
    build_inner_dict(STAY_BRIDGES, SAFETY_3_INVERTED)
]

INVERSELY_PROPORTIONAL = [
    build_inner_dict(DIAMETER_PARAMETERS, [SAFETY_INVERTED_PARAMETERS, SIM_2_DEFLECTIONS, SIM_3_DEFLECTIONS]),
    build_inner_dict(STAY_BRIDGES, SIM_2_DEFLECTIONS + ['Sim 3 Bottom Bracket X Rot. Magnitude'])
]


class ModelAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EvaluationService()

    def test_alter_request(self):
        alter_request = self.alter_request(request, MODEL_MASS_PARAMETERS, [5])
        self.assertEqual(alter_request[MODEL_MASS_PARAMETERS[0]], 5)

    def alter_request(self, request_, keys_to_alter, new_values):
        for key, value in zip(keys_to_alter, new_values):
            request_[key] = value
        return request_
