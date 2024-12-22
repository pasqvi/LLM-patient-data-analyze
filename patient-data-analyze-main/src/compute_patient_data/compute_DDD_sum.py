

from pandas import DataFrame


def compute_DDD(group: DataFrame):

    if len(group) > 1:
        return group["giorni terapia teorici (DDD)"][:-1].sum()

    return 0
