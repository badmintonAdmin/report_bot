from gsheets.get_data import *
from contracts.get_data import get_epoch
from datetime import datetime
from aiogram.utils import markdown as m


def all_format():
    current_date = datetime.now().strftime(m.hbold("Top-Up Requirements %B %d, %Y"))
    title = [current_date, ""]
    policies = get_policies()
    pools = get_pools()
    epoch = get_epoch()
    loans = get_loans()
    combined_list = [*title, *policies, *pools, *epoch, *loans]
    result = "\n".join(combined_list)
    return result
