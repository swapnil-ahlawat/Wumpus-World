#!/usr/bin/env python3
from Agent import * # See the Agent.py file
import copy
numberOfCalls=0

class KnowledgeBase:
    #clause[i]=-1 represents the presence of negative literal represented by i
    #clause[i]=1 represents the presence of positive literal represented by i
    #values 0 to 15 represents W(1,1) to W(4,4)
    #values 16 to 31 represents S(1,1) to S(4,4)
    #values 33 to 47 represents P(1,1) to P(4,4)
    #values 48 to 63 represents B(1,1) to B(4,4)
    def __init__(self):
        self.clauses= []

        #clauses for atleast 1 Wumpus and 1 Pit
        atleast1Wumpus= {}
        atleast1Pit = {}
        for i in range (16):
            atleast1Wumpus[i]=1
            atleast1Pit[i+32]=1
        self.clauses.append(atleast1Wumpus)
        self.clauses.append(atleast1Pit)

        #clauses for atmost 1 Wumpus and 1 Pit
        for i in range(16):
            for j in range(i+1, 16):
                atmost1Wumpus={}
                atmost1Pit={}
                atmost1Wumpus[i]=-1
                atmost1Wumpus[j]=-1
                atmost1Pit[i+32]=-1
                atmost1Pit[j+32]=-1
                self.clauses.append(atmost1Wumpus)
                self.clauses.append(atmost1Pit)

        #Stench-Wumpus bijection clauses
        for i in range(16):
            stenchWumpusClause={}
            stenchWumpusClause[i+16]=-1
            if (i+4)//4 < 4:
                stenchWumpusClause[i+4]=1
                stenchClause={}
                stenchClause[i+16]=1
                stenchClause[i+4]=-1
                self.clauses.append(stenchClause)
            if(i-4)//4 >= 0:
                stenchWumpusClause[i-4]=1
                stenchClause={}
                stenchClause[i+16]=1
                stenchClause[i-4]=-1
                self.clauses.append(stenchClause)
            if i//4 == (i+1)//4:
                stenchWumpusClause[i+1]=1
                stenchClause={}
                stenchClause[i+16]=1
                stenchClause[i+1]=-1
                self.clauses.append(stenchClause)
            if i//4 == (i-1)//4:
                stenchWumpusClause[i-1]=1
                stenchClause={}
                stenchClause[i+16]=1
                stenchClause[i-1]=-1
                self.clauses.append(stenchClause)
            self.clauses.append(stenchWumpusClause)
        
        #Breeze-Pit Bijection Clauses
        for i in range(16):
            breezePitClause={}
            breezePitClause[i+48]=-1
            if(i+4)//4 < 4:
                breezePitClause[i+4+32]=1
                pitClause={}
                pitClause[i+48]=1
                pitClause[i+4+32]=-1
                self.clauses.append(pitClause)
            if(i-4)//4 >= 0:
                breezePitClause[i-4+32]=1
                pitClause={}
                pitClause[i+48]=1
                pitClause[i-4+32]=-1
                self.clauses.append(pitClause)
            if i//4 == (i+1)//4:
                breezePitClause[i+1+32]=1
                pitClause={}
                pitClause[i+48]=1
                pitClause[i+1+32]=-1
                self.clauses.append(pitClause)
            if i//4 == (i-1)//4:
                breezePitClause[i-1+32]=1
                pitClause={}
                pitClause[i+48]=1
                pitClause[i-1+32]=-1
                self.clauses.append(pitClause)
            self.clauses.append(breezePitClause)

        #No wumpus and pit at [1, 1]
        noWumpusStart={0:-1}
        noPitStart={32:-1}
        self.clauses.append(noWumpusStart)
        self.clauses.append(noPitStart)

    def AddClause(self, clause): #adding a clause to knowledge base
        self.clauses.append(clause)
    
    def getclauses(self): #return Wumpus clauses
        return copy.deepcopy(self.clauses)
    

def FindPureSymbol(clauses, symbols):
    for symbol in symbols:
        positive=0
        negative=0
        for clause in clauses:
            if symbol in clause:
                if clause[symbol]==1:
                    positive= positive+1
                else:
                    negative= negative+1
        if negative==0:
            return symbol, 1
        elif positive==0:
            return symbol, -1
    return -1, 0

def FindUnitClause(clauses):
    for clause in clauses:
        if len(clause)==1:
            for symbol in clause:
                return symbol, clause[symbol]
    return -1, 0

def selectSymbol(clauses, symbols):
    count={}
    positive={}
    negative={}
    for clause in clauses:
        for literal in clause:
            if literal not in count:
                count[literal]=0
                positive[literal]=0
                negative[literal]=0

            count[literal]= count[literal]+1
            if clause[literal]==1:
                positive[literal]=positive[literal]+1
            else:
                negative[literal]=negative[literal]+1
    
    maxLiteral= list(symbols.keys())[0]
    maxCount=0
    for literal in count:
        if count[literal]>maxCount:
            maxLiteral= literal
            maxCount= count[literal]

    if positive[maxLiteral]>negative[maxLiteral]:
        return maxLiteral, 1
    return maxLiteral, -1

def DPLL(clauses, symbols, model):
    global numberOfCalls
    numberOfCalls= numberOfCalls+1
    removeClauses=[]
    for clause in clauses:
        valueUnknown=True
        deleteLiterals=[]
        for literal in clause.keys():
            if literal in model.keys():
                if model[literal]==clause[literal]: #clause is true
                    removeClauses.append(clause)
                    valueUnknown=False
                    break
                else:
                    deleteLiterals.append(literal)
        
        for literal in deleteLiterals:
            del clause[literal]
        if valueUnknown==True and not bool(clause): #clause is false
            return False

    clauses= [ x for x in clauses if x not in removeClauses]

    if len(clauses)==0: #all clauses are true
        return True

    pureSymbol, value = FindPureSymbol(clauses, symbols)
    if value!=0:
        del symbols[pureSymbol]
        model[pureSymbol]=value
        return DPLL(clauses, symbols, model)
    
    unitSymbol, value = FindUnitClause(clauses)
    if value!=0:
        del symbols[unitSymbol]
        model[unitSymbol]=value
        return DPLL(clauses, symbols, model)

    symbol, value= selectSymbol(clauses, symbols)
    del symbols[symbol]
    model[symbol]= value

    if DPLL(copy.deepcopy(clauses), copy.deepcopy(symbols), copy.deepcopy(model)):
        return True
    
    model[symbol]= -value
    return DPLL(clauses, symbols, model)


def DPLLSatisfiable(clauses):
    symbols={}
    for clause in clauses:
        for literal in clause:
            symbols[literal]=True
    
    model={}
    return DPLL(clauses, symbols, model)

def MoveToUnvisited(ag, visited, goalLoc, dfsVisited): #dfs to new safe room
    curPos=ag.FindCurrentLocation()
    curLoc= 4*(curPos[0]-1)+curPos[1]-1
    if(curLoc==goalLoc):
        return True
    dfsVisited[curLoc]=True
    
    if curPos[1]+1 <=4 and (visited[curLoc+1]==True or (curLoc+1)==goalLoc) and dfsVisited[curLoc+1]==False:
        ag.TakeAction('Up')
        roomReachable= MoveToUnvisited(ag, visited, goalLoc, dfsVisited)
        if roomReachable:
            return True
        ag.TakeAction('Down')

    if curPos[0]+1 <=4 and (visited[curLoc+4]==True or (curLoc+4)==goalLoc) and dfsVisited[curLoc+4]==False:
        ag.TakeAction('Right')
        roomReachable= MoveToUnvisited(ag, visited, goalLoc, dfsVisited)
        if roomReachable:
            return True
        ag.TakeAction('Left')

    if curPos[0]-1 >0 and (visited[curLoc-4]==True or (curLoc-4)==goalLoc) and dfsVisited[curLoc-4]==False:
        ag.TakeAction('Left')
        roomReachable= MoveToUnvisited(ag, visited, goalLoc, dfsVisited)
        if roomReachable:
            return True
        ag.TakeAction('Right')

    if curPos[1]-1 >0 and (visited[curLoc-1]==True or (curLoc-1)==goalLoc) and dfsVisited[curLoc-1]==False:
        ag.TakeAction('Down')
        roomReachable= MoveToUnvisited(ag, visited, goalLoc, dfsVisited)
        if roomReachable:
            return True
        ag.TakeAction('Up')

    return False

def ExitWumpusWorld(ag, kb):
    visited = [False for i in range(16)] #Rooms Visited till now 
    while(ag.FindCurrentLocation()!=[4, 4]):
        percept= ag.PerceiveCurrentLocation()
        curPos = ag.FindCurrentLocation()
        curLocIndex= 4*(curPos[0]-1)+ curPos[1]-1
        visited[curLocIndex]=True
        
        breezeClause={}
        stenchClause={}

        if percept[0]==True: #breeze
            breezeClause[curLocIndex+48]=1
        else:
            breezeClause[curLocIndex+48]=-1
        kb.AddClause(breezeClause) #presence/absence of breeze

        if percept[1]==True: #stench
            stenchClause[curLocIndex+16]=1
        else:
            stenchClause[curLocIndex+16]=-1
        kb.AddClause(stenchClause) #presence/absence of stench
            
        for newLoc in range(16):
            if visited[newLoc]==False:
                tempclauses= kb.getclauses()
                checkClause={newLoc:1, newLoc+32:1}  
                tempclauses.append(checkClause)
                if DPLLSatisfiable(tempclauses)==False:
                    #Room is safe
                    noWumpus={newLoc:-1}
                    noPit={newLoc+32:-1}
                    kb.AddClause(noWumpus)
                    kb.AddClause(noPit)
                    dfsVisited = [False for i in range(16)] 
                    roomReachable=MoveToUnvisited(ag, visited, newLoc, dfsVisited) #dfs to new safe Room
                    if roomReachable:
                        break

def main():
    ag = Agent()
    kb= KnowledgeBase()
    print('Start Location: {0}'.format(ag.FindCurrentLocation()))
    ExitWumpusWorld(ag, kb)
    print('{0} reached. Exiting the Wumpus World.'.format(ag.FindCurrentLocation()))
    print('Total number of times DPLL function is called: {0}'.format(numberOfCalls))


if __name__=='__main__':
    main()
