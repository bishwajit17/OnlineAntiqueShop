import re

def User_Name(string):
    if not re.fullmatch(re.compile(r'([A-Za-z ]){3,}'), string):
        #print("Name doesn't match")
        return False
    else:
        return True

def Name_LastName(string):
    #if not re.match(re.compile(r'[A-Za-z]{2,25}( [A-Za-z]{2,25})?'), string):
    if not re.fullmatch(re.compile(r'^(([A-Za-z])+( [A-Za-z]{1,})+)+'), string):    
        #print("Name doesn't match")
        return False
    else:
        return True
        #print("Matches")
def Email(string):
    if not re.fullmatch(re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'), string):
        print("Doesnt Match")
        return False
    else:
        return True

def PhoneNum(string):
    if not re.fullmatch(re.compile(r"^(\+)?([\d]{6,})"), string):
        print("Doesnt Match")
        return False
    else:
        return True
    

def Password(string):
    if not re.fullmatch(re.compile(r'[A-Za-z0-9@#$%^&+=]{8,}'),string):
        return False
    else:
        return True
