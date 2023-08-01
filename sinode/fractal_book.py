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

    
class FractalBook(sinode.Node, exportable.Exportable):
    def __init__(self, **kwargs):
        # defaults
        self.nodeNumber = 0
        self.verseNo = 0
        self.referenceNo = 0
        
        # the default meta
        sinode.Node.__init__(self, **kwargs)
        os.makedirs(self.getApex().graphsDir, exist_ok=True)
        # create this key. its just a number. the label will be set later
        self.clusterName = '"cluster_' + str(self.getApex().nodeNumber) + '"'
        self.getApex().nodeNumber += 1
        
        if self.parent is not None:
            self.meta = {}
            for k, v in self.parent.meta.items():
                if k not in self.parent.meta["noPropagate"]:
                    self.meta[k] = v
            
        if not os.path.exists("graphs"):
            os.mkdir("graphs")
        

        # Process a directory
        if self.origin == "directory":
            
            self.name = self.source.split(os.sep)[-1]
        
            # iterate over files
            for file in os.listdir(self.source):
                resolved = os.path.join(self.source, file)
                
                # check for meta files
                if file == "meta.py":
                    with open(resolved, 'r') as f:
                        self.meta = sinode.depthFirstDictMerge(eval(f.read()), self.meta)
                        #for k, v in self.meta.items():
                        #    exec("self." + k + " = v")
                    continue

                # if its a dir, its a subcategory
                if os.path.isdir(resolved):
                    FractalBook(parent = self, origin = "directory", source = resolved, depth=self.depth + 1)

                # otherwise, if it's a python file, execute it
                # each python file is a chapter, containing a list of paragraphs
                else:
                    if file.endswith(".py"):
                        print("processing file " + file)
                        FractalBook(parent = self, origin = "file", source = resolved, depth=self.depth + 1)

        # process a file
        # by reading it, and processing as texr  
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

        # if this is the apex, recursively 
        # sort children
        if self.parent is None:
            self.sortChildrenByPriority()
        
    
            
    def processText(self):
        # if its a list, add all elements as children
        if type(self.source) is list:
            for element in self.source:
                FractalBook(parent = self, depth = self.depth+1, name = "", origin="text", source=element)
                self.meta = sinode.depthFirstDictMerge({"type": "list"}, self.meta)
        
        # similar with dictionary, except the elements are named
        elif type(self.source) is dict:
            for k, v in self.source.items():
                # read meta, dont add as child
                if k == "meta":
                    #print(json.dumps(self.meta, indent=2))
                    #print(self.name)
                    self.meta = sinode.depthFirstDictMerge(v, self.meta)
                    #for k, v in self.meta.items():
                    #    exec("self." + k + " = v")
                    continue
                FractalBook(parent = self, depth = self.depth+1, name = k, origin="text", source=v)
        
        else:
            self.name = self.source

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
