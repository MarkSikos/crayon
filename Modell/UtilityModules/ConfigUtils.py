from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt
import os, secrets, time

IMAGE_DIR = 'Persistence/image_dump'

class ConfigUtils:
    """ 
    A képeknek a fájlrendszeren való létrehozásáért felelős Singleton osztály. 
    """
    
    # Konstruktor
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__instance_initialized = False
        return cls._instance

    def __init__(self):
        if not self.__instance_initialized:
            super().__init__()
            self.__instance_initialized = True
   
   # A logikát megvalósító függvények
   
    @staticmethod
    def create_and_save_big_image(width, height):
        """ Egy nagy kép létrehozásáért felelős függvény."""
        big_width = int(width * 0.6)
        big_height = int(height * 0.6)
        big_image = QImage(big_width, big_height, QImage.Format.Format_ARGB32)
        big_image.fill(Qt.GlobalColor.transparent)  
        
        timestamp = int(time.time() * 1000)
        random_token = secrets.token_hex(8) 
        unique_filename = f"{timestamp}-{random_token}.png"
        os.makedirs(IMAGE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_DIR, unique_filename)
        big_image.save(image_path, 'PNG')

        return(image_path)

    def create_small_image(self= None , path = None):
        """" Egy kis kép (feladatokhoz) létrehozásáért felelős függvény."""
        small_width = 400
        small_height = 200
        small_image = QImage(small_width, small_height, QImage.Format.Format_ARGB32)
        small_image.fill(Qt.GlobalColor.transparent)
        
        if path is None:
            timestamp = int(time.time() * 1000)
            random_token = secrets.token_hex(8) 
            unique_filename = f"{timestamp}-{random_token}.png"
            os.makedirs(IMAGE_DIR, exist_ok=True)
            image_path = os.path.join(IMAGE_DIR, unique_filename)
            small_image.save(image_path)
            return(image_path)
        else:
            image_path = path
        small_image.save(image_path)
        return(image_path)

    