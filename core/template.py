from datetime import datetime


def generate_report(big_arr, cash_out):
    today = datetime.today().strftime("%B %d, %Y")
    report = [f"Balance Change Report for {today}\n"]
    big_arr = flatten_list(big_arr)

    for i, item in enumerate(big_arr, start=1):
        report.append(f"{i} {item}\n" + "=" * 34)

    # add cash_out
    if len(cash_out[0]) == 1:
        report.append(f"{cash_out[0][0]}")
    else:
        report.append(f"\n")
        report.append("==========CASH OUT============")
        report.append(f"LNDX Sold    | {cash_out[0][-1]}")
        report.append(f"Wallets Sold | {cash_out[0][0]}")

        for i, item in enumerate(cash_out[0][1:-1][:3], start=1):
            report.append(f"{i} {item}\n" + "=" * 34)

    return "\n".join(report)


def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list
