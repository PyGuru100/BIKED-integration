import pandas as pd


def get_row(_dict) -> pd.DataFrame:
    model_input_dict = {key: float(value) for key, value in _dict.items()}
    return get_row_from_dict(model_input_dict)


def get_row_from_dict(model_input_dict) -> pd.DataFrame:
    return pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))


def get_dict_from_row(row) -> dict:
    return row.loc[first_row_index(row)].to_dict()


def first_row_index(dataframe) -> int:
    return dataframe.index.values[0]