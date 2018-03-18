

class DBManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_user(self, username, password):
        raise NotImplementedError

    # for creating a new user
    def set_user(self, username, password):
        raise NotImplementedError

    def get_nearby_chats(self, location):
        raise NotImplementedError

    def get_user_chats(self, username):
        raise NotImplementedError

    # returns chat info, enrolls, last n messages
    def get_chat(self, chatID, history=50):
        raise NotImplementedError

    # modifies chat info
    def set_chat(self, chatID=None, username=None, location=None, description=None):
        raise NotImplementedError

    def new_message(self, chatID, username, message):
        raise NotImplementedError

    def set_enrollment(self, chatID, username, moderator=None, banned=None):
        raise NotImplementedError
