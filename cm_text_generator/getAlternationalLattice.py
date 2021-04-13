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
  
  alignment = sys.argv[4]
  # newAlignment = changeAlignmentFormat(sys.argv[4], sen1, sen2)
  
  (root_1, root_2, sentence_1, sentence_2, grammar)  = appDataPreparationPipeline(sen2, formattedParse, alignment)
  mySentencePair = sentencePairStructure()
  mySentencePair.sentence_1 = sentence_1
  mySentencePair.sentence_2 = sentence_2
  mySentencePair.root_1 = root_1
  mySentencePair.root_2 = root_2
  mySentencePair.grammar = grammar  
  
  ###define model for lattice building
  myModel1 = alternationalModelStructure()
  if sys.argv[5] == "1":
    myModel1.allowLexicalSubstituion = True
  
  # if sys.argv[6] != "0":
    # myModel1.switchLabels = sys.argv[8].split(" ")
  
  if sys.argv[6] == "1":
    myModel1.allowIllFormed = True
  
  ###build lattice
  if myModel1.allowLexicalSubstitution == True:
    populateLexSubFlags(mySentencePair.root_1, myModel2.lexSubLabels)
  
  dfa1 = makeAlternationalLattice(myModel1, mySentencePair)
  
  if myModel1.allowIllFormed == False:
    disallowIllformedMonolingualFragmentsGeneric(dfa1, mySentencePair.sentence_1, mySentencePair.sentence_2)
  
  ###minimize for viewing if required
  viewMinimize = int(sys.argv[7])
  if viewMinimize == 1:
    minimize(dfa1)

  print("Success")  
  dfa1.printGraphicDfa("output\\"+str(uuid.uuid4()))    
  
  ###generate random sentence if required
  # print generateRandomSentence(dfa1)
  



if __name__ == "__main__":
  main()