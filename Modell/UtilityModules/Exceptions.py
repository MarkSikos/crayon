class InvalidUserTitleException(Exception):
    """ Ha a Programban véletlenül nem megfelelő típusú user lenne bevíve. """

    def __init__(self, message="InvalidUserTitleException"):
        self.message = message
        super().__init__(self.message)
        
        
class DatabaseException(Exception):
    """ A Modellben fellépő Adatbázishibákat jelző Exception oszály.  """

    def __init__(self, message="DatabaseException - Az adatbázisban hiba lépett fel."):
        self.message = message
        super().__init__(self.message)
        
      
class FileSystemException(Exception):
    """ A Modellben fellépő Fájlrendszerhibákat jelző Exception oszály.  """

    def __init__(self, message="FileSystemException - A filerendszerben hiba lépett fel."):
        self.message = message
        super().__init__(self.message)