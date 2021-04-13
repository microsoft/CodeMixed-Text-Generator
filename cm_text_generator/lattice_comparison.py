from fe_get_insertional_lattice import *
from fe_get_alternational_lattice import *
import uuid

def main():

  # sen1 = "There were no other houses beyond her garden , which made it seem as if her house lay at the end of the world"	
  # sen2 = "No habia otras casas mas alla su jardin , que hizo parecer como si su casa pone en el fin del mundo"	
  # align = "1-0 1-1 0-2 2-3 3-4 4-5 5-5 6-6 7-7 8-8 9-9 10-10 11-11 11-12 12-13 13-14 14-15 15-16 16-17 17-18 18-19 19-20 20-21 21-22 21-23"	
  # parse = "(ROOT (S (NP (EX There)) (VP (VBD were) (NP (NP (DT no) (JJ other) (NNS houses)) (PP (IN beyond) (NP (NP (PRP$ her) (NN garden)) (, ,) (SBAR (WHNP (WDT which)) (S (VP (VBD made) (SBAR (S (NP (PRP it)) (VP (VBP seem) (SBAR (RB as) (IN if) (S (NP (PRP$ her) (NN house)) (VP (VBD lay) (PP (IN at) (NP (NP (DT the) (NN end)) (PP (IN of) (NP (DT the) (NN world))))))))))))))))))))"
  
  sen1 = "She turned the corner into Clover Close"
  sen2 = "Ella doblo la esquina en el cierre de Clover"
  align = "0-0 1-1 2-2 3-3 4-4 7-5 8-5 5-6 6-6"
  parse = "(ROOT (S (NP (PRP She)) (VP (VBD turned) (NP (DT the) (NN corner)) (PP (IN into) (NP (NNP Clover) (NNP Close))))))"
  
  doof1 = fe_get_ins_lat(sen1, sen2, parse, align, "1", "1", "0", "0", "0")
  # doof.makeAllStrings(0, [], allStrings)
  doof2 = fe_get_ins_lat(sen1, sen2, parse, align, "1", "1", "0", "0", "0")
  # doof.makeAllStrings(0, [], allStrings)

  aliph = hackyAlphabet(doof1, doof2)
  ba = makeOfficialDfa(doof1, aliph)
  djim = makeOfficialDfa(doof2, aliph)
  printGraphicLibDfa(ba, "output\\one")
  printGraphicLibDfa(djim, "output\\two")
  
  djinn = intersection(ba, djim)
  djinn.minimize()
  printGraphicLibDfa(djinn, "output\\three")
  
  djinn = union(ba, djim)
  djinn.minimize()
  printGraphicLibDfa(djinn, "output\\four")
  
  djinn = inverse(djinn)
  djinn.minimize()
  printGraphicLibDfa(djinn, "output\\five")
  
  djinn = intersection(ba, djim)
  djinn.minimize()
  printGraphicLibDfa(djinn, "output\\six")
  
  djinn = symmetric_difference(ba, djim)
  djinn.minimize()
  printGraphicLibDfa(djinn, "output\\seven")
  

  
  
  
  
  # name = str(uuid.uuid4())
  # doof1.printGraphicDfa("output//"+name+"1")
  # doof2.printGraphicDfa("output//"+name+"2")
  
  # doof = fe_get_alt_lat(sen1, sen2, parse, align, "0", "0", "1")
  # doof.makeAllStrings(0, [], allStrings)

  # fp = open("esen\\" + name + "_ec.txt", "w")
  # for sen in allStrings:
    # fp.write(sen+"\n")
  # fp.close()



  
if __name__ == "__main__":
  main()