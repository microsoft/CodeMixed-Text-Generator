import sys
from data_structure_definitions import *
from data_preparation_pipeline import *
import uuid


def main():
    
  sen2 = sys.argv[1]
  
  parse = sys.argv[2][:-1]
  parseSplit = parse.split(" ")
  parseSplit = parseSplit[1:]
  formattedParse = "( " + " ".join(parseSplit) + " )"
  
  alignment = sys.argv[3]
  
  (root1, root2, sen1, sen2, grammar)  = appDataPreparationPipeline(sen2, formattedParse, alignment)
  
  print("Success")
  
  fn = "output\\"+str(uuid.uuid4())
  root1.printTreeToFile(fn)
  print(fn)
  
  fn = "output\\"+str(uuid.uuid4())
  root2.printTreeToFile(fn)
  print(fn)
  
  
if __name__ == "__main__":
  main()