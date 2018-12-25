#OTA equivalence

import sys
from ota import *
import copy

def get_regions(max_time_value):
    """
        Partition R into a finite collection of one-dimensional regions depending on the appearing max time value.
    """
    regions = []
    bound = 2*max_time_value+1
    for i in range(0, bound+1):
        if i % 2 == 0:
            temp = i//2
            r = Constraint('[' + str(temp) + ',' + str(temp) + ']')
            regions.append(r)
        else:
            temp = (i-1)//2
            if temp < max_time_value:
                r = Constraint('(' + str(temp) + ',' + str(temp+1) + ')')
                regions.append(r)
            else:
                r = Constraint('(' + str(temp) + ',' + '+' + ')')
                regions.append(r)
    return regions

def state_to_letter(state, max_time_value):
    region = None
    integer = int(state.v)
    fraction = state.get_fraction()
    if fraction > 0.0:
        if integer < max_time_value:
            region = Constraint('(' + str(integer) + ',' + str(integer+1) + ')')
        else:
            region = Constraint('(' + str(integer) + ',' + '+' + ')')
    else:
        region = Constraint('[' + str(integer) + ',' + str(integer) + ']')
    #return fraction, region
    return Letter(state.location, region)

class Letter(object):
    """
        The definition of letter. A letter is a pair (location, region).
        "location" for indicating the location
        "constraint" for the region
    """
    def __init__(self, location, constraint):
        self.location = location
        self.constraint = constraint
    
    def __eq__(self, letter):
        if self.location == letter.location and self.constraint == letter.constraint:
            return True
        else:
            return False

    def show(self):
        return self.location.get_flagname() + ',' + self.constraint.show()

class ABConfiguration(object):
    """
        The definition of A/B-configuration.
    """
    def __init__(self, Ac, Bstate):
        self.Aconfig = copy.deepcopy(Ac)
        self.Bstate = copy.deepcopy(Bstate)

    def configuration_to_letterword(self, max_time_value):
        """
            Transform an A/B-configuration to a letterword.
        """  
        allstates = [state for state in self.Aconfig]
        allstates.append(self.Bstate)
        allstates.sort(key=lambda x: x.get_fraction())
        temp_letterword = []
        current_fraction = -1
        for state in allstates:
            if state.get_fraction() == current_fraction:
                temp_letterword[len(temp_letterword)-1].append(state)
            else:
                new_letter = [state]
                temp_letterword.append(new_letter)
                current_fraction = state.get_fraction()
        letterword = [[state_to_letter(state, max_time_value) for state in letter] for letter in temp_letterword]   
        return letterword

def is_letters_subset(letters1, letters2):
    """
        To determin whether letters1 is a subset of letters2.
    
    if set(letters1).issubset(set(letters2)):
        return True
    else:
        return False
    """
    flag = True
    for letter in letters1:
        if letter in letters2:
            pass
        else:
            flag = False
            break
    return flag
    
def letterword_dominated(lw1, lw2):
    """
        To determin whether letterword lw1 is dominated by letterword lw2 (lw1 <= lw2)
    """
    index = 0
    flag = 0
    for letters1 in lw1:
        for i in range(index, len(lw2)):
            if is_letters_subset(letters1, lw2[i]):
                index = i+1
                flag = flag + 1
                break
            else:
                pass
    #print(flag)
    if flag == len(lw1):
        return True
    else:
        return False

def main():
    L1 = Location("1", True, False, 's')
    L2 = Location("2", False, False, 's')
    L3 = Location("3", False, True, 'q')
    print(L1.show())
    print(type(L1.get_name()))
    print(L2.show())
    print(L3.show())
    s1 = State(L1, 0.0)
    s2 = State(L1, 0.3)
    s3 = State(L1, 1.2)
    s4 = State(L2, 0.4)
    s5 = State(L2, 1.0)
    q1 = State(L3, 0.8)
    q2 = State(L3, 1.3)
    print(s1.show())
    print(s2.show())
    print("---------------A------------------")
    paras = sys.argv
    A,_ = buildOTA(paras[1])
    A.show()
    print("------------------Assist-----------------")
    AA = buildAssistantOTA(A, 's')
    AA.show()
    print("--------------max value---------------------")
    max_time_value = AA.max_time_value()
    print(max_time_value)
    print("--------------all regions---------------------")
    regions = get_regions(max_time_value)
    for r in regions:
        print(r.show())
    print("-------------------------------------")
    letter1 = state_to_letter(s1, max_time_value)
    letter2 = state_to_letter(s2, max_time_value)
    letter3 = state_to_letter(s3, max_time_value)
    letter5 = state_to_letter(s5, max_time_value)
    print(letter1.show())
    print(letter2.show())
    print("---------------AB-configuration------------------")
    Ac = [s1,s2,s3,s4,s5]
    Bstate = q2
    ABConfig = ABConfiguration(Ac, Bstate)
    letterword = ABConfig.configuration_to_letterword(max_time_value)
    for letters in letterword:
        print([l.show() for l in letters])
    print("-----------------------letters-----------------------")
    letters1 = letterword[0]
    letters2 = letterword[1]
    letters3 = [letter5, letter1]
    letters4 = [letter1]
    print(is_letters_subset(letters1, letters2))
    print(is_letters_subset(letters3, letters1))
    print(is_letters_subset(letters4, letters1))
    print("----------------------dominated----------------------")
    Ac2 = [s1,s2,s4]
    ABConfig2 = ABConfiguration(Ac2, Bstate)
    letterword2 = ABConfig2.configuration_to_letterword(max_time_value)
    for letters in letterword2:
        print([l.show() for l in letters])
    print(letterword_dominated(letterword2,letterword))

if __name__=='__main__':
	main()
