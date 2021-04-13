###DATA PREPARATION PIPELINE

import sys
from .data_structure_definitions import *
from .input_data_reading import *
from .input_data_modification import *
from .hindi_parse_tree import *
from .grammar_inference import *

def dataPreparationPipeline(data):
  ###INPUT DATA READING
  (root, engTokenList, hinTokenList)=prepareData(data)
  
  ###INPUT DATA MODIFICATION
  glueEnglishPhrases(root, engTokenList)
  glueHindiPhrases(hinTokenList)
  (hinTokenList, engTokenList)=reformat(hinTokenList, engTokenList)

  ###HINDI PARSE TREE
  # print([node.token for node in hinTokenList])
  # print([node.finalAlignment for node in hinTokenList])
  # print([node.token for node in engTokenList])
  # print([node.finalAlignment for node in engTokenList])
  hinRoot=projectHindiTree(hinTokenList, engTokenList)
  # print(hinRoot)
  # sys.exit(0)
  #treatNullMorphemes(hinRoot) (have commented this so that a surface form is seen for null morphemes)
  checkAndAdjustDirection(hinRoot)
  updateRepeatIndexEnglish(root)
  updateRepeatIndexHindi(hinRoot)

  ###GRAMMAR INFERENCE
  grammar=[]
  ruleEnlister(root.children[0], grammar)
  fillHindiRuleNums(hinRoot.children[0])
  projectHindiRules(hinRoot.children[0], grammar)
  setParents(root)
  setParents(hinRoot)
  checkRuleOrder(grammar)
  
  ###SENTENCES
  hinSentence = " ".join([item.token for item in hinTokenList])
  engSentence = " ".join([item.token for item in engTokenList])
  
  return root, hinRoot, engSentence, hinSentence, grammar
  
def appDataPreparationPipeline(hinSentence, parse, alignments):
  ###INPUT DATA READING
  (root, engTokenList, hinTokenList)=appPrepareData(hinSentence, parse, alignments)
  
  ###INPUT DATA MODIFICATION
  glueEnglishPhrases(root, engTokenList)
  glueHindiPhrases(hinTokenList)
  (hinTokenList, engTokenList)=reformat(hinTokenList, engTokenList)

  ###HINDI PARSE TREE
  hinRoot=projectHindiTree(hinTokenList, engTokenList)
  #treatNullMorphemes(hinRoot) (have commented this so that a surface form is seen for null morphemes)
  checkAndAdjustDirection(hinRoot)
  updateRepeatIndexEnglish(root)
  updateRepeatIndexHindi(hinRoot)

  ###GRAMMAR INFERENCE
  grammar=[]
  ruleEnlister(root.children[0], grammar)
  fillHindiRuleNums(hinRoot.children[0])
  projectHindiRules(hinRoot.children[0], grammar)
  setParents(root)
  setParents(hinRoot)
  checkRuleOrder(grammar)
  
  ###SENTENCES
  hinSentence = " ".join([item.token for item in hinTokenList])
  engSentence = " ".join([item.token for item in engTokenList])
  
  return root, hinRoot, engSentence, hinSentence, grammar