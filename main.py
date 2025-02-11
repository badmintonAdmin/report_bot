import random
import string
from datetime import datetime
from core.run import get_report


def generate_random_string(length=5):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def save_report_to_log():
    report = get_report()

    today = datetime.today().strftime("%Y_%m_%d")
    random_str = generate_random_string()
    filename = f"report_logs/{today}_{random_str}.txt"

    with open(filename, "w") as file:
        file.write(report)

    print(report)
    print(f"Report saved as {filename}")


if __name__ == "__main__":
    save_report_to_log()
