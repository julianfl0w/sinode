import pickle
import os
from . import sinode
from . import exportable
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
        retval = priority.copy()
        for k,v in additions.items():
            if k in retval.keys():
                retval[k] = depthFirstDictMerge(retval[k], v)
            else:
                retval[k] = v
        return retval
                
    elif type(priority) is list:
        return priority + additions
        die
    
    else:
        return priority
    
class FractalBook(sinode.Node, exportable.Exportable):
    def __init__(self, **kwargs):
        # defaults
        self.name = ""
        self.nodeNumber = 0
        self.verseNo = 0
        self.referenceNo = 0
        
        # the default meta
        sinode.Node.__init__(self, **kwargs)
        
        # create this key. its just a number. the label will be set later
        self.clusterName = '"cluster_' + str(self.getApex().nodeNumber) + '"'
        self.getApex().nodeNumber += 1
        
        if self.parent is not None:
            self.meta = self.parent.meta.copy()
            
        if not os.path.exists("graphs"):
            os.mkdir("graphs")
        
        if self.origin == "directory":
            
            self.name = self.source.split(os.sep)[-1]
        
            # iterate over files
            for file in os.listdir(self.source):
                resolved = os.path.join(self.source, file)
                
                # check for meta files
                if file == "meta.py":
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
            self.name = self.source.split(os.sep)[-1].replace(".py", "")
            with open(self.source, "r") as f:
                self.source = eval(f.read())
                
            self.processText()
            
        
        elif self.origin == "text":
            self.processText()
            
        # if it has no children, assume its a sentence
        if not len(self.children):
            self.origin = "sentence"
        
        self.computeHeightNoLists()
        self.sortChildrenByPriority()
        
            
    def processText(self):
        # if its a list, add all elements as children
        if type(self.source) == list:
            die
            for element in self.source:
                self.children += [FractalBook(parent = self, depth = self.depth+1, name = "", origin="text", source=element)]
                self.meta = depthFirstDictMerge({"type": "list"}, self.meta)
        
        # similar with dictionary, except the elements are named
        if type(self.source) == dict:
            for k, v in self.source.items():
                # read meta, dont add as child
                if k == "meta":
                    #print(json.dumps(self.meta, indent=2))
                    #print(self.name)
                    self.meta = depthFirstDictMerge(v, self.meta)
                    #for k, v in self.meta.items():
                    #    exec("self." + k + " = v")
                    continue
                self.children += [FractalBook(parent = self, depth = self.depth+1, name = k, origin="text", source=v)]
                    

if __name__ == "__main__":
    m = FractalBook(os.path.join(here, "Book Of Julian"), depth=1)

    preformat = m.toMarkdown()
    die
    with open("README.md", "w+") as f:
        f.write(preformat)
    preformat = preformat.replace("/graphs", os.path.join(here, "graphs"))
    preformat = preformat.replace("?raw=true", "")
    # preformat = preformat.replace("<sup>", "")
    # preformat = preformat.replace("</sup>", "")

    with open("README_formatted.md", "w+") as f:
        f.write(preformat)

    # os.system("mdpdf -o README.pdf README_formatted.md")
    os.system("pandoc --pdf-engine=xelatex README_formatted.md -s -o README.pdf")
