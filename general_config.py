from dotenv import dotenv_values


class Config:
    def __init__(self):
        values = dotenv_values()
        for key, value in values.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__dict__}"


config = Config()
