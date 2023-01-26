import pickle
import os
from . import sinode
import json
here = os.path.dirname(os.path.abspath(__file__))

def toPDF(intext, basedir = here, ext="html"):
    preformat = intext
    preformat = preformat.replace("/graphs", os.path.join(basedir, "graphs"))
    preformat = preformat.replace("?raw=true", "")
    # preformat = preformat.replace("<sup>", "")
    # preformat = preformat.replace("</sup>", "")

    formattedFilename = "README_formatted." + ext
    with open(formattedFilename, "w+") as f:
        f.write(preformat)

    # os.system("mdpdf -o README.pdf README_formatted.md")
    os.system("pandoc --pdf-engine=xelatex " + formattedFilename + " -s -o README.pdf")

def depthFirstDictMerge(priority, additions):
    if type(priority) is dict:  
        retdict = priority.copy()
        for k,v in additions.items():
            if k in retdict.keys():
                retdict[k] = depthFirstDictMerge(retdict[k], v)
            else:
                retdict[k] = v
        return retdict
                
    elif type(priority) is list:
        return priority + additions
    
    else:
        return priority
    
    
    
class FractalBook(sinode.Node):
    def __init__(self, **kwargs):
        # defaults
        self.name = ""
        # the default meta
        self.meta = {
            "priority": 1000,
            "type": "default",
            "graphParams": {
                "rankdir": "LR",
                "style": "filled",
                "color": "lightgrey",
                "bgcolor": "\"#262626\"",
                "fillcolor": "\"darkgray:gold\"",
                "gradientangle": 0,
                "dpi": 300,
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
        sinode.Node.__init__(self, **kwargs)
        
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
            
            # iterate over files
            for file in os.listdir(self.source):
                resolved = os.path.join(self.source, file)
                
                # check for special files
                if file in ignore or file == "ignore.py":
                    continue
                elif file == "meta.py":
                    with open(resolved, 'r') as f:
                        self.meta = depthFirstDictMerge(eval(f.read()), self.meta)
                        #for k, v in self.meta.items():
                        #    exec("self." + k + " = v")
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
        # if its a list, add all elements as children
        if type(self.source) == list:
            for element in self.source:
                self.children += [FractalBook(parent = self, depth = self.depth+1, name = "", origin="text", source=element)]
                self.meta = depthFirstDictMerge({"type": "list"}, self.meta)
        
        # similar with dictionary, except the elements are named
        if type(self.source) == dict:
            for k, v in self.source.items():
                # read meta, dont add as child
                if k == "meta":
                    #print(json.dumps(self.meta, indent=2))
                    self.meta = depthFirstDictMerge(v, self.meta)
                    if "font" in v.keys():
                        print(json.dumps(self.meta, indent=2))
                        die
                    #for k, v in self.meta.items():
                    #    exec("self." + k + " = v")
                    continue
                self.children += [FractalBook(parent = self, depth = self.depth+1, name = k, origin="text", source=v)]
                    
    def toMarkdown(self, **kwargs):
        
        for k, v in kwargs.items():
            exec("self." + k + " = v")
        
        self.verseNo = 0
        
        markdownString = ""
        htmlString = ""
        
        if self.ignore:
            return {"html":htmlString, "markdown":markdownString}
        
        if self.depth == 0:
            htmlString += "<html>\n"
            htmlString += "<body style=\"color:white;align:justify\">\n"
            
        if "font" in self.meta.keys():
            htmlString += "<p "
            for k, v in self.meta["font"].items():
                htmlString += k + " : " + str(v) + ";\n" 
                
            
        if self.meta["type"] == "lineage":
            # put the graph title
            markdownString += self.name + "\n"
            htmlString += self.name + "\n"
            # and include the graph!
            self.toGraphViz(params=self.meta)
            
        elif self.meta["type"] == "list":
            # put the list title
            if self.name != "Prompt":
                markdownString += self.name + "\n"
                htmlString += self.name + "\n"
                htmlString += "<ul>"
            else:
                htmlString     += "<i>"
                htmlString += "<ul style=\"list-style: none;padding-left: 0;\">"
            
            # start listing
            for child in self.children:
                markdownString += child.toList(depth = 0)["markdown"]
                htmlString     += child.toList(depth = 0)["html"]
                
            htmlString += "</ul>"
            
            if self.name == "Prompt":
                htmlString     += "</i>"
               
            
            # double newline after
            markdownString += "\n\n"
            htmlString     += "\n\n"

        elif self.meta["type"] == "eval":
            #print(self.children[0].name)
            htmlString += eval(self.children[0].children[0].name) + "\n"
            
        elif self.meta["type"] == "default":
            
            
            # if its height is 0, this is normal text
            if self._height == 0:
                
                # print verse number and name
                if hasattr(self.getApex(), "displayVerseNo"):
                    markdownString += (
                        "<sup>" + str(self.getApex().verseNo) + "</sup> "
                    )
                    htmlString += (
                        "<sup>" + str(self.getApex().verseNo) + "</sup> "
                    )    
                    self.getApex().verseNo += 1
                    
                markdownString += self.name + ". "
                    
                htmlString += self.name + ". "
                
            # otherwise its a title / heading
            else:
                markdownString += "#" * (self.depth) + " " + self.name + "\n\n"
                if self.depth == 0:
                    htmlString += "<title>" + self.name + "</title>\n"
                htmlString += ("<h" + str(self.depth+1) + ">" + 
                                    "<a name=" + self.name.replace(" ","_") + ">" + 
                                    self.name + 
                                    "</a>"+
                                    "</h" + str(self.depth+1) + ">\n")
                self.getApex().verseNo = 0
                #htmlString     += "\n<hr>"
                
            # if its height is 1, add paragraph tag
            if self._height == 1:
                htmlString += (
                    "<p align=\"justify\">"
                )    
                
                
            # dont forget the children
            for child in self.children:
                markdownString += child.toMarkdown()["markdown"]
                htmlString     += child.toMarkdown()["html"]

            # add a new line between paragraphs
            if self._height > 0:
                # double newline after
                markdownString += "\n\n"
                htmlString     += "\n"
                
            # if its height is 1, add paragraph end
            if self._height == 1:
                htmlString += (
                    "</p>"
                )    
        
        else:
            print(self.meta["type"])
            die

        if "font" in self.meta.keys():
            htmlString += "</p>"

        if self.depth == 0:
            htmlString += "</body>\n"
            htmlString += "</html>\n"
            
        return {"html":htmlString, "markdown":markdownString}


    def asDotNotation(self, depth = 0, **kwargs):
        dotNotationString = ""
        
        # create this key. its just a number. the label will be set later
        self.boxNameWithQuotes = '"' + str(self.getApex().nodeNumber) + '"'
        self.getApex().nodeNumber += 1
        
        kwargs["boxParams"]["label"] = '"' + self.name + '"'
        #print(self.boxNameWithQuotes)
        
        if self.ignore:
            return dotNotationString
        
        for key, value in kwargs.items():
            exec(key + " = value")
            

        #print(kwargs)
        # translate box parameters
        dotNotationString += self.boxNameWithQuotes + " ["
        for k, v in kwargs["boxParams"].items():
            dotNotationString += k + "=" + str(v) + ", "
        # remove final comma and space
        dotNotationString = dotNotationString[:-2]
        dotNotationString += "]\n"
        
        # relationships
        if self.parent is not None and hasattr(self.parent, "boxNameWithQuotes"):
            dotNotationString += self.parent.boxNameWithQuotes + " -> " + self.boxNameWithQuotes + " ["
            for k, v in kwargs["arrowParams"].items():
                dotNotationString += k + "=" + str(v) + ", "
            # remove final comma and space
            dotNotationString = dotNotationString[:-2]
            dotNotationString += "]\n"
                
        # provided we havent reached max depth
        if "maxDepth" in kwargs.keys() and depth >= kwargs["maxDepth"] :
            return dotNotationString
            
        kwargs["depth"] = depth+1
        # insert the child nodes
        for c in self.children:
            dotNotationString += c.asDotNotation(**kwargs)

        return dotNotationString

    def toGraphViz(self, **kwargs):
        self.getApex().nodeNumber = 0
        self.proc_kwargs(**kwargs)
        print("graphing")
        dotString = ""
        dotString += "digraph D {\n"
                
        # translate graph parameters
        for k, v in self.meta["graphParams"].items():
            dotString += k + " = " + str(v) + "\n"
        # insert our own node
        #kwargs["boxParams"] = self.meta["boxParams"]
        dotString += self.asDotNotation(arrowParams = self.meta["arrowParams"], 
                                        boxParams = self.meta["boxParams"],**kwargs)
        dotString += "}"

        imagename = os.path.join("graphs", self.name.replace(" ", "_") + ".png")
        
        # dont regenerate graphs if indicated
        if hasattr(self.getApex(), "skipGraphs") and self.getApex().skipGraphs:
            pass
        else:
            # write out the dot notation file
            filename = os.path.join("graphs", self.name.replace(" ", "_") + ".dot")
            with open(filename, "w+") as f:
                f.write(dotString)

            # convert to image
            runstring = "dot -Tpng '" + filename + "' -o " + "'" + imagename + "'"
            #print(runstring)
            os.system(runstring)

        # reference it in the markdown
        markdownString = (
            "\n![" + self.name + "](/" + imagename + '?raw=true""' + self.name + '")\n\n'
        )

        # and HTML
        htmlString = "<img src=\"" + imagename + "\" width=\"100%\">\n"

        return {"html":htmlString, "markdown":markdownString}

    def toList(self, depth=0):
        markdownString = ""
        markdownString += "  " * depth
        markdownString += "- "
        markdownString += self.name + "\n"
        
        # do children markdown
        for c in self.children:
            markdownString +=  c.toList(depth=depth + 1)["markdown"]

        # make self as item
        htmlString = ""
        htmlString += "<li>\n"
        htmlString += self.name
        
        # create a list of children, if applicable
        if len(self.children):
            htmlString += "<ul>\n"
            for c in self.children:
                htmlString += c.toList(depth=depth + 1)["html"]
            htmlString += "</ul>\n"

        # end self as item
        htmlString += "</li>"
        
        return {"html":htmlString, "markdown":markdownString}

    def toTableOfContents(self, depth=0, **kwargs):
        for key, value in kwargs.items():
            exec(key + " = value")
        kwargs["depth"] = depth + 1
            
        markdownString = ""
        htmlString = ""
        
        if depth > kwargs["maxDepth"]:
            return {"html":htmlString, "markdown":markdownString}
        
        markdownString += "  " * depth
        markdownString += "- "
        markdownString += self.name + "\n"
        
        # do children markdown
        for c in self.children:
            markdownString +=  c.toTableOfContents(**kwargs)["markdown"]

        # make self as item
        htmlString += "<li>\n"
        if hasattr(self.getApex(), "link"):
            htmlString += "<a href=#" + self.name.replace(" ", "_") + ">" + self.name + "</a>"
        else:
            htmlString += self.name
        
        # create a list of children, if applicable
        if len(self.children):
            htmlString += "<ul>\n"
            for c in self.children:
                htmlString += c.toTableOfContents(**kwargs)["html"]
            htmlString += "</ul>\n"

        # end self as item
        htmlString += "</li>"
        
        return {"html":htmlString, "markdown":markdownString}


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
