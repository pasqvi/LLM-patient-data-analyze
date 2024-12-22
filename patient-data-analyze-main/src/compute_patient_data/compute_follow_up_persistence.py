"""
Compute the follow-up persistence for each patient in the group
"""

from pandas import DataFrame, Timestamp
from datetime import timedelta
from utils.parse_datetime import parse_datetime


def compute_follow_up_persistence(max_delivery_date: Timestamp, group: DataFrame):
    """
    Compute the follow-up persistence for each patient in the group
    :param max_delivery_date: maximum delivery date to compute difference
    :param group: group
    :return: follow-up persistence
    """
    last_delivery_date = group["DT_EROG"].iloc[-1]

    # If pandas has not already parsed the dates, then parse it
    max_delivery_date = parse_datetime(max_delivery_date)
    last_delivery_date = parse_datetime(last_delivery_date)




    y = group["giorni di terapia reali (PDD)"].iloc[-1] + 60  #giorni terapia teorici (DDD)      giorni di terapia reali (PDD)
    x = last_delivery_date + timedelta(days=int(y))

    if x > max_delivery_date:
        return 1

    return 0

