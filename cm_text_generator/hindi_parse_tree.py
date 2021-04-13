###FOR HINDI PARSE TREE

from .data_structure_definitions import *
from .helper_functions import *
from copy import copy

def projectHindiTree(hinTokenList, engTokenList):
  
  hinTreeList=[]
  projBitList=[0]*len(engTokenList)

  for item in engTokenList:
    if item.finalAlignment==-1:
      projBitList[engTokenList.index(item)]=1

  for i in range(len(hinTokenList)):
    if (hinTokenList[i].finalAlignment == -1):
      # to ignore tokens without alignments to any English tokens
      continue
    # print(hinTokenList[i].token)
    hinTreeList.append(hinTokenList[i])
    projBitList[engTokenList[hinTokenList[i].finalAlignment].tokenNum]=1
    # print(projBitList)
    stack=[]
    stack.append(engTokenList[hinTokenList[i].finalAlignment].parent)
    while(stack[0].label!="root"):
      stack.insert(0, stack[0].parent)

    while (len(stack)>0 and usedUp(stack[-1], projBitList)) :
      # print('stack')
      # print([word.token for word in stack])
      lastOneOut=stack.pop()
      newElem=copy(lastOneOut)
      newElem.counterpart=lastOneOut
      newElem.counterpart.counterpart=newElem
      newElem.children=[]
	  
      for curr in hinTreeList:
        if curr.token=="XXXXX":
          if curr.parent==lastOneOut:
            newElem.addIndexedChild(curr)
            curr.parent=newElem
        else:
          if engTokenList[curr.finalAlignment].parent==lastOneOut:
            curr.label=engTokenList[curr.finalAlignment].label
            newElem.addIndexedChild(curr)
            curr.parent=newElem
      hinTreeList.append(newElem)
      

      # print "Now ---> "
      # for item in hinTreeList:
      #   print item.label, item.token, "(",
      #   for child in item.children:
      #     print child.label, child.token, child.language, ",",

      #   print ")"

      # hinTreeList[-1].printTree()
      
      if newElem.label=="root":
        return hinTreeList[-1]
		
def checkAndAdjustDirection(treeNode):

  # print(treeNode)
  treeNode.children=sorted(treeNode.children, key=lowToken)

  flag=True
  while(flag):
    flag=False
    for counter in range(len(treeNode.children)-1):
 
      if highToken(treeNode.children[counter])>=lowToken(treeNode.children[counter+1]):

        if(treeNode.children[counter].token=="XXXXX"):
          treeNode.children=treeNode.children.__add__(treeNode.children[counter].children)
          treeNode.counterpart.children=treeNode.counterpart.children.__add__(treeNode.children[counter].counterpart.children)
        if(treeNode.children[counter+1].token=="XXXXX"):
          treeNode.children=treeNode.children.__add__(treeNode.children[counter+1].children)
          treeNode.counterpart.children=treeNode.counterpart.children.__add__(treeNode.children[counter+1].counterpart.children)
        
		#separated from previous step so that the indices don't change during those operations
        if(treeNode.children[counter+1].token=="XXXXX"):
          treeNode.counterpart.children.remove(treeNode.children[counter+1].counterpart)
          del treeNode.children[counter+1]
        if(treeNode.children[counter].token=="XXXXX"):  
          treeNode.counterpart.children.remove(treeNode.children[counter].counterpart)
          del treeNode.children[counter]
		  
        treeNode.children=sorted(treeNode.children, key=lowToken)
        treeNode.counterpart.children=sorted(treeNode.counterpart.children, key=lowToken)
		
        for child in treeNode.children:
          child.parent=treeNode
        for child in treeNode.counterpart.children:
          child.parent=treeNode.counterpart

        flag=True
        break

  for child in treeNode.children:
    checkAndAdjustDirection(child) 