"""
Compute the number of delays between treatments for each patient in the group
"""

from pandas import DataFrame

from utils.parse_datetime import parse_datetime


def compute_delays(group: DataFrame):
    """
    Compute the number of delays between treatments for each patient in the group
    :param group: group
    :return: number of delays between treatments for each patient in the group
    """
    count = 0

    for i in range(len(group["DT_EROG"]) - 1):
        end_date = group["DT_EROG"].iloc[i + 1]
        start_date = group["DT_EROG"].iloc[i]

        # If pandas has not already parsed the dates, then parse it
        start_date = parse_datetime(start_date)
        end_date = parse_datetime(end_date)

        interval_days = (end_date - start_date).days
        if interval_days >= (35 * group["QTA"].iloc[i]):
            count += 1

    return count
