from gsheets.get_data import *


def all_format():
    policies = get_policies()
    pools = get_pools()
    epoch = get_epoch()
    loans = get_loans()
    combined_list = policies + pools + epoch + loans
    result = "\n".join(combined_list)
    return result
