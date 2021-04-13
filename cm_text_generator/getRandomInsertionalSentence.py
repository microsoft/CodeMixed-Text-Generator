import sys
import uuid

from bench import *

def main():

  ###get sentence pair for lattice building information
  sen1 = sys.argv[1]
  sen2 = sys.argv[2]
  
  parse = sys.argv[3][:-1]
  parseSplit = parse.split(" ")
  parseSplit = parseSplit[1:]
  formattedParse = "( " + " ".join(parseSplit) + " )"
  
  newAlignment = changeAlignmentFormat(sys.argv[4], sen1, sen2)
  
  (root_1, root_2, sentence_1, sentence_2, grammar)  = appDataPreparationPipeline(sen2, formattedParse, newAlignment)
  mySentencePair = sentencePairStructure()
  mySentencePair.sentence_1 = sentence_1
  mySentencePair.sentence_2 = sentence_2
  mySentencePair.root_1 = root_1
  mySentencePair.root_2 = root_2
  mySentencePair.grammar = grammar  
  
  ###define model for lattice building
  myModel1 = insertionalModelStructure()
  if sys.argv[5] == "1":
    myModel1.nest = True
  myModel1.matrix = int(sys.argv[6])
  if sys.argv[7] == "0":
    myModel1.allowIllFormed = False
  
  if sys.argv[8] != "0":
    myModel1.switchLabels = sys.argv[8].split(" ")
    
  ###build lattice
  dfa1 = makeInsertionalLattice(myModel1, mySentencePair)
  if myModel1.allowIllFormed == False:
    disallowIllformedMonolingualFragmentsGeneric(dfa1, mySentencePair.sentence_1, mySentencePair.sentence_2)
  
  ###minimize for viewing if required
  viewMinimize = int(sys.argv[9])
  if viewMinimize == 1:
    minimize(dfa1)

  # dfa1.printGraphicDfa("output\\"+str(uuid.uuid4()))    
  
  ###generate random sentence if required
  print(generateRandomSentence(dfa1))
  



if __name__ == "__main__":
  main()