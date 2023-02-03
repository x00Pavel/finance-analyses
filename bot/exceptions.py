class BotException(Exception):
    def __init__(self, msg=None, tg_msg=None):
        if msg is not None:
            self.msg = msg
        if tg_msg is not None:
            self.tg_message = tg_msg
