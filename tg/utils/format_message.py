def format_where_tokens(data):
    content = ["*===Tokens that were found===*"]
    for index, row in data.iterrows():
        content.append(
            f'{index} -Token: {row["token"]} | Address: *{row["address"]}* | Chain: {row["chain"]} | Amount: *{row["amount"]:,.2f}*'
        )
        content.append("=" * 32)

    text = "\n".join(content)
    return text
