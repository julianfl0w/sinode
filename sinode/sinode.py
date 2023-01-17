import dill as pickle
import os

class Generic(object):
    def __init__(self, **kwargs):
        self.children = []
        for key, value in kwargs.items():
            exec("self." + key + " = value")


def dict2node(content, parent=None):
    retNodes = []
    if type(content) == dict:
        for k, v in content.items():
            print("Processing " + k)
            # dont record meta block
            if k == "meta":
                parent.meta = v
                continue
            thisNode = Node(name=k, parent=parent)
            thisNode.children = dict2node(v, parent=thisNode)
            retNodes += [thisNode]
        return retNodes
    elif type(content) == list:
        for i in content:
            retNodes += [dict2node(i, parent=parent)]
        return retNodes

    else:
        return Node(name=content)


class Node(Generic):
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

    def asDotNotation(self, params):
        self.dotNotationString = ""
        # create this key
        self.boxNameWithQuotes = '"' + self.name + '"'
        print(self.boxNameWithQuotes)

        # translate box parameters
        self.dotNotationString += self.boxNameWithQuotes + " ["
        for k, v in params.items():
            self.dotNotationString += k + "=" + str(v) + ",\n "
        # remove final comma and space
        self.dotNotationString = self.dotNotationString[:-2]
        self.dotNotationString += "]\n"
        
        # insert the child nodes
        for c in self.children:
            self.dotNotationString += c.asDotNotation(params)

        # relationships
        for c in self.children:
            self.dotNotationString += self.boxNameWithQuotes + " -> " + c.boxNameWithQuotes + " [penwidth=1]\n"
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
        if hasattr(self, "meta"):
            if self.meta["type"] == "lineage":
                self.markdownString += self.toGraphViz(params=meta)

            elif self.meta["type"] == "list":
                self.markdownString += self.asList()

        else:
            # assume its a list of verses
            self.markdownString += self.name
            for c in self.children:
                self.markdownString += (
                    "<sup>" + str(self.verse) + "</sup> " + sentence + ". "
                )
                self.verse += 1

        return self.markdownString

    def toGraphViz(self):
        print("graphing")
        dotString = ""
        dotString += "digraph D {\n"
        # translate graph parameters
        for k, v in self.meta["graphParams"].items():
            dotString += k + " = " + str(v) + "\n"
        # insert our own node
        dotString += self.asDotNotation(self.meta["boxParams"])
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

        #
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

    
# a file is equivalent to a chapter
class Chapter(Node):
    def __init__(self, file, depth):
        Node.__init__(self)
        print("Adding chapter " + file)
        self.depth = depth
        self.verse = 0
        self.paragraphs = []
        self.name = file.split(os.sep)[-1].replace(".py", "")
        with open(file, "r") as f:
            print(file)
            chapter = eval(f.read())
            for i, paragraph in enumerate(chapter):
                self.paragraphs += [Paragraph(verse = self.verse, paragraph=paragraph)]
                self.verse += self.paragraphs[-1].verse
        self.children = self.paragraphs

    def toMarkdown(self):

        # add its title
        self.outstring = "#" * (self.depth) + " " + self.name + "\n"

        for child in self.children:
            self.outstring += child.toMarkdown()
            # add a new line between paragraphs
            self.outstring += "\n\n"
        return self.outstring

class Paragraph(Node):
    pass

class Category(Node):
    def __init__(self, directory, depth=0):
        Node.__init__(self)
        self.depth = depth
        self.chapters = []
        self.categories = []
        self.outstring = ""
        self.name = directory.split(os.sep)[-1]

        # read in ignore file
        if os.path.exists(os.path.join(directory, "ignore.py")):
            with open(os.path.join(directory, "ignore.py"), "r") as f:
                ignore = eval(f.read())
        else:
            ignore = []
        # print("Ignore " + str(ignore))

        # iterate over files
        for file in os.listdir(directory):
            if file in ignore or file == "ignore.py":
                continue
            resolved = os.path.join(directory, file)

            # if its a dir, its a subcategory
            if os.path.isdir(resolved):
                self.categories += [Category(resolved, depth + 1)]

            # otherwise, if it's a python file, execute it
            # each python file is a chapter, containing a list of paragraphs
            else:
                if file.endswith(".py"):
                    print("processing file " + file)
                    self.chapters += [Chapter(resolved, depth=depth + 1)]

    def toMarkdown(self):
        # add its title
        self.outstring += "#" * (self.depth) + " " + self.name + "\n"
        for chapter in self.chapters:
            self.outstring += chapter.toMarkdown()
        for category in self.categories:
            self.outstring += category.toMarkdown()
        return self.outstring


if __name__ == "__main__":
    m = Category(os.path.join(here, "Book Of Julian"), depth=1)

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
