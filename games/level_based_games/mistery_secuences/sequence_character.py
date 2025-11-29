from abc import ABC, abstractmethod
from enum import Enum, auto



class SequenceCharacter(ABC):
    def __init__(self,):
        pass
    

    @abstractmethod
    def check_sequence(self, sequence):
        """
        Checks if a sequence is valid based on the rules defined by the character.
        returns True if the sequence is valid, False otherwise.
        """
        pass


class Letter(SequenceCharacter):
    def __init__(self, position):
        self.position = position
    pass

class LetterA(Letter):
    def check_sequence(self, sequence):
        for i in range(0, self.position + 1):
            if sequence[i] == 1:
                return False
        return True
    
class LetterB(Letter):
    def check_sequence(self, sequence):
        for i in range(self.position, len(sequence)):
            if sequence[i] == 1:
                return False
        return True
            
class LetterX(Letter):
    def check_sequence(self, sequence):
        return sequence[self.position] != 1