# TO MAKE WORD LATTICE FOR EQUIVALENCE CONSTRAINT MODEL

from copy import deepcopy

# from .data_structure_definitions import *
from .data_structure_definitions import *
from .lattice_operations import *


def populateLexSubFlags(node, lexSubLabels):

    for child in node.children:
        populateLexSubFlags(child, lexSubLabels)

    if node.label in lexSubLabels or (len(node.children) > 0 and node.children[-1].lexSubFlag == 1):
        node.lexSubFlag = 1
        node.counterpart.lexSubFlag = 1


def populateMethodLabels(node, grammar):

    if (node.ruleNum != -1 and not grammar[node.ruleNum].languageAgnostic) or node.parent.methodLabel == 1:
        node.methodLabel = 1
        node.counterpart.methodLabel = 1

    for child in node.children:
        populateMethodLabels(child, grammar)


def checkForEquivalence(grammar, ruleNum, index):
    for i in range(len(grammar[ruleNum].rhs)):
        if grammar[ruleNum].rhs[i].engRank >= index and grammar[ruleNum].rhs[i].hinRank < index or \
                grammar[ruleNum].rhs[i].engRank < index and grammar[ruleNum].rhs[i].hinRank >= index:
            return 0
    return 1


def makeCompressedEqLattice(node, grammar):

    global dependencyList
    # print node.label

    d = dfa()
    if node.token != 'XXXXX':
        a = d.addState()
        b = d.addState()
        d.addTransition(a, node.token + "_e", b,
                        [("push", node.label + '_e'), ("match"), ("pop")])
        d.addTransition(a, node.counterpart.token + "_h", b,
                        [("push", node.counterpart.label + '_h'), ("match"), ("pop")])
        node.doof = d
        '''node.doof.printGraphicDfa(None)
        input()'''
        return

    # for child in node.children:
        # makeCompressedEqLattice(child, grammar)

    prevEP = 0
    nextEP = 0
    while nextEP < len(node.children):
        prevEP = nextEP
        nextEP = nextEP + 1
        while not checkForEquivalence(grammar, node.ruleNum, nextEP):
            nextEP = nextEP + 1
        # print prevEP, nextEP
        engDfa = dfa()
        hinDfa = dfa()
        if nextEP - prevEP == 1:
            engDfa = node.children[prevEP].doof
        else:
            for index in range(prevEP, nextEP):
                engDfa.mergeDfaSeries(node.children[index].doof)
                hinDfa.mergeDfaSeries(
                    node.counterpart.children[index].counterpart.doof)
            engDfa.mergeDfaParallel(hinDfa)

        d.mergeDfaSeries(engDfa)

    node.doof = d
    '''node.doof.printGraphicDfa(None)
    input()'''
    return


def insertSensiblyEng(bigDfa, smallDfa):
    if bigDfa.engEnd == -1 and bigDfa.mixEnd == -1 and bigDfa.hinEnd == -1:
        bigDfa.mergeDfa(smallDfa)
        bigDfa.engEnd = smallDfa.engEnd
        bigDfa.hinEnd = smallDfa.hinEnd
        bigDfa.mixEnd = smallDfa.mixEnd
        return

    if bigDfa.mixEnd == -1:
        if bigDfa.hinEnd == -1:
            if smallDfa.mixEnd == -1:
                if smallDfa.hinEnd == -1:
                    # 13
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                else:
                    # 5
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mixEnd = smallDfa.hinEnd + nextStart
                    bigDfa.hinEnd = -1
            else:
                if smallDfa.hinEnd == -1:
                    # 9
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mixEnd = smallDfa.mixEnd + nextStart
                else:
                    # 1
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    bigDfa.mixEnd = smallDfa.mixEnd + nextStart
                    bigDfa.hinEnd = -1
        else:
            if smallDfa.mixEnd == -1:
                if smallDfa.hinEnd == -1:
                    # 15
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.mixEnd = smallDfa.engEnd + nextStart

                    bigDfa.hinEnd = -1
                else:
                    # 7
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerOne = smallDfa.hinEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerTwo = smallDfa.engEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne
            else:
                if smallDfa.hinEnd == -1:
                    # 11
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.engEnd + nextStart, [smallDfa.mixEnd + nextStart])
                    hangerTwo = smallDfa.engEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

                    bigDfa.hinEnd = -1

                else:
                    # 3
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerTwo = smallDfa.mixEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

    else:
        if bigDfa.hinEnd == -1:
            if smallDfa.mixEnd == -1:
                if smallDfa.hinEnd == -1:
                    # 14
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mixEnd = smallDfa.engEnd + nextStart
                else:
                    # 6
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerOne = smallDfa.hinEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.engEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerTwo = smallDfa.engEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

            else:
                if smallDfa.hinEnd == -1:
                    # 10
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.engEnd + nextStart, [smallDfa.mixEnd + nextStart])
                    hangerTwo = smallDfa.engEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

                else:
                    # 2
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.engEnd + nextStart, [smallDfa.mixEnd + nextStart, smallDfa.hinEnd + nextStart])
                    hangerTwo = smallDfa.engEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

        else:
            if smallDfa.mixEnd == -1:
                if smallDfa.hinEnd == -1:
                    # 16
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart

                    bigDfa.mergeStates(bigDfa.mixEnd, [bigDfa.hinEnd])
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mixEnd = smallDfa.engEnd + nextStart

                    bigDfa.hinEnd = -1
                else:
                    # 8
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerOne = smallDfa.hinEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerTwo = smallDfa.engEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.engEnd + nextStart, [smallDfa.hinEnd + nextStart, smallDfa.hinEnd])

                    bigDfa.mergeStates(smallDfa.engEnd +
                                       nextStart, [hangerOne, hangerTwo])
                    bigDfa.mixEnd = smallDfa.engEnd + newStart

            else:
                if smallDfa.hinEnd == -1:
                    # 12
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerTwo = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])

                    bigDfa.mergeStates(smallDfa.mixEnd +
                                       nextStart, [hangerOne, hangerTwo])
                    bigDfa.mixEnd = smallDfa.mixEnd + newStart

                    bigDfa.hinEnd = -1

                else:
                    # 4
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerTwo = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart, smallDfa.hinENd + nextStart])

                    bigDfa.mergeStates(smallDfa.mixEnd +
                                       nextStart, [hangerOne, hangerTwo])
                    bigDfa.mixEnd = smallDfa.mixEnd + newStart


def insertSensiblyHin(bigDfa, smallDfa):
    if bigDfa.hinEnd == -1 and bigDfa.mixEnd == -1 and bigDfa.engEnd == -1:
        # print(smallDfa.states)
        bigDfa.mergeDfa(smallDfa)
        bigDfa.hinEnd = smallDfa.hinEnd
        bigDfa.engEnd = smallDfa.engEnd
        bigDfa.mixEnd = smallDfa.mixEnd
        return

    if bigDfa.mixEnd == -1:
        if bigDfa.engEnd == -1:
            if smallDfa.mixEnd == -1:
                if smallDfa.engEnd == -1:
                    # 13
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                else:
                    # 5
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mixEnd = smallDfa.engEnd + nextStart
                    bigDfa.engEnd = -1
            else:
                if smallDfa.engEnd == -1:
                    # 9
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mixEnd = smallDfa.mixEnd + nextStart
                else:
                    # 1
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    bigDfa.mixEnd = smallDfa.mixEnd + nextStart
                    bigDfa.engEnd = -1
        else:
            if smallDfa.mixEnd == -1:
                if smallDfa.engEnd == -1:
                    # 15
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.mixEnd = smallDfa.hinEnd + nextStart

                    bigDfa.engEnd = -1
                else:
                    # 7
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerOne = smallDfa.engEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerTwo = smallDfa.hinEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne
            else:
                if smallDfa.engEnd == -1:
                    # 11
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.hinEnd + nextStart, [smallDfa.mixEnd + nextStart])
                    hangerTwo = smallDfa.hinEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

                    bigDfa.engEnd = -1

                else:
                    # 3
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerTwo = smallDfa.mixEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

    else:
        if bigDfa.engEnd == -1:
            if smallDfa.mixEnd == -1:
                if smallDfa.engEnd == -1:
                    # 14
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mixEnd = smallDfa.hinEnd + nextStart
                else:
                    # 6
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerOne = smallDfa.engEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.hinEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerTwo = smallDfa.hinEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

            else:
                if smallDfa.engEnd == -1:
                    # 10
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.hinEnd + nextStart, [smallDfa.mixEnd + nextStart])
                    hangerTwo = smallDfa.hinEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

                else:
                    # 2
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.hinEnd + nextStart, [smallDfa.mixEnd + nextStart, smallDfa.engEnd + nextStart])
                    hangerTwo = smallDfa.hinEnd + nextStart

                    bigDfa.mergeStates(hangerOne, [hangerTwo])
                    bigDfa.mixEnd = hangerOne

        else:
            if smallDfa.mixEnd == -1:
                if smallDfa.engEnd == -1:
                    # 16
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart

                    bigDfa.mergeStates(bigDfa.mixEnd, [bigDfa.engEnd])
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mixEnd = smallDfa.hinEnd + nextStart

                    bigDfa.engEnd = -1
                else:
                    # 8
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerOne = smallDfa.engEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    hangerTwo = smallDfa.hinEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.hinEnd + nextStart, [smallDfa.engEnd + nextStart, smallDfa.engEnd])

                    bigDfa.mergeStates(smallDfa.hinEnd +
                                       nextStart, [hangerOne, hangerTwo])
                    bigDfa.mixEnd = smallDfa.hinEnd + newStart

            else:
                if smallDfa.engEnd == -1:
                    # 12
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerTwo = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])

                    bigDfa.mergeStates(smallDfa.mixEnd +
                                       nextStart, [hangerOne, hangerTwo])
                    bigDfa.mixEnd = smallDfa.mixEnd + newStart

                    bigDfa.engEnd = -1

                else:
                    # 4
                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.hinEnd, [nextStart])
                    bigDfa.hinEnd = smallDfa.hinEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.engEnd + nextStart])
                    hangerOne = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.engEnd, [nextStart])
                    bigDfa.engEnd = smallDfa.engEnd + nextStart
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart])
                    hangerTwo = smallDfa.mixEnd + nextStart

                    nextStart = bigDfa.nextIndex
                    bigDfa.mergeDfa(smallDfa)
                    bigDfa.mergeStates(bigDfa.mixEnd, [nextStart])
                    bigDfa.mergeStates(
                        smallDfa.mixEnd + nextStart, [smallDfa.hinEnd + nextStart, smallDfa.engENd + nextStart])

                    bigDfa.mergeStates(smallDfa.mixEnd +
                                       nextStart, [hangerOne, hangerTwo])
                    bigDfa.mixEnd = smallDfa.mixEnd + newStart


def attachFinal(doof, engDfa):
    if doof.mixEnd == -1 and doof.engEnd == -1 and doof.hinEnd == -1:
        doof.mergeDfa(engDfa)
        doof.engEnd = engDfa.engEnd
        doof.hinEnd = engDfa.hinEnd
        doof.mixEnd = engDfa.mixEnd

    else:
        if doof.mixEnd == -1:
            if engDfa.mixEnd == -1:
                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.engEnd, [nextStart])
                doof.engEnd = engDfa.engEnd + nextStart
                hangerOne = engDfa.hinEnd + nextStart

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.hinEnd, [nextStart])
                doof.hinEnd = engDfa.hinEnd + nextStart
                hangerTwo = engDfa.engEnd + nextStart

                doof.mergeStates(hangerOne, [hangerTwo])
                doof.mixEnd = hangerOne

            else:
                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.engEnd, [nextStart])
                doof.engEnd = engDfa.engEnd + nextStart
                doof.mergeStates(engDfa.hinEnd + nextStart,
                                 [engDfa.mixEnd + nextStart])
                hangerOne = engDfa.hinEnd + nextStart

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.hinEnd, [nextStart])
                doof.hinEnd = engDfa.hinEnd + nextStart
                doof.mergeStates(engDfa.engEnd + nextStart,
                                 [engDfa.mixEnd + nextStart])
                hangerTwo = engDfa.engEnd + nextStart

                doof.mergeStates(hangerOne, [hangerTwo])
                doof.mixEnd = hangerOne

        else:
            if engDfa.mixEnd == -1:
                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.engEnd, [nextStart])
                doof.engEnd = engDfa.engEnd + nextStart
                hangerOne = engDfa.hinEnd + nextStart

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.hinEnd, [nextStart])
                doof.hinEnd = engDfa.hinEnd + nextStart
                hangerTwo = engDfa.engEnd + nextStart

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.mixEnd, [nextStart])
                doof.mergeStates(engDfa.hinEnd + nextStart,
                                 [engDfa.engEnd + nextStart])

                doof.mergeStates(engDfa.hinEnd + nextStart,
                                 [hangerOne, hangerTwo])
                doof.mixEnd = engDfa.hinEnd + nextStart

            else:

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.engEnd, [nextStart])
                doof.engEnd = engDfa.engEnd + nextStart
                doof.mergeStates(engDfa.hinEnd + nextStart,
                                 [engDfa.mixEnd + nextStart])
                hangerOne = engDfa.hinEnd + nextStart

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.hinEnd, [nextStart])
                doof.hinEnd = engDfa.hinEnd + nextStart
                doof.mergeStates(engDfa.engEnd + nextStart,
                                 [engDfa.mixEnd + nextStart])
                hangerTwo = engDfa.engEnd + nextStart

                nextStart = doof.nextIndex
                doof.mergeDfa(engDfa)
                doof.mergeStates(doof.mixEnd, [nextStart])
                doof.mergeStates(engDfa.hinEnd + nextStart,
                                 [engDfa.engEnd + nextStart])

                doof.mergeStates(engDfa.hinEnd + nextStart,
                                 [hangerOne, hangerTwo])
                doof.mixEnd = engDfa.hinEnd + nextStart


def makeBlownUpEqLattice(node, grammar):

    global dependencyList

    node.doof = dfa()
    if node.token != 'XXXXX':
        a = node.doof.addState()
        b = node.doof.addState()
        c = node.doof.addState()
        node.doof.addTransition(
            a, node.token+"_e", b, [('push', node.label + '_e'), ('match'), ('pop')])
        node.doof.addTransition(a, node.counterpart.token+"_h", c,
                                [('push', node.counterpart.label + '_h'), ('match'), ('pop')])
        if node.lexSubFlag == 1:
            node.doof.addTransition(a, node.counterpart.token+"_e", b,
                                    [('push', node.counterpart.label + '_h'), ('match'), ('pop')])
            node.doof.addTransition(
                a, node.token+"_h", c, [('push', node.label + '_e'), ('match'), ('pop')])
        node.doof.engEnd = b
        node.doof.hinEnd = c
        node.doof.mixEnd = -1
        return

    for child in node.children:
        makeBlownUpEqLattice(child, grammar)

    prevEP = 0
    nextEP = 0
    while nextEP < len(node.children):
        prevEP = nextEP
        nextEP = nextEP + 1
        # while (model == 'sankoff' and not checkForEquivalence(grammar, node.ruleNum, nextEP)) or \
        # (model == 'fhc' and ((not checkForEquivalence(grammar, node.ruleNum, nextEP)) or ( nextEP > 0 and \
        # nextEP < len(node.children) and \
        # ((node.children[nextEP-1].label, node.children[nextEP].label) in dependencyList)))): #uncomment for FHC
        while not checkForEquivalence(grammar, node.ruleNum, nextEP):
            nextEP = nextEP + 1

        engDfa = dfa()
        hinDfa = dfa()
        if nextEP - prevEP == 1:
            engDfa = node.children[prevEP].doof

        else:
            for index in range(prevEP, nextEP):
                if (index < len(node.children) and index < len(node.counterpart.children)):
                    # print(prevEP, nextEP, index)
                    # print([child.token for child in node.children])
                    # print(node.counterpart.token)
                    # print([child.token for child in node.counterpart.children])
                    temp1 = deepcopy(node.children[index].doof)
                    temp2 = deepcopy(
                        node.counterpart.children[index].counterpart.doof)

                    # if node.children[index].counterpart != node.counterpart.children[index]:

                    # if node.children[index].lexSubFlag == 0:
                    temp1.deleteState(temp1.hinEnd)
                    temp1.hinEnd = -1

                    # if node.counterpart.children[index].lexSubFlag == 0:
                    temp2.deleteState(temp2.engEnd)
                    temp2.engEnd = -1

                    insertSensiblyEng(engDfa, temp1)
                    insertSensiblyHin(hinDfa, temp2)

            # after making engDfa and hinDfa
            currStart = engDfa.initialStates[0]
            nextStart = engDfa.nextIndex
            engDfa.mergeDfa(hinDfa)
            engDfa.mergeStates(currStart, [nextStart])
            engDfa.hinEnd = hinDfa.hinEnd + nextStart

            if engDfa.mixEnd != -1:
                if hinDfa.mixEnd != -1:
                    engDfa.mergeStates(
                        engDfa.mixEnd, [hinDfa.mixEnd + nextStart])
            else:
                if hinDfa.mixEnd != -1:
                    engDfa.mixEnd = hinDfa.mixEnd + nextStart
                else:
                    engDfa.mixEnd = -1

        attachFinal(node.doof, engDfa)
    # input()
    process_node_parse(node, grammar)
    return


def makeEqLattice(node, grammar):

    if node.methodLabel == 1:
        makeBlownUpEqLattice(node, grammar)
        trimTrapStates(node.doof)
    else:
        for child in node.children:
            makeEqLattice(child, grammar)
            if child.methodLabel == 1:
                child.doof.mergeSpokes()
        makeCompressedEqLattice(node, grammar)
    '''node.doof.printGraphicDfa(None)
    input()'''


def wellformedIfMonolingual(string1, string2, engSentence, hinSentence):
    if string1[-1] != string2[-1]:
        return True

    lang = string1[-1]
    word1 = string1[:-2]
    word2 = string2[:-2]
    fragment = word1 + " " + word2

    if lang == 'e':
        if fragment in engSentence:
            return True
        return False
    else:
        if fragment in hinSentence:
            return True
        return False


def disallowIllformedMonolingualFragments(doof, engSentence, hinSentence):

    statesToDelete = []

    for s in doof.states:
        transIn = {k: v for k, v in doof.transitions.items() if v == s}
        transOut = {k: v for k, v in doof.transitions.items() if k[0] == s}
        if transIn == {}:
            continue
        if transOut == {}:
            continue

        key1 = transIn.keys()[0][1]
        inPartition1 = {k: v for k, v in transIn.items() if k[1] == key1}
        outPart1 = {k: v for k, v in transOut.items() if wellformedIfMonolingual(
            key1, k[1], engSentence, hinSentence)}

        inPartition2 = {k: v for k, v in transIn.items() if k[1] != key1}
        if inPartition2 != {}:
            key2 = inPartition2.keys()[0][1]
            outPart2 = {k: v for k, v in transOut.items() if wellformedIfMonolingual(
                key2, k[1], engSentence, hinSentence)}

        if inPartition1 == transIn:
            if outPart1 != transOut:
                for k, v in transOut.items():
                    if not wellformedIfMonolingual(key1, k[1], engSentence, hinSentence):
                        del doof.transitions[k]
            continue

        elif inPartition2 == transIn:
            if outPart2 != transOut:
                for k, v in transOut.items():
                    if not wellformedIfMonolingual(key2, k[1], engSentence, hinSentence):
                        del doof.transitions[k]
            continue

        elif outPart1 == outPart2 and outPart1 == transOut:
            continue

        else:
            a = doof.addState()
            for k, v in inPartition1.items():
                doof.transitions[k] = a
            outPart1 = {(a, k[1]): v for k, v in outPart1.items()}
            doof.transitions = dict(
                doof.transitions.items() + outPart1.items())

            b = doof.addState()
            for k, v in inPartition2.items():
                doof.transitions[k] = b
            outPart2 = {(b, k[1]): v for k, v in outPart2.items()}
            doof.transitions = dict(
                doof.transitions.items() + outPart2.items())

            statesToDelete.append(s)

    for s in statesToDelete:
        doof.deleteState(s)


def wellformedIfMonolingualGeneric(string1, string2, engSentence, hinSentence):

    word1 = string1[:-2]
    word2 = string2[:-2]
    tokens1 = engSentence.split(" ")
    tokens2 = hinSentence.split(" ")

    # print word1, word2

    if word1 in tokens1 and word2 in tokens1:
        for i in range(len(tokens1)-1):
            if tokens1[i] == word1 and tokens1[i+1] == word2:
                # print "true"
                return True
        # print "false"
        return False

    if word1 in tokens2 and word2 in tokens2:
        for j in range(len(tokens2)-1):
            if tokens2[j] == word1 and tokens2[j+1] == word2:
                # print "true"
                return True
        # print "false"
        return False

    return True

    # if word1 in engSentence and word2 in engSentence:
    # if fragment not in engSentence:
    # return False

    # if word1 in hinSentence and word2 in hinSentence:
    # if fragment not in hinSentence:
    # return False

    # return True


def disallowIllformedMonolingualFragmentsGeneric(doof, engSentence, hinSentence):

    # print engSentence, hinSentence

    statesToDelete = []

    for s in doof.states:
        transIn = {k: v for k, v in doof.transitions.items() if v == s}
        transOut = {k: v for k, v in doof.transitions.items() if k[0] == s}
        if transIn == {}:
            continue
        if transOut == {}:
            continue

        # print transIn, transOut

        newStates = []

        for key, val in transIn.items():
            myTransOut = {k: v for k, v in transOut.items(
            ) if wellformedIfMonolingualGeneric(key[1], k[1], engSentence, hinSentence)}
            # print key, val
            # print myTransOut

            if myTransOut == {}:
                del doof.transitions[key]
                del doof.transition_ops[key]
                continue

            if myTransOut == transOut:
                continue

            for thisNewState in newStates:
                if myTransOut == {k: v for k, v in doof.transitions.items() if k[0] == thisNewState}:
                    doof.transitions[key] = thisNewState
                    continue

            if doof.transitions[key] == s:
                a = doof.addState()
                doof.transitions[key] = a
                for k, v in myTransOut.items():
                    doof.transitions[(a, k[1])] = v
                    doof.transition_ops[(a, k[1])] = doof.transition_ops[k]
                if a in doof.finalStates:
                    doof.finalStates.remove(a)

        if {k: v for k, v in doof.transitions.items() if v == s} == 0:
            statesToDelete.append(s)

    for s in statesToDelete:
        doof.delete(s)

def process_node_parse(node, grammar):
    start_states = [0]
    end_states = node.doof.finalStates
    for k, v in node.doof.transitions.items():
        if k[0] in start_states:
            rule = grammar[node.ruleNum]
            if rule.languageAgnostic:
                node.doof.transition_ops[k].insert(0, ('push', node.label))
            else:
                first_op = node.doof.transition_ops[k][0]
                if type(first_op) == str:
                    print("something is wrong")
                    exit()
                else:
                    first_node = first_op[1]
                    if len(first_node) > 2:
                        if first_node[-2] == '_':
                            first_node = first_node[:-2]
                    if rule.rhs[0].nonTerminal == first_node:
                        node.doof.transition_ops[k].insert(0, ('push', node.label + '_e'))
                    else:
                        node.doof.transition_ops[k].insert(0, ('push', node.label + '_h'))
        if v in end_states:
            # pass
            node.doof.transition_ops[k].append('pop')