from enum import Enum

class ExerciseConfig(Enum):
    """
    A feladatok (teszt és házi feladat) megkülönböztetésére szolgáló enumerátor osztály.
    """
    TEST = 1
    HOMEWORK = 2
