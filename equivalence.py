#OTA equivalence

import sys
from ota import *
import copy
from queue import Queue

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
        if isinstance(constraint, str):
            constraint = Constraint(constraint)
        self.constraint = constraint
    
    def __eq__(self, letter):
        if self.location == letter.location and self.constraint == letter.constraint:
            return True
        else:
            return False
            
    def __hash__(self):
        return hash(("LETTER", self.location, self.constraint))
    
    def to_state(self, i):
        """
            Transform a letter to a state.
        """
        location = self.location
        v = 0
        if self.constraint.isPoint():
            v = self.constraint.min_value+'.0'
        else:
            v = self.constraint.min_value + '.' + str(i+1)
        return State(location, v)

    def show(self):
        return self.location.get_flagname() + ',' + self.constraint.show()
        
    def __str__(self):
        return self.show()
        
    def __repr__(self):
        return self.show()

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
                temp_letterword[len(temp_letterword)-1].add(state_to_letter(state, max_time_value))
            else:
                new_letters = set()
                new_letters.add(state_to_letter(state, max_time_value))
                temp_letterword.append(new_letters)
                current_fraction = state.get_fraction() 
        return temp_letterword
    
def letterword_dominated(lw1, lw2):
    """
        To determin whether letterword lw1 is dominated by letterword lw2 (lw1 <= lw2)
    """
    index = 0
    flag = 0
    for letters1 in lw1:
        for i in range(index, len(lw2)):
            if letters1.issubset(lw2[i]):
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

def immediate_letter_asucc(letter, action, ota):
    """
    """
    location_name = letter.location.name
    region = letter.constraint
    succ_location = None
    for tran in ota.trans:
        if tran.source == location_name and action == tran.label and region.issubset(tran.constraints[0]):
            succ_location_name = tran.target
            succ_location = ota.findlocationbyname(succ_location_name)
            if tran.reset == True:
                region = Constraint("[0,0]")
            if succ_location is not None:
                return Letter(succ_location, region)
    return None

def immediate_asucc(letterword, A, B):
    """ Perform the immediate 'a' action.
        in case of L(B) is a subset of L(A).
    """
    results = []
    if len(letterword) == 1:
        letter1, letter2 = list(letterword[0])
        for action in B.sigma:
            B_letter = None
            A_letter = None
            w = None
            if letter1.location.flag == A.locations[0].flag:
                B_letter = immediate_letter_asucc(letter2, action, B)
                A_letter = immediate_letter_asucc(letter1, action, A)
            else:
                B_letter = immediate_letter_asucc(letter1, action, B)
                A_letter = immediate_letter_asucc(letter2, action, A)
            if B_letter is not None and A_letter is not None:
                B_ispoint = B_letter.constraint.isPoint()
                A_ispoint = A_letter.constraint.isPoint()
                if A_ispoint == True and B_ispoint == True:
                    w = [{A_letter, B_letter}]
                elif A_ispoint == True and B_ispoint == False:
                    w = [{A_letter}, {B_letter}]
                elif A_ispoint == False and B_ispoint == True:
                    w = [{B_letter}, {A_letter}]
                else:
                    w = [{A_letter, B_letter}]
                if w not in results:
                    results.append(w)
    elif len(letterword) == 2:
        letter1, letter2 = list(letterword[0])[0], list(letterword[1])[0]
        for action in B.sigma:
            B_letter = None
            A_letter = None
            w = None
            if letter1.location.flag == A.locations[0].flag:
                B_letter = immediate_letter_asucc(letter2, action, B)
                A_letter = immediate_letter_asucc(letter1, action, A)
                if B_letter is not None and A_letter is not None:
                    B_ispoint = B_letter.constraint.isPoint()
                    A_ispoint = A_letter.constraint.isPoint()
                    if A_ispoint == True and B_ispoint == True:
                        w = [{A_letter, B_letter}]
                    elif A_ispoint == True and B_ispoint == False:
                        w = [{A_letter}, {B_letter}]
                    elif A_ispoint == False and B_ispoint == True:
                        w = [{B_letter}, {A_letter}]
                    else:
                        w = [{A_letter}, {B_letter}]
                    if w not in results:
                        results.append(w)
            else:
                B_letter = immediate_letter_asucc(letter1, action, B)
                A_letter = immediate_letter_asucc(letter2, action, A)
                if B_letter is not None and A_letter is not None:
                    B_ispoint = B_letter.constraint.isPoint()
                    A_ispoint = A_letter.constraint.isPoint()
                    if A_ispoint == True and B_ispoint == True:
                        w = [{A_letter, B_letter}]
                    elif A_ispoint == True and B_ispoint == False:
                        w = [{A_letter}, {B_letter}]
                    elif A_ispoint == False and B_ispoint == True:
                        w = [{B_letter}, {A_letter}]
                    else:
                        w = [{B_letter}, {A_letter}]
                    if w not in results:
                        results.append(w)
    else:
        raise NotImplementedError()
    return results

def letterword_to_configuration(letterword, flag):
    """
        Transform a letterword to A/B-configuration.
    """
    lwlen = len(letterword)
    G = []
    Bstate = None
    for letters, i in zip(letterword, range(lwlen)):
        for letter in list(letters):
            state = letter.to_state(i)
            if state.location.flag == flag:
                G.append(state)
            else:
                Bstate = state
    return ABConfiguration(G, Bstate)

def next_region(region, max_time_value):
    """Returns r_0^1 for r_0, r_1 for r_0^1, etc.
    """
    if region.isPoint():
        if int(region.max_value) == max_time_value:
            return Constraint('(' + region.max_value + ',' + '+' + ')')
        else:
            return Constraint('(' + region.max_value + ',' + str(int(region.max_value) + 1) + ')')
    else:
        if region.max_value == '+':
            return Constraint('(' + region.min_value + ',' + '+' + ')')
        else:
            return Constraint('[' + region.max_value + ',' + region.max_value + ']')

def compute_wsucc(letterword, max_time_value, A, B):
    """Compute the Succ of letterword.
    """
    # First compute all possible time delay
    results = []
    last_region = Constraint('(' + str(max_time_value) + ',' + '+' + ')')
    if len(letterword) == 1:
        result = letterword[0]
        while any(letter.constraint != last_region for letter in result):
            results.append([result])
            new_result = set()
            for letter in result:
                new_letter = Letter(letter.location, next_region(letter.constraint, max_time_value))
                new_result.add(new_letter)
            result = new_result
        if [result] not in results:
            results.append([result])
    elif len(letterword) == 2:
        if len(letterword[0]) != 1 and len(letterword[1]) != 1:
            raise NotImplementedError()
        result = letterword
        while list(result[0])[0].constraint != last_region or list(result[1])[0].constraint != last_region:
            results.append(result)
            new_result = []
            l1, l2 = list(result[0])[0], list(result[1])[0]
            if l1.constraint.isPoint():
                new_result.append({Letter(l1.location, next_region(l1.constraint, max_time_value))})
                new_result.append({l2})
            else:
                new_result.append({Letter(l2.location, next_region(l2.constraint, max_time_value))})
                new_result.append({l1})
            result = new_result
        if result not in results:
            results.append(result)
            new_result = [result[1], result[0]]
            if new_result not in results:
                results.append(new_result)
    else:
        raise NotImplementedError()

    # Next, perform the immediate 'a' transition
    next = []
    for letterword in results:
        next_ws = immediate_asucc(letterword, A, B)
        for next_w in next_ws:
            if next_w not in next:
                next.append(next_w)
    return results, next

def is_bad_letterword(letterword, A, B):
    """Determin whether a letterword is bad.
       in case of L(B) is a subset of L(A)
    """
    letter1 = None
    letter2 = None
    if len(letterword) == 1:
        letter1, letter2 = list(letterword[0])
    elif len(letterword) == 2:
        letter1, letter2 = list(letterword[0])[0], list(letterword[1])[0]
    else:
        raise NotImplementedError()
    location1 = letter1.location
    location2 = letter2.location
    if location1.flag == B.locations[0].flag:
        if location1.name in B.accept_names and location2.name not in A.accept_names:
            return True
        else:
            return False
    else:
        if location2.name in B.accept_names and location1.name not in A.accept_names:
            return True
        else:
            return False

def explored_undominated(explored, w):
    if len(explored) == 0:
        return False
    for v in explored:
        if letterword_dominated(v, w):
            return False
    return True

def ota_inclusion(max_time_value, A, B):
    """Determin whether L(B) is a subset of L(A).
    """
    A_init_name = A.initstate_name
    B_init_name = B.initstate_name
    L1 = A.findlocationbyname(A_init_name)
    Q1 = B.findlocationbyname(B_init_name)
    w0 = [{Letter(L1, "[0,0]"), Letter(Q1, "[0,0]")}]
    to_explore = []
    to_explore.append(w0)
    explored = []
    while True:
        if len(to_explore) == 0:
            return True
        w = to_explore[0]
        del to_explore[0]
        if is_bad_letterword(w, A, B):
            return False
        while explored_undominated(explored, w):
            if len(to_explore) == 0:
                return True
            w = to_explore[0]
            del to_explore[0]
            if is_bad_letterword(w, A, B):
                return False
        wsucc, next = compute_wsucc(w, max_time_value, A, B)
        for nw in next:
            if nw not in to_explore:
                to_explore.append(nw)
        if w not in explored:
            explored.append(w)
    #return w0

def main():
    #print("---------------A------------------")
    paras = sys.argv
    #print(paras[1])
    A,_ = buildOTA(paras[1], 's')
    A.show()
    D, _ = buildOTA(paras[2], 'q')
    D.show()
    print("-----------------------------------------")
    ota_inclusion(4, D, A)
    """
    print("------------------Assist-----------------")
    AA = buildAssistantOTA(A, 's')
    AA.show()
    print("--------------max value---------------------")
    max_time_value = AA.max_time_value()
    print("--------------all regions---------------------")
    regions = get_regions(max_time_value)
    for r in regions:
        print(r.show())
    print("-------------------------------------")
    letter1 = state_to_letter(s1, max_time_value)
    letter2 = state_to_letter(s2, max_time_value)
    letter3 = state_to_letter(s3, max_time_value)
    letter5 = state_to_letter(s5, max_time_value)
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
    print("----------------------dominated----------------------")
    Ac2 = [s1,s2,s4]
    ABConfig2 = ABConfiguration(Ac2, Bstate)
    letterword2 = ABConfig2.configuration_to_letterword(max_time_value)
    #for letters in letterword2:
        #print([l.show() for l in letters])
    print(letterword2)
    print(letterword_dominated(letterword2,letterword))
    print("----------------------letterword_to_configuration-----------------")
    ABConfig3 = letterword_to_configuration(letterword, 's')
    print([state.show() for state in ABConfig3.Aconfig])
    print(ABConfig3.Bstate.show())
    print("----------------next_region---------------------------")
    """
    """
    print("----------------compute_wsucc----------------------")
    w = [[Letter(L1, regions[0]), Letter(L2, regions[2])]]
    wsucc = compute_wsucc(w, max_time_value)
    for letterword in wsucc:
        print(letterword)
    print()
    w = [[Letter(L1, regions[5]), Letter(L2, regions[9])]]
    wsucc = compute_wsucc(w, max_time_value)
    print(wsucc)
    print()
    w = [[Letter(L1, regions[0])], [Letter(L2, regions[1])]]
    wsucc = compute_wsucc(w, max_time_value)
    for letterword in wsucc:
        print(letterword)
    print()
    w = [[Letter(L1, regions[1])], [Letter(L3, regions[1])]]
    wsucc = compute_wsucc(w, max_time_value)
    for letterword in wsucc:
        print(letterword)
    """
    #print("--------------------B----------------------")
    #B,_ = buildOTA(paras[2], 'q')
    #B.show()

if __name__ == '__main__':
	main()
