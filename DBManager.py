

class DBManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_user(self, user, password):
        raise NotImplementedError

    # for creating a new user
    def set_user(self, user, password):
        raise NotImplementedError

    def get_chats(self, lat, lon):
        raise NotImplementedError

    # returns chat info, enrolls, last n messages
    def get_chat(self, chatID, history=50):
        raise NotImplementedError

    # modifies chat info
    def set_chat(self, chatID, name=None, lat=None, lon=None, description=None):
        raise NotImplementedError

    def receive_message(self, userID, chatID, message):
        raise NotImplementedError

    def set_enrollment(self, userID, chatID, isModerator=None, isBanned=None):
        raise NotImplementedError
