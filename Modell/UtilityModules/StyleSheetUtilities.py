from Modell.UtilityModules.Exceptions import FileSystemException

class StyleSheetUtilities:
    """ 
    A felhasználói felület stíluslapjainak kezeléséért felelős osztály.
    """
    
    @staticmethod
    def load_stylesheet(window, path):
        """ A stíluslapok beolvasásáért felelő függvény """
        try:
            with open(path, "r") as f:
                stylesheet = f.read()
                window.setStyleSheet(stylesheet)
        except Exception as e:
            raise FileSystemException from e