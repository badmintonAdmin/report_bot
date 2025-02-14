from gsheets.get_data import *
from datetime import datetime


def all_format():
    current_date = datetime.now().strftime("*Top-Up Requirements %B %d, %Y*")
    title = [current_date, ""]
    policies = get_policies()
    pools = get_pools()
    epoch = get_epoch()
    loans = get_loans()
    combined_list = [*title, *policies, *pools, *epoch, *loans]
    result = "\n".join(combined_list)
    return result
