# INPUT DATA READING AND PREPARATION

from .data_structure_definitions import *
import functools

open_file = functools.partial(open, encoding='utf-8')


def buildTree(parsedSentence):

    beforeTree = parsedSentence.split(" ")
    beforeTree = beforeTree[1:]

    root = node(label="root", parent="self")
    curr = root

    tokenCount = 0
    tokenList = []

    for part in beforeTree:
        # adding nodes in depth first fashion
        if part[0] == "(":
            newNode = node(label=part[1:], parent=curr)
            curr.addIndexedChild(newNode)
            curr = newNode
            # print "New node added: ", curr.label

            # token information for a leaf node
        else:
            firstcurlindex = part.find(")")
            curr.token = part[:firstcurlindex]
            curr.tokenNum = tokenCount
            tokenCount = tokenCount+1
            tokenList.append(curr)
            # print "Added token ", curr.token

            # backtracking past completed part of tree
            for bracket in part[firstcurlindex:]:
                curr = curr.parent
                # print "Backtracking to ", curr.label

    return (root, tokenList)


def prepareData(data):

    hinTokenList = []
    hinRawList = data[1].split(" ")
    tokenCount = 0
    for el in hinRawList:
        hinTokenList.append(node(parent="self", token=el, tokenNum=tokenCount))
        tokenCount = tokenCount+1

    (root, engTokenList) = buildTree(data[3])

    # print([val.token for val in hinTokenList])
    # print([val.token for val in engTokenList])
    alignmentsRaw = data[4].split(" ")
    for align in alignmentsRaw:
        dashindex = align.find("-")
        hinInd = int(align[:dashindex])
        engInd = int(align[dashindex+1:])
        if engInd >= len(engTokenList):
            print(
                str(engInd) + " : index exceeds length of english sentence, " + len(engTokenList))
        else:
            engTokenList[engInd].alignments.append(hinInd)
        if hinInd >= len(hinTokenList):
            print(
                str(hinInd) + " : index exceeds length of hindi sentence, " + len(hinTokenList))
        else:
            hinTokenList[hinInd].alignments.append(engInd)

    for tok in engTokenList:
        tok.language = "English"
    for tok in hinTokenList:
        tok.language = "Hindi"

    return(root, engTokenList, hinTokenList)


def appPrepareData(hinSentence, parse, alignments):

    hinTokenList = []
    hinRawList = hinSentence.split(" ")
    tokenCount = 0
    for el in hinRawList:
        hinTokenList.append(node(parent="self", token=el, tokenNum=tokenCount))
        tokenCount = tokenCount+1

    (root, engTokenList) = buildTree(parse)

    alignmentsRaw = alignments.split(" ")
    for align in alignmentsRaw:
        dashindex = align.find("-")
        hinInd = int(align[:dashindex])
        engInd = int(align[dashindex+1:])
        if engInd >= len(engTokenList):
            print(
                str(engInd) + " : index exceeds length of english sentence, " + len(engTokenList))
        else:
            engTokenList[engInd].alignments.append(hinInd)
        if hinInd >= len(hinTokenList):
            print(
                str(hinInd) + " : index exceeds length of hindi sentence, " + len(hinTokenList))
        else:
            hinTokenList[hinInd].alignments.append(engInd)

    for tok in engTokenList:
        tok.language = "English"
    for tok in hinTokenList:
        tok.language = "Hindi"

    return(root, engTokenList, hinTokenList)
