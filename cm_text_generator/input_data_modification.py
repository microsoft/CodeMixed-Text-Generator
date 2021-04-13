###INPUT DATA MODIFICATION

from .data_structure_definitions import *
from .helper_functions import *

def glueEnglishPhrases(root, engTokenList):
  # print "My range is ", str(len(engTokenList)-1)
  for i in range(len(engTokenList)-1)[::-1]:
    continueFlag=False
    it=0
    while it<len(engTokenList[i].alignments) and continueFlag==False:
      jt=0
      while jt<len(engTokenList[i+1].alignments) and continueFlag==False:
        #print engTokenList[i].token, str(engTokenList[i].alignments[it]), str(engTokenList[i+1].alignments[jt]) 
        if engTokenList[i].alignments[it]==engTokenList[i+1].alignments[jt]:
          engTokenList[i].token=engTokenList[i].token+" "+engTokenList[i+1].token
          engTokenList[i].label=engTokenList[i].label+"+"+engTokenList[i+1].label
          engTokenList[i].alignments=engTokenList[i].alignments+ list(set(engTokenList[i+1].alignments)-set(engTokenList[i].alignments))
          engTokenList[i+1].token="XX"

          closestJoin=closestCommonAncestor(root, engTokenList[i], engTokenList[i+1]) 
          # print "Closest join of ", engTokenList[i].token, engTokenList[i+1].token, " is ", closestJoin.label
          ###NEW METHOD
          if closestJoin==engTokenList[i].parent:
            #engTokenList[i+1].parent.children.remove(engTokenList[i+1])
            deleteNodeRecursive(engTokenList[i+1])
          elif closestJoin==engTokenList[i+1].parent:
            #engTokenList[i].parent.children.remove(engTokenList[i])
            deleteNodeRecursive(engTokenList[i])
            closestJoin.children.insert(closestJoin.children.index(engTokenList[i+1]), engTokenList[i])
            engTokenList[i].parent=closestJoin
            closestJoin.children.remove(engTokenList[i+1]) #remove non-recursively as parent has at least one child, the glued token
          else:
            j=0
            while not ancestor(closestJoin.children[j], engTokenList[i+1]):
              j=j+1
            closestJoin.children.insert(j, engTokenList[i])
            #engTokenList[i+1].parent.children.remove(engTokenList[i+1])
            #engTokenList[i].parent.children.remove(engTokenList[i])
            deleteNodeRecursive(engTokenList[i]) #correctly removed as it still stores its previous parent's address
            deleteNodeRecursive(engTokenList[i+1])
            engTokenList[i].parent=closestJoin

          ###OLD METHOD
          # if closestJoin!=engTokenList[i].parent or closestJoin!=engTokenList[i+1].parent:
          #   newChildrenList=[]
          #   flattenTreeNode(closestJoin, newChildrenList)
          #   closestJoin.children=newChildrenList
          #   for child in newChildrenList:
          #     child.parent=closestJoin
          # else:
          #   closestJoin.children.remove(engTokenList[i+1]) 
          
          continueFlag=True #to indicate that this pair of tokens have already been glued and their alignments needn't be searched further
        jt=jt+1
      it=it+1

  #trimEmptyParents(root)

def glueHindiPhrases(hinTokenList):
  for i in range(len(hinTokenList)-1)[::-1]:
    it=0
    continueFlag=False
    while it<len(hinTokenList[i].alignments) and continueFlag==False:
      jt=0
      while jt<len(hinTokenList[i+1].alignments) and continueFlag==False:
        if hinTokenList[i].alignments[it]==hinTokenList[i+1].alignments[jt]:
          hinTokenList[i].token=hinTokenList[i].token+" "+hinTokenList[i+1].token
          hinTokenList[i].alignments=hinTokenList[i].alignments+ list(set(hinTokenList[i+1].alignments)-set(hinTokenList[i].alignments))
          hinTokenList[i+1].token="XX"
          continueFlag=True
        jt=jt+1
      it=it+1 

def reformat(hinTokenList, engTokenList):
  hinTokenList=list(filter(useful, hinTokenList))
  engTokenList=list(filter(useful, engTokenList))
  
  for elem1 in hinTokenList:
    for elem2 in engTokenList:
      if elem1.tokenNum in elem2.alignments:
        elem1.finalAlignment=engTokenList.index(elem2)
        elem2.finalAlignment=hinTokenList.index(elem1)
        
        elem1.counterpart=elem2
        elem2.counterpart=elem1

  for index in range(len(hinTokenList)):
    hinTokenList[index].tokenNum=index
  for index in range(len(engTokenList)):
    engTokenList[index].tokenNum=index

  return (hinTokenList, engTokenList)