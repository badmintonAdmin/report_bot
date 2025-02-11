from core.get_data import *
from core.template import generate_report


def get_report():

    data, cash_out = get_all_data()
    text = generate_report(data, cash_out)
    return text
