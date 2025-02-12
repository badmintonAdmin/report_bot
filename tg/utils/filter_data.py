def apply_amount_filter(data, filter_value):
    filter_value = filter_value.strip()
    try:
        operator = filter_value[0]
        amount = float(filter_value[1:])
        if operator == ">":
            filtered = data[data["amount"] > amount]
            return filtered
        elif operator == "<":
            filtered = data[data["amount"] < amount]
            return filtered

    except (ValueError, IndexError):
        pass

    return data
