# DATA STRUCTURE DEFINITIONS
import graphviz
import time
import copy


class insertionalModelStructure(object):

    def __init__(self):
        self.switchLabels = ["CD", "FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RB", "RBR", "RBS", "RP", "SYM", "UH", "VBN",
                             "ADJP", "ADVP", "FRAG", "INTJ", "NP", "NX", "PP", "PRN", "PRT", "QP", "RRC", "UDP", "WHADJP", "WHADVP", "WHNP", "WHPP"]
        self.nest = False  # no nesting
        self.matrix = 1  # first language (can tak evalues 1 or 2)
        self.allowIllFormed = True  # no trimming ill formed monolingual fragments
        # currently we cannot disallow ill-formed as the function is tailored for nodes with only 2 inputs as in ec


class insertionalModelStructure_2(object):

    def __init__(self):
        self.switchLabels = ["CD", "FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RB", "RBR", "RBS", "RP", "SYM", "UH", "VBN",
                             "ADJP", "ADVP", "FRAG", "INTJ", "NP", "NX", "PP", "PRN", "PRT", "QP", "RRC", "UDP", "WHADJP", "WHADVP", "WHNP", "WHPP"]
        self.nest = False  # no nesting
        self.matrix = 2  # first language (can tak evalues 1 or 2)
        self.allowIllFormed = True  # no trimming ill formed monolingual fragments
        # currently we cannot disallow ill-formed as the function is tailored for nodes with only 2 inputs as in ec


class alternationalModelStructure(object):

    def __init__(self):
        self.lexSubLabels = ["CD", "FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP",
                             "NNPS", "RB", "RBR", "RBS", "RP", "SYM", "UH", "VBN", "FRAG", "INTJ"]
        self.allowLexicalSubstitution = False
        self.allowIllFormed = False


class sentencePairStructure(object):

    def __init__(self):
        self.sentence_1 = ""
        self.sentence_2 = ""
        self.root_1 = None
        self.root_2 = None
        self.grammar = None


class dfa(object):

    def __init__(self):
        self.states = []
        self.transitions = {}
        self.transition_ops = {}
        self.initialStates = []
        self.finalStates = []
        self.nextIndex = 0
        self.engEnd = -1
        self.hinEnd = -1
        self.mixEnd = -1

    def addState(self):
        self.states.append(self.nextIndex)
        self.finalStates.append(self.nextIndex)
        if len(self.states) == 1:
            self.initialStates = [self.nextIndex]
        self.nextIndex = self.nextIndex + 1
        return self.nextIndex - 1

    def addTransition(self, source, phrase, sink, ops):

        if phrase == "":
            phrase = "$"

        if source in self.states and sink in self.states:
            if (source, phrase) not in self.transitions:
                self.transitions[(source, phrase)] = sink
                self.transition_ops[(source, phrase)] = ops
                if source in self.finalStates:
                    self.finalStates.remove(source)
                return 1

            else:
                # print 'Transition from this state with this tag already exists', source, phrase, sink
                return 0

        else:
            # print 'One of the states specified doesn\'t exist'
            return 0

    def deleteState(self, index):
        # haven't considered sitaution in which index is an initial state, or in which other states
        # become final states due to its deletion
        if index in self.states:
            self.states.remove(index)
        self.transition_ops = {
            k: v for k, v in self.transition_ops.items() if k[0] != index and self.transitions[k] != index}
        self.transitions = {
            k: v for k, v in self.transitions.items() if k[0] != index and v != index}
        if index in self.finalStates:
            self.finalStates.remove(index)
        if self.engEnd == index:
            self.engEnd = -1
        if self.hinEnd == index:
            self.hinEnd = -1
        if self.mixEnd == index:
            self.mixEnd = -1

    def mergeSpokes(self):
        if self.engEnd != -1:
            if self.hinEnd != -1:
                if self.mixEnd != -1:  # 1-1-1
                    self.mergeStates(self.engEnd, [self.mixEnd, self.hinEnd])
                    self.mixEnd = self.engEnd
                    self.hinEnd = self.engEnd
                else:  # 1-1-0
                    self.mergeStates(self.engEnd, [self.hinEnd])
                    self.hinEnd = self.engEnd
            else:
                if self.mixEnd != -1:  # 1-0-1
                    self.mergeStates(self.engEnd, [self.mixEnd])
                    self.mixEnd = self.engEnd
                else:  # 1-0-0
                    return
        else:
            if self.hinEnd != -1:
                if self.mixEnd != -1:  # 0-1-1
                    self.mergeStates(self.hinEnd, [self.mixEnd])
                    self.mixEnd = self.hinEnd
                else:  # 0-1-0
                    return
            else:
                if self.mixEnd != -1:  # 0-0-1
                    return
                else:  # 0-0-0
                    return

    def makeInitialState(self, index):
        self.initialState = index

    def mergeStates(self, s1, others):
        temp = {}

        for o in others:
            self.states.remove(o)
            if o in self.initialStates:
                self.initialStates.remove(o)
                if s1 not in self.initialStates:
                    self.initialStates.append(s1)

            if o in self.finalStates:
                self.finalStates.remove(o)

        for (k, v), (k1, v1) in zip(self.transitions.items(), self.transition_ops.items()):
            if k[0] in others:
                self.transitions.pop(k)
                self.transition_ops.pop(k1)
                if ((s1, k[1]) in self.transitions) or v == s1:
                    # print 'Not adding this transition', k, v
                    self.transitions[k] = -1
                    self.transition_ops[k1] = []
                else:
                    self.transitions[(s1, k[1])] = v
                    self.transition_ops[(s1, k[1])] = copy.copy(v1)

                if s1 in self.finalStates:
                    self.finalStates.remove(s1)

            if v in others:
                if k[0] == s1:
                    print('Cannot merge states safely, your DFA is now garbage')
                    return
                self.transitions[k] = s1
                self.transition_ops[k1] = copy.copy(v1)

        self.transition_ops = {k: v for k, v in self.transition_ops.items() if k[0] in self.states and self.transitions[k] in self.states}
        self.transitions = {k: v for k, v in self.transitions.items(
        ) if k[0] in self.states and v in self.states}
        return

    def mergeDfa(self, other):
        self.states = self.states + \
            [val + self.nextIndex for val in other.states]

        for (k, v), (k1, v1) in zip(other.transitions.items(), other.transition_ops.items()):
            self.transitions[(k[0] + self.nextIndex, k[1])
                             ] = int(v) + self.nextIndex
            self.transition_ops[(k[0] + self.nextIndex, k[1])] = copy.copy(v1)

        self.finalStates = self.finalStates + \
            [val + self.nextIndex for val in other.finalStates]

        self.initialStates = self.initialStates + \
            [val + self.nextIndex for val in other.initialStates]

        # print "states", other.states
        self.nextIndex = self.nextIndex + max(other.states) + 1

    def mergeDfaSeries(self, other):

        if self.finalStates != []:
            currFinal = self.finalStates[0]
        else:
            currFinal = -1
        nextStart = self.nextIndex

        self.mergeDfa(other)
        self.engEnd = other.engEnd
        self.hinEnd = other.hinEnd
        self.mixEnd = other.mixEnd

        if currFinal != -1:
            self.mergeStates(currFinal, [nextStart])

    def mergeDfaParallel(self, other):

        currFinal = self.finalStates[0]
        currStart = self.initialStates[0]
        nextStart = self.nextIndex
        self.mergeDfa(other)
        self.mergeStates(currStart, [nextStart])
        self.mergeStates(currFinal, [self.nextIndex - 1])

    def printGraphicDfa(self, fp):
        g = graphviz.Digraph(format='jpg')
        g.body.extend(['rankdir=TB'])

        for s in self.states:
            g.node(str(s), shape='circle')

        for k, v in self.transitions.items():
            if k[0] in self.states and v in self.states:
                g.edge(str(k[0]), str(v), label=k[1][:-2])

        file = g.render(filename="image", view=True)

    def printDfa(self):
        print("Printing information about this DFA:")
        print(self.states)
        print(self.transitions)
        print(self.initialStates)
        print(self.finalStates)
        print(self.nextIndex)
        print(self.engEnd)
        print(self.mixEnd)
        print(self.hinEnd)

    def makeAllStrings(self, currState, currString, allStrings):
        possibleTransitions = {
            k: v for k, v in self.transitions.items() if k[0] == currState}

        if possibleTransitions == {}:
            sen = " ".join(currString)
            if sen not in allStrings:
                allStrings.append(sen)

        for k, v in possibleTransitions.items():
            self.makeAllStrings(v, currString + [k[1][:-2]], allStrings)

    def __repr__(self):
        return " ".join(["{} -> {}".format(key, self.transitions[key]) for key in self.transitions])


class node(object):

    def __init__(self, parent, label="XXXXX", token="XXXXX", tokenNum=-1):

        # tree constituent attributes
        self.label = label
        self.token = token
        self.tokenNum = tokenNum

        if parent == "self":
            self.parent = self
        else:
            self.parent = parent
        self.children = []

        self.ruleNum = -1  # rule applied at this node
        self.repeatIndex = 0  # index among siblings with the same label

        # code-switch related attributes
        self.language = ""

        self.alignments = []
        self.finalAlignment = -1
        self.counterpart = self

        self.canSwitch = 0  # can this node be switched in joshi model
        self.lexSubFlag = 0

        # helper fields for use during CS sentence generation
        self.eq = ""
        self.joshiSwitch = 0
        self.doof = dfa()
        self.methodLabel = 0
        self.phrase = ""
        self.emDfaStart = -1
        self.emDfaEnd = -1

    def addIndexedChild(self, newChild):
        for existingChild in self.children:
            if existingChild.label == newChild.label:
                newChild.repeatIndex = newChild.repeatIndex+1
        self.children.append(newChild)

    # printing functions
    def printSubTree(self, count):
        if self.token == "XXXXX":
            print("".join(count)+self.label+" " +
                  str(self.emDfaStart)+":"+str(self.emDfaEnd))
            for child in self.children:
                child.printSubTree(count+[" "])
        else:
            print("".join(count)+self.label+" "+self.token+" " +
                  str(self.emDfaStart)+":"+str(self.emDfaEnd))

    def printTree(self):
        self.printSubTree([])

    def printSubTreeToFile(self, fp, count):
        fp.write("".join(count)+self.label+" "+self.token+"\n")
        for child in self.children:
            child.printSubTreeToFile(fp, count+[" "])

    def printTreeToFile(self, filename):
        fp = open_file(filename, "w")
        self.printSubTreeToFile(fp, [])

    def printSubTreeToString(self, count):
        textTree = "".join(count) + self.label + " " + self.token + "\n"
        for child in self.children:
            textTree = textTree + child.printSubTreeToString(count+[" "])
        return textTree

    def printTreeToString(self):
        return self.printSubTreeToString([])

    def __repr__(self):
        if self.language == '':
            return self.label
        else:
            return "{}:{}_{}".format(self.label, self.token, 'e' if self.language is 'English' else 'h')


class grammarPoint(object):
    # for lhs/rhs non-terminal/terminal. index indicates position among siblings of same label.
    def __init__(self, nonTerminal, index, engRank, hinRank=-1):
        self.nonTerminal = nonTerminal
        self.index = index
        self.engRank = engRank
        self.hinRank = hinRank


class grammarRule(object):
    # lhs is a grammarPoint, rhs is a list of grammarPoints
    def __init__(self, ruleNum, lhs, rhs):
        self.ruleNum = ruleNum
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        lhs = self.lhs.nonTerminal
        rhs = " ".join([gP.nonTerminal for gP in self.rhs])
        return "{} -> {}".format(lhs, rhs)
