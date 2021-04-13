import sys

from data_structure_definitions import *
from input_data_reading import *
import graphviz

from nltk import Tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget

global index
import uuid

def populateGraph(node, graph, parentLabel):

  global index
  myLabel = str(index)+" "+node.label
  if node.token != "XXXXX":
    myLabel = myLabel + " " + node.token
  print(myLabel)
  graph.node(myLabel, shape = 'circle')
  if parentLabel != 'root':
    graph.edge(parentLabel, myLabel)

  index = index + 1
  for child in node.children:
    populateGraph(child, graph, myLabel)

def printParse(root, fp):
  g=graphviz.Digraph(format='jpg')
  g.body.extend(['rankdir=TB'])
  
  global index
  index = 0
  populateGraph(root, g, 'root')
  
  file=g.render(filename=fp)	  
  print(file)

def main():
  print("hi")
  parse = sys.argv[1][:-1]
  print(parse)
  parseSplit = parse.split(" ")
  parseSplit = parseSplit[1:]
  formattedParse = "( "+" ".join(parseSplit)+" )"
  print(formattedParse)
  (root, tokens) = buildTree(formattedParse)
  root.printTree()
  printParse(root.children[0], "output\\"+str(uuid.uuid4()))
  

if __name__ == "__main__":
  main()