import pytesseract
import keras_ocr
import cv2
from unidecode import unidecode
from PyQt6.QtCore import QObject, pyqtSignal
from fuzzywuzzy import process

class OCRUtils(QObject):
    """ 
    Az OCR-rel kapcsolatos feladatokért (szövegfelismerés, ajánlattevés) felelős osztály. 
    """
    
    # Események
    
    recognition_started = pyqtSignal()
    
    # Konstruktor
    
    def __init__(self):
        super().__init__()
        with open("Persistence/dictionary/hu.txt", 'r', encoding='utf-8') as file:
            raw_dictionary = file.read().splitlines()
            self.__dictionary  = [unidecode(word).lower() for word in raw_dictionary]
        self.__pipeline = keras_ocr.pipeline.Pipeline()
        keras_ocr.recognition.Recognizer().model.load_weights('Persistence/modell/halo.h5')
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'  
        self.__tesseract_config = r'--oem 3 --psm 11 -l hun'
        
    # Fő funkcionalitást megvalósító függvények
    
    def recognize_text(self, image_path):
        """ A jegyzetelés ablak számára szófelismerést és ajánlott szavak előállításának elindításáért felelős függvény. 
        Visszaadja az szó ajánlásokat. """
        self.recognition_started.emit()
        corrected_texts_keras = []
        corrected_texts_tesseracht = []
        image_path = image_path
        
        preprocessed_image = self.__preprocess_image(image_path)
        keras_prediction, _ = self.__get_keras_ocr_output(preprocessed_image)
        tesseract_prediction, _ = self.__get_tesseracht_output(preprocessed_image)
        
        if tesseract_prediction is not None:
            corrected_texts_tesseracht = self.__check_word(tesseract_prediction)
        if keras_prediction is not None:
            corrected_texts_keras = self.__check_word(keras_prediction)
        if corrected_texts_keras is not None:
            corrected_texts_keras = self.extract_first_two_strings(corrected_texts_keras)
        if corrected_texts_tesseracht is not None:
            corrected_texts_tesseracht = self.extract_first_two_strings(corrected_texts_tesseracht)
            
        return[corrected_texts_keras, corrected_texts_tesseracht]
    
    def recognize_text_test(self, image_path, answer):
        """ A jegyzetelés ablak számára szófelismerést és ajánlott szavak előállításának elindításáért felelős függvény. 
        Visszaadja a felismert szavakat (vagy None értéket), illetve hogy talált -e egyezést. """
        self.recognition_started.emit()
        image_path = image_path
        preprocessed_image = self.__preprocess_image(image_path)
        keras_prediction, _ = self.__get_keras_ocr_output(preprocessed_image, answer)
        tesseract_prediction, _ = self.__get_tesseracht_output(preprocessed_image, answer)
        return [keras_prediction, tesseract_prediction, True]
        
    def __get_keras_ocr_output(self,preprocessed_image, answer=None):
        """ A keras_ocr-el törénő képfelismerésért felelős függvény.
        Visszaadja a szót, illetve feladatok esetén hogy volt-e egyezés"""
        matching = False
        image = keras_ocr.tools.read(preprocessed_image)
        predictions = self.__pipeline.recognize([image])[0]
        texts = [text for text, _ in predictions]
        
        if isinstance(texts, list):
            if len(texts) > 1:
                corrected_texts_keras = None
            else:
                if texts == []:
                    return [None, None] 
                texts = texts[0]
                if texts.isdigit():     
                    corrected_texts_keras = texts
                else:           
                    if answer is not None and texts == answer:
                        matching = True
                    corrected_texts_keras= texts
        else:
            if texts.isdigit():     
                corrected_texts_keras = texts
            else:
                if answer is not None and texts == answer:
                        matching = True           
                corrected_texts_keras=texts
                
        return corrected_texts_keras, matching

    def __get_tesseracht_output(self,preprocessed_image, answer = None):
        """ A tesseract-ocr-el törénő képfelismerésért felelős függvény.
        Visszaadja a szót, illetve feladatok esetén hogy volt-e egyezés"""
        matching = False
        tesseract_output = pytesseract.image_to_string(preprocessed_image, config=self.__tesseract_config).split()
        corrected_texts_tesseracht = None
        
        if tesseract_output:
            texts = [text.lower() for text in tesseract_output]
            if texts and len(texts) == 1:
                texts = texts[0]
                if ' ' in texts or '\n' in texts: 
                    corrected_texts_tesseracht = None
                else:
                    if texts.isdigit():
                        if answer is not None and texts == answer:
                            matching = True
                        corrected_texts_tesseracht = texts
                    else:
                        if answer is not None and texts == answer:
                            matching = True
                        corrected_texts_tesseracht = texts
            else:
                corrected_texts_tesseracht = None
                
        return corrected_texts_tesseracht, matching

    def __check_word(self, word):
        """ Egy felismert szóhoz ajánlatot készítő függvény. A szótárból megkeresi a leghasonlóbb szavakat."""
        word = unidecode(word).lower()
        best_match = process.extract(word, self.__dictionary, limit=2)        
        return best_match
    
    def __preprocess_image(self, image_path):
        """ Segédfüggvény, a képek hatékony előfeldolgozásáért felel."""
        img = cv2.imread(image_path[0], cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Nem található a fájl a helyen: {image_path}")
        if img.shape[2] == 4:
            color, alpha = img[..., :3], img[..., 3]
            color[alpha == 0] = [255, 255, 255]
            img = color
        else:
            raise ValueError("A Kép üres!")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        preprocessed_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
        return preprocessed_image
    
    def extract_first_two_strings(self,tuples_list):
        """ Segédfüggvény, a két legrelevánsabb ajánlat visszaadása (amennyiben van 2). """
        if tuples_list is None:
            return []
        if len (tuples_list) == 0:
            return [None, None]
        if len(tuples_list) == 1:
            return tuples_list[0][0]
        else:
            return [tuples_list[0][0], tuples_list[1][0]]
        
    
