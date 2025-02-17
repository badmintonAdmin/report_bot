from report.get_data import *
from report.template import generate_report


def get_remote_report():

    data, cash_out = get_all_data()
    text = generate_report(data, cash_out)
    return text
