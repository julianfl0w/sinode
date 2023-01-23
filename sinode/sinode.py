import dill as pickle
import os

class Generic(object):
    def __init__(self, **kwargs):
        self.children = []
        self.priority = 999
        self.ignore = False
        self.type = "normal"
        self.proc_kwargs(**kwargs)
    def proc_kwargs(self, **kwargs):
        for key, value in kwargs.items():
            exec("self." + key + " = value")
        self.kwargs = kwargs.copy()
        for c in self.children:
            c.proc_kwargs(**self.kwargs)

            
def copyDictUnique(indict, modifier):
    outdict = {}
    if type(indict) == dict:
        for k, v in indict.items():
            outdict[k + modifier] = copyDictUnique(v, modifier)
        return outdict
    else:
        return indict + modifier


def dict2node(source, parent=None):
    retNodes = []
    if type(source) == dict:
        for k, v in source.items():
            print("Processing " + k)
            # dont record meta block
            if k == "meta":
                parent.meta = v
                continue
            thisNode = Node(name=k, parent=parent)
            thisNode.children = dict2node(v, parent=thisNode)
            retNodes += [thisNode]
        return retNodes
    elif type(source) == list:
        for i in source:
            retNodes += [dict2node(i, parent=parent)]
        return retNodes

    else:
        return Node(name=source)

class Node(Generic):
    
    def sortChildrenByPriority(self):
        for c in self.children:
            c.sortChildrenByPriority()
        
        self.children.sort(key=lambda x: x.priority, reverse=False)
    
    def __str__(self):
        retstr = str(type(self)) + "\n"
        for child in self.children:
            retstr += "  " + str(child).replace("\n", "  \n") + "\n"

        return retstr

    def asDict(self):
        retList = []
        for child in self.children:
            try:
                retList += [child.asDict()]
            except:
                retList += [str(child)]  # + " " + hex(id(child))]

        retDict = {}
        retDict[str(type(self))] = retList
        return retDict

    def getSiblings(self):
        return self.parent.children

    def descendants(self):
        d = self.children
        for c in self.children:
            d += c.descendants()
        return d

    def getAncestor(self, ancestorType):
        if not hasattr(self, "parent"):
            return false
        if ancestorType in str(type(self.parent)).lower():
            return self
        return self.parent.getAncestor(ancestorType)

    def __unicode__(self):
        return self.__str__()

    def release(self):
        for child in self.children:
            # print("PK releasing " + str(child))
            child.release()

    def toFile(self, filename):
        # open a file, where you ant to store the data
        with open(filename, "wb+") as f:
            # dump information to that file
            pickle.dump(self, f)

    def asDotNotation(self, depth = 0, **kwargs):
        self.dotNotationString = ""
        
        # create this key
        self.boxNameWithQuotes = '"' + self.name + '"'
        print(self.boxNameWithQuotes)
        
        if self.ignore:
            return self.dotNotationString
        
        for key, value in kwargs.items():
            exec(key + " = value")
            

        print(kwargs)
        # translate box parameters
        self.dotNotationString += self.boxNameWithQuotes + " ["
        for k, v in kwargs["boxParams"].items():
            self.dotNotationString += k + "=" + str(v) + ", "
        # remove final comma and space
        self.dotNotationString = self.dotNotationString[:-2]
        self.dotNotationString += "]\n"
        
        # relationships
        if self.parent is not None and hasattr(self.parent, "boxNameWithQuotes"):
            self.dotNotationString += self.parent.boxNameWithQuotes + " -> " + self.boxNameWithQuotes + " ["
            for k, v in kwargs["arrowParams"].items():
                self.dotNotationString += k + "=" + str(v) + ", "
            # remove final comma and space
            self.dotNotationString = self.dotNotationString[:-2]
            self.dotNotationString += "]\n"
                
        # provided we havent reached max depth
        if "maxDepth" in kwargs.keys() and depth >= kwargs["maxDepth"] :
            return self.dotNotationString
            
        kwargs["depth"] = depth+1
        # insert the child nodes
        for c in self.children:
            self.dotNotationString += c.asDotNotation(**kwargs)

        return self.dotNotationString

    def asList(self, depth=0):
        string = ""
        string += "  " * depth
        string += "- "
        string += self.name + "\n"

        for i in self.children:
            string += i.asList(depth=depth + 1)

        return string

    def toMarkdown(self):
        self.markdownString = ""
        
        # print verse number and name
        self.markdownString += (
            "<sup>" + str(self.getApex().verseNo) + "</sup> " + self.name + ". "
        )
        self.getApex().verseNo += 1

        return self.markdownString

    def toGraphViz(self, **kwargs):
        self.proc_kwargs(**kwargs)
        print("graphing")
        dotString = ""
        dotString += "digraph D {\n"
        
        # apply default params if none exist
        self.meta = {
            "type": "lineage",
            "graphParams": {
                "rankdir": "LR",
                "style": "filled",
                "color": "lightgrey",
                "bgcolor": "\"#262626\"",
                "fillcolor": "\"darkgray:gold\"",
                "gradientangle": 0,
            },
            "boxParams": {
                "shape": "box",
                #"color": "black",
                "color": "\"#262626\"",
                "fontcolor": "white",
                #"fillcolor": "\"darkorchid4:grey10\"",
                "fillcolor": "\"#6C2944:#29001C\"",
                "style": "filled",
                "gradientangle": 270.05,
            },
            "arrowParams":{
                "color": "white",
                "penwidth": 1,
            }
        }
        
        # translate graph parameters
        for k, v in self.meta["graphParams"].items():
            dotString += k + " = " + str(v) + "\n"
        # insert our own node
        #kwargs["boxParams"] = self.meta["boxParams"]
        dotString += self.asDotNotation(arrowParams = self.meta["arrowParams"], 
                                        boxParams = self.meta["boxParams"],**kwargs)
        dotString += "}"

        # write out the dot notation file
        filename = os.path.join("graphs", self.name.replace(" ", "_") + ".dot")
        with open(filename, "w+") as f:
            f.write(dotString)

        # convert to image
        imagename = os.path.join("graphs", self.name.replace(" ", "_") + ".png")
        runstring = "dot -Tpng '" + filename + "' -o " + "'" + imagename + "'"
        print(runstring)
        os.system(runstring)

        # reference it in the markdown
        self.markdownString = (
            "\n![" + self.name + "](/" + imagename + '?raw=true "' + self.name + '")\n\n'
        )

        return self.markdownString

    def getDecendentGenerationCount(self):
        if self.children == []:
            return 0
        else:
            return max([c.getHeight() for c in children])

    def getHeight(self):
        return getDecendentGenerationCount(self)

    def getAncestors(self):
        if self.parent is None:
            return [self]
        else:
            return self.parent.getAncestors() + [self]

    def getAncestor(self, ancestorType):
        print("checking " + str(self))
        print("type " + str(type(self)))
        if not hasattr(self, "parent"):
            return false
        if ancestorType in str(type(self)).lower():
            return self
        return self.parent.getAncestor(ancestorType)

    def isApex(self):
        return self.parent is None

    def getApex(self):
        if self.parent is None:
            return self
        return self.parent.getApex()
    
    def toPDF(self):
        preformat = self.toMarkdown()
        preformat = preformat.replace("/graphs", os.path.join(here, "graphs"))
        preformat = preformat.replace("?raw=true", "")
        # preformat = preformat.replace("<sup>", "")
        # preformat = preformat.replace("</sup>", "")

        with open("README_formatted.md", "w+") as f:
            f.write(preformat)

        # os.system("mdpdf -o README.pdf README_formatted.md")
        os.system("pandoc --pdf-engine=xelatex README_formatted.md -s -o README.pdf")

    def computeHeight(self):
        if not len(self.children):
            self._height = 0
        else:
            self._height = 1 + max([c.computeHeight() for c in self.children])
            
        return self._height
        
def NodeFromFile(filename):
    # open a file, where you ant to store the data
    with open(filename, "rb") as f:
        # dump information to that file
        a = pickle.load(f)
    return a


class Sinode(Node):
    def __init__(self, parent=None):
        Node.__init__(self)
        self.parent = parent  # enforce single inheritance
        if not hasattr(self, "index"):
            self.index = 0
        # accumulate path
        if parent is not None:
            self.ancestors = parent.ancestors + [parent]
            self.path = parent.path + [self.index]
        else:
            self.ancestors = []
            self.path = [self.index]

        self.apex = self.getApex()


class Minode(Node):
    def __init__(self, parents):
        self.parents = parents  # allow multi inheritance through a set
        self.children = []

    def getAncestor(self, ancestorType):
        if not hasattr(self, "parent"):
            return false
        if str(type(self.parent)) == ancestorType:
            return self
        return self.parent.getAncestor(ancestorType)


class FractalBook(Node):
    def __init__(self, **kwargs):
        # defaults
        self.name = ""
        self.priority = 1000
        Node.__init__(self, **kwargs)
        
        if not os.path.exists("graphs"):
            os.mkdir("graphs")
        
        # print("Ignore " + str(ignore))
        if self.origin == "directory":
            
            self.name = self.source.split(os.sep)[-1]
        
            # read in ignore file
            if os.path.exists(os.path.join(self.source, "ignore.py")):
                with open(os.path.join(self.source, "ignore.py"), "r") as f:
                    ignore = eval(f.read())
            else:
                ignore = []

            # list files by priority
            
                
            # iterate over files
            for file in os.listdir(self.source):
                resolved = os.path.join(self.source, file)
                
                # check for special files
                if file in ignore or file == "ignore.py":
                    continue
                elif file == "meta.py":
                    with open(resolved, 'r') as f:
                        self.meta = eval(f.read())
                        for k, v in self.meta.items():
                            exec("self." + k + " = v")
                    continue

                # if its a dir, its a subcategory
                if os.path.isdir(resolved):
                    self.children += [FractalBook(parent = self, origin = "directory", source = resolved, depth=self.depth + 1)]

                # otherwise, if it's a python file, execute it
                # each python file is a chapter, containing a list of paragraphs
                else:
                    if file.endswith(".py"):
                        print("processing file " + file)
                        self.children += [FractalBook(parent = self, origin = "file", source = resolved, depth=self.depth + 1)]
                        
        elif self.origin == "file":
            print("Adding chapter " + self.source)
            self.name = self.source.split(os.sep)[-1].replace(".py", "")
            with open(self.source, "r") as f:
                print(self.source)
                self.source = eval(f.read())
                
            self.processText()
            
        
        elif self.origin == "text":
            self.processText()
            
        # if it has no children, assume its a sentence
        if not len(self.children):
            self.origin = "sentence"
        
        self.computeHeight()
        self.sortChildrenByPriority()
            
    def processText(self):
        if type(self.source) == list:
            raise Exception("Lists not allowed!")
            #for i, paragraph in enumerate(chapter):
            #    self.children += [FractalBook(parent = self, origin="text", source=paragraph)]
        if type(self.source) == dict:
            for k, v in self.source.items():
                if k == "meta":
                    self.meta = v
                    for k, v in self.meta.items():
                        exec("self." + k + " = v")
                    continue
                self.children += [FractalBook(parent = self, depth = self.depth+1, name = k, origin="text", source=v)]
                    
    def toMarkdown(self):
        self.verseNo = 0
        self.markdownString = ""
        
        if self.ignore:
            return self.markdownString

        self.markdownString += self.name + "\n"
        if self.type == "lineage":
            self.markdownString += self.toGraphViz(params=self.meta)
        elif self.type == "list":
            for child in self.children:
                self.markdownString += child.asList(depth = 0   )
            self.markdownString += "\n\n"


        else:
            # add its title
            if self._height > 0:
                self.markdownString += "#" * (self.depth) + " " + self.name + "\n"
                self.getApex().verseNo = 0

            else:
                self.markdownString += self.name + ". "

            for child in self.children:
                self.markdownString += child.toMarkdown()

            if self._height >= 1:
                # add a new line between paragraphs
                self.markdownString += "\n\n"
            
        return self.markdownString


if __name__ == "__main__":
    m = FractalBook(os.path.join(here, "Book Of Julian"), depth=1)

    preformat = m.toMarkdown()
    with open("README.md", "w+") as f:
        f.write(preformat)
    die
    preformat = preformat.replace("/graphs", os.path.join(here, "graphs"))
    preformat = preformat.replace("?raw=true", "")
    # preformat = preformat.replace("<sup>", "")
    # preformat = preformat.replace("</sup>", "")

    with open("README_formatted.md", "w+") as f:
        f.write(preformat)

    # os.system("mdpdf -o README.pdf README_formatted.md")
    os.system("pandoc --pdf-engine=xelatex README_formatted.md -s -o README.pdf")
