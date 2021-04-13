#!/usr/bin/python

# DRIVER

from __future__ import print_function
import sys
import subprocess
import os.path
import re
import uuid
# import graphviz
import nltk.tree

from random import randint
from subprocess import STDOUT, PIPE
from copy import copy, deepcopy

from .data_structure_definitions import *
from .embedded_matrix_lattice import *
from .equivalence_constraint_lattice import *
from .data_preparation_pipeline import *

from .play_with_dfa import *

import functools    
open_file = functools.partial(open, encoding='utf-8')

all_CM_sentences = set()
linguistic_theory = ''

# import sys

# def tracefunc(frame, event, arg, indent=[0]):
#       if event == "call":
#           indent[0] += 2
#           try:
#             print("-" * indent[0] + "> call function ->", frame.f_code.co_name, ", on line:", frame.f_lineno, "in:", frame.f_code.co_filename.split("/")[-1], "with arguments:", [frame.f_locals[x] for x in frame.f_code.co_varnames[:frame.f_code.co_argcount]])
#           except AttributeError as err:
#               print("ERROR:", err)
#       elif event == "return":
#         #   print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
#           indent[0] -= 2
#       return tracefunc

def makeInsertionalLattice(model, sentencePair):
    global linguistic_theory

    if model.matrix == 1:
        makeEmLattice(sentencePair.root_1, sentencePair.grammar, model, linguistic_theory)
        doof = sentencePair.root_1.doof
    if model.matrix == 2:
        makeEmLattice(sentencePair.root_2, sentencePair.grammar, model, linguistic_theory)
        doof = sentencePair.root_2.doof

    return doof


def makeAlternationalLattice(model, sentencePair):
    global linguistic_theory

    populateMethodLabels(sentencePair.root_1, sentencePair.grammar)
    # if model.allowLexicalSubstitution == True:
    # populateLexSubFlags(sentencePair.root_1, model.lexSubLabels)
    makeEqLattice(sentencePair.root_1.children[0], sentencePair.grammar, linguistic_theory)
    doof = sentencePair.root_1.children[0].doof
    # doof.printGraphicDfa(None)
    return doof


def generateRandomSentence(doof):

    mySentence = ""
    currState = doof.initialStates[0]
    possibleTransitions = [(k[1], v)
                           for k, v in doof.transitions.items() if k[0] == currState]
    while possibleTransitions != []:
        myInt = randint(0, len(possibleTransitions)-1)
        mySentence = mySentence+" "+possibleTransitions[myInt][0][:-2]
        currState = possibleTransitions[myInt][1]
        possibleTransitions = [
            (k[1], v) for k, v in doof.transitions.items() if k[0] == currState]

    return mySentence


def generateAllSentencesEC(doof, currState, currString, parseString, stack):
    global all_CM_sentences
    # all_CM_sentences = set()
    possibleTransitions = [(k[1], v)
                           for k, v in doof.transitions.items() if k[0] == currState]
    possibleTransition_ops = [(k[1], doof.transition_ops[k])
                           for k, v in doof.transitions.items() if k[0] == currState]

    if possibleTransitions != []:
        for i in range(len(possibleTransitions)):
            new_stack = copy.copy(stack)
            new_State = possibleTransitions[i][1]
            new_parseString = parseString
            for op in possibleTransition_ops[i][1]:
                if type(op) == str:
                    if op == "match":
                        new_parseString += " {}".format(possibleTransitions[i][0][:-2])
                    else: # op is pop
                        new_stack.pop()
                        new_parseString += ")"
                else: #len is 2
                    new_stack.append("(")
                    new_parseString += " ({}".format(op[1])
            generateAllSentencesEC(
                doof, new_State, currString+' '+possibleTransitions[i][0][:-2], new_parseString, new_stack)
    else:
        all_CM_sentences.add((currString.strip(), parseString))

    return

def generateAllSentencesML(doof, currState, currString, parseString, stack):
    global all_CM_sentences
    # all_CM_sentences = set()
    possibleTransitions = [(k[1], v)
                           for k, v in doof.transitions.items() if k[0] == currState]

    if possibleTransitions != []:
        for i in range(len(possibleTransitions)):
            new_State = possibleTransitions[i][1]
            generateAllSentencesML(
                doof, new_State, currString+' '+possibleTransitions[i][0][:-2], '', [])
    else:
        all_CM_sentences.add((currString.strip(), ''))

    return

def minimize(doof):

    oldStates = 0
    iterations = 0

    while oldStates != len(doof.states) and iterations < 100:
        iterations = iterations + 1
        oldStates = len(doof.states)
        trimTrapStates(doof)
        removeUnreachableStates(doof)
        # removeUselessStates(doof)
        # mergeEquivalentStates(doof)
        # removeDollarTransitions(doof)

    # print "Minimization took", str(iterations), "rounds"


def changeAlignmentFormat(alignments, langOneSen, langTwoSen):

    langOneRanges = {}
    wordCount = 0
    characterIndex = 0
    firstChar = 0
    while characterIndex < len(langOneSen):
        while characterIndex < len(langOneSen) and langOneSen[characterIndex] != " ":
            characterIndex = characterIndex + 1
        langOneRanges[(firstChar, characterIndex - 1)] = wordCount
        firstChar = characterIndex + 1
        wordCount = wordCount + 1
        characterIndex = characterIndex + 1

    langTwoRanges = {}
    wordCount = 0
    characterIndex = 0
    firstChar = 0
    while characterIndex < len(langTwoSen):
        while characterIndex < len(langTwoSen) and langTwoSen[characterIndex] != " ":
            characterIndex = characterIndex + 1
        langTwoRanges[(firstChar, characterIndex - 1)] = wordCount
        firstChar = characterIndex + 1
        wordCount = wordCount + 1
        characterIndex = characterIndex + 1

    alignmentList = alignments.split(" ")
    finalAlignmentList = []
    for alignment in alignmentList:
        range = alignment.split("-")
        langOneEndPoints = range[0].split(":")
        langTwoEndPoints = range[1].split(":")
        langOneToken = langOneRanges[(
            int(langOneEndPoints[0]), int(langOneEndPoints[1]))]
        langTwoToken = langTwoRanges[(
            int(langTwoEndPoints[0]), int(langTwoEndPoints[1]))]
        finalAlignmentList.append(str(langOneToken)+'-'+str(langTwoToken))

    return " ".join(finalAlignmentList)


def main(combined_data):
    global all_CM_sentences
    global linguistic_theory
    
    all_CM_sentences = set()
    linguistic_theory = combined_data.pop()
    data = combined_data

    # get sentence pair for lattice building information
    (root_1, root_2, sentence_1, sentence_2,
     grammar) = dataPreparationPipeline(data)
    mySentencePair = sentencePairStructure()
    mySentencePair.sentence_1 = sentence_1
    mySentencePair.sentence_2 = sentence_2
    mySentencePair.root_1 = root_1
    mySentencePair.root_2 = root_2
    mySentencePair.grammar = grammar

    if linguistic_theory == 'ec':
        # define model for lattice building
        myModel2 = alternationalModelStructure()
        myModel2.allowLexicalSubstitution = True
        myModel2.allowIllFormed = False

        # build lattice!
        if myModel2.allowLexicalSubstitution == True:
            populateLexSubFlags(mySentencePair.root_1, myModel2.lexSubLabels)
        dfa2 = makeAlternationalLattice(myModel2, mySentencePair)

        if myModel2.allowIllFormed == False:
            disallowIllformedMonolingualFragmentsGeneric(
                dfa2, mySentencePair.sentence_1, mySentencePair.sentence_2)

        # minimize for viewing if required
        viewMinimize = True
        if viewMinimize == True:
            minimize(dfa2)

        generateAllSentencesEC(dfa2, dfa2.initialStates[0], '', '', [])
        
        all_CM_sentences_sorted = sorted(list(all_CM_sentences))
        if all_CM_sentences_sorted[0][0] != '':
            final_strings = []
            for (a, b) in all_CM_sentences_sorted:
                try:
                    t = nltk.tree.Tree.fromstring(b)
                    rules = t.productions()
                    if not(type(t[0]) == str) and not (0 in [len(rule.rhs()) for rule in rules]):
                        final_strings.append((a, '(ROOT{})'.format(b)))
                except:
                    continue
            # all_CM_sentences_sorted = [(a, '(ROOT{})'.format(b)) for (a,b) in all_CM_sentences_sorted]
        # all_CM_sentences_sorted = ['{}\t{}'.format(s[0], s[1])  for s in all_CM_sentences_sorted]
        return final_strings


    elif linguistic_theory == 'ml':
        # Matrix language 1
        myModel1 = insertionalModelStructure()
        dfa1 = makeInsertionalLattice(myModel1, mySentencePair)
        # print("myModel1:", myModel1.__dict__)
        # print("mySentencePair:", mySentencePair.__dict__)
        # print("dfa1:", dfa1.__dict__)
        # dfa1.printDfa()
        # dfa1.printGraphicDfa("before")
        generateAllSentencesML(dfa1, dfa1.initialStates[0], '', '', [])

        # Matrix language 2
        myModel1 = insertionalModelStructure_2()
        dfa1 = makeInsertionalLattice(myModel1, mySentencePair)
        generateAllSentencesML(dfa1, dfa1.initialStates[0], '', '', [])
        
        all_CM_sentences_sorted = sorted(list(all_CM_sentences))
        
        return all_CM_sentences_sorted

if __name__ == "__main__":
    # sys.setprofile(tracefunc)
    with open(sys.argv[1], 'r') as f:
        data = f.read().split('\n')
    res = main(data)
    res = ['{}\t{}'.format(s[0], s[1]) for s in res]
    gcm_output = '\n'.join(res) 
    with open(sys.argv[2], 'w') as f:
        f.write(gcm_output)