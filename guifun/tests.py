




def test1_entry(somearg:int, anotherarg:str):
    """
    This is some test start
    """
    pass

def test2_entry():
    pass

def test3_entry():
    pass

class SomeClass:
    "This is a doc string"
    def __init__(somevar):
        pass

    def __call__(bleh, bleh2):
        """
        Here is another
        """
        pass

exported_tests = {
    'Example test 1' : test1_entry,
    'Example test 2' : test2_entry,
    'Example test 3' : test3_entry,
    'Bleh' : SomeClass(),
}