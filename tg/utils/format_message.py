from aiogram.utils import markdown as m


def format_where_tokens(data):
    content = [m.hbold("===Tokens that were found===")]
    for index, row in data.iterrows():
        content.append(
            f'{index} -Token: {row["token"]} | Address: {m.hbold(row["address"])} | Chain: {row["chain"]} | Amount: {m.hbold(f'{row["amount"]:,.2f}')}'
        )
        content.append("=" * 32)

    text = "\n".join(content)
    return text
