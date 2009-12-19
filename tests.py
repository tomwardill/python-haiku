
import unittest
from haiku_checker import find_haiku

class TestFindHaiku(unittest.TestCase):
    
    def testsinglehaiku(self):
        result = find_haiku('As the wind does blow Across the trees, I see the Buds blooming in May')
        self.assertEqual(len(result), 1)
    
    def testarbitarysentence(self):
        result = find_haiku("Hacked his way through his first gig in 4 years, hopefully not my last. 'survival' is the main description of my attemts to play. Eb's suck.")
        self.assertEqual(len(result), 59)
        
    def testnohaiku(self):
        result = find_haiku("testing")
        self.assertEqual(len(result), 0)