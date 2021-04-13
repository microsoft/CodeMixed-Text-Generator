#!/usr/bin/python

###DRIVER

import sys, subprocess, os.path, re
import uuid
# import graphviz

from random import randint
from subprocess import STDOUT, PIPE
from copy import copy, deepcopy

from .data_structure_definitions import *
from .embedded_matrix_lattice import *
from .equivalence_constraint_lattice import *
from .data_preparation_pipeline import *

from .play_with_dfa import *

all_CM_sentences = set()
def makeInsertionalLattice(model, sentencePair):

  if model.matrix == 1:
    makeEmLattice(sentencePair.root_1, sentencePair.grammar, model)
    doof = sentencePair.root_1.doof
  if model.matrix == 2:
    makeEmLattice(sentencePair.root_2, sentencePair.grammar, model)
    doof = sentencePair.root_2.doof
  
  return doof
  
def makeAlternationalLattice(model, sentencePair):

  populateMethodLabels(sentencePair.root_1, sentencePair.grammar)
  # if model.allowLexicalSubstitution == True:
    # populateLexSubFlags(sentencePair.root_1, model.lexSubLabels)
  makeEqLattice(sentencePair.root_1.children[0], sentencePair.grammar)
  doof = sentencePair.root_1.children[0].doof

  return doof    

def generateRandomSentence(doof):
    
  mySentence = ""
  currState = doof.initialStates[0] 
  possibleTransitions = [(k[1],v) for k,v in doof.transitions.items() if k[0] == currState]
  while possibleTransitions != []:
    myInt = randint(0, len(possibleTransitions)-1)
    mySentence = mySentence+" "+possibleTransitions[myInt][0][:-2]
    currState = possibleTransitions[myInt][1]
    possibleTransitions = [(k[1],v) for k,v in doof.transitions.items() if k[0] == currState]

  return mySentence  
    
def generateAllSentences(doof, currState, currString):

  possibleTransitions = [(k[1],v) for k,v in doof.transitions.items() if k[0] == currState]

  if possibleTransitions != []:
  	for i in range(len(possibleTransitions)):
  		new_State = possibleTransitions[i][1]
  		generateAllSentences(doof, new_State, currString+' '+possibleTransitions[i][0][:-2])
  else:
  	all_CM_sentences.add(currString.strip())
  	# print currString.strip()

  return

def minimize(doof):

  oldStates = 0
  iterations = 0
  
  while oldStates != len(doof.states) and iterations < 100:
    iterations = iterations + 1
    oldStates = len(doof.states)
    trimTrapStates(doof)
    removeUnreachableStates(doof)
    removeUselessStates(doof)
    mergeEquivalentStates(doof)
    removeDollarTransitions(doof)
    
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
    langOneToken = langOneRanges[(int(langOneEndPoints[0]), int(langOneEndPoints[1]))]
    langTwoToken = langTwoRanges[(int(langTwoEndPoints[0]), int(langTwoEndPoints[1]))]
    finalAlignmentList.append(str(langOneToken)+'-'+str(langTwoToken))
    
  return " ".join(finalAlignmentList)
  
def main(data):
 
  ###get sentence pair for lattice building information
  (root_1, root_2, sentence_1, sentence_2, grammar)  = dataPreparationPipeline(data)
  mySentencePair = sentencePairStructure()
  mySentencePair.sentence_1 = sentence_1
  mySentencePair.sentence_2 = sentence_2
  mySentencePair.root_1 = root_1
  mySentencePair.root_2 = root_2
  mySentencePair.grammar = grammar
  
  ###define model for lattice building
  # myModel2 = alternationalModelStructure()
  # myModel2.allowLexicalSubstitution = True
  # myModel2.allowIllFormed = False
    
  ###build lattice!
  # if myModel2.allowLexicalSubstitution == True:
  #   populateLexSubFlags(mySentencePair.root_1, myModel2.lexSubLabels)
  # dfa2 = makeAlternationalLattice(myModel2, mySentencePair)
  
  
  # if myModel2.allowIllFormed == False:
  #   disallowIllformedMonolingualFragmentsGeneric(dfa2, mySentencePair.sentence_1, mySentencePair.sentence_2)
    
  # fp = "output\\"+str(uuid.uuid4())
  # dfa1.printGraphicDfa(fp)
  # dfa1.printDfa()
    
    
  ###minimize for viewing if required
  # viewMinimize = True
  # if viewMinimize == True:
  #   minimize(dfa2)     
    
  ###print for viewing  
  # fp = "output\\"+str(uuid.uuid4())
  #dfa1.printGraphicDfa(fp)
  # dfa2.printDfa()

  
  ###generate random sentence if required
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)
  # print generateRandomSentence(dfa2)

  # Matrix language 1
  myModel1 = insertionalModelStructure()
  dfa1 = makeInsertionalLattice(myModel1, mySentencePair)
  generateAllSentences(dfa1, dfa1.initialStates[0], '')
  # Matrix language 2
  myModel1 = insertionalModelStructure_2()
  dfa1 = makeInsertionalLattice(myModel1, mySentencePair)
  generateAllSentences(dfa1, dfa1.initialStates[0], '')
  # generateAllSentences(dfa2, dfa2.initialStates[0], '')
  # print "\nAll possible sentences\n"
  all_CM_sentences_sorted = sorted(list(all_CM_sentences))
  print('\n'.join(all_CM_sentences_sorted))
  # print("# generated sentences: %d" % (len(all_CM_sentences_sorted)))

  ###compare dfa's
  # alphabet = hackyAlphabet(dfa1, dfa2)
  # dfa1 = makeOfficialDfa(dfa1, alphabet)
  # dfa2 = makeOfficialDfa(dfa2, alphabet)
  # uDfa = union(dfa1, dfa2)
  # uDfa.minimize()
  # printGraphicLibDfa(uDfa, "output\\symdiff")
  
  
  

  
if __name__=="__main__":
  main()
