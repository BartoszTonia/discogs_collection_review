from decouple import config

class Credentials:
    def __init__(self):
        self.user = config('USER')
        self.token = config('TOKEN')
        self.mail_out = config('MAIL_OUT')
        self.mail_pass = config('MAIL_PASS')
        self.mail_in = config('MAIL_IN')
        self.container_host = config('CONTAINER_HOST')