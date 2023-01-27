import pickle
import os
import json
here = os.path.dirname(os.path.abspath(__file__))

class Exportable:
    def toMarkdown(self, **kwargs):
        
        print(self.name)
                
        #for k, v in kwargs.items():
        #    exec("self." + k + " = v")
        
        
        markdownString = ""
        htmlString = ""
        
        if self.meta["ignore"]:
            return {"html":htmlString, "markdown":markdownString}
        
        if self.depth == 0:
            htmlString += "<html>\n"
            htmlString += """
        <head>
        <style>
        a:link {
          color: white;
          background-color: transparent;
          text-decoration: none;
        }
        a:visited {
          color: white;
          background-color: transparent;
          text-decoration: none;
        }
        a:hover {
          color: red;
          background-color: transparent;
          text-decoration: underline;
        }
        a:active {
          color: yellow;
          background-color: transparent;
          text-decoration: underline;
        }
        </style>
        </head>
    """
            htmlString += "<body style=\"color:white;align:justify\">\n"
        
            
        #if "font" in self.meta.keys():
        #    htmlString += "<span style=\""
        #    for k, v in self.meta["font"].items():
        #        htmlString += k + ":" + str(v) + ";" 
        #    htmlString += "\">"
                
            
        if self.meta["type"] == "lineage":
            # put the graph title
            #markdownString += self.name + "\n"
            #htmlString += self.name + "\n"
            markdownString += "\n"
            htmlString     += "\n"
            # and include the graph!
            gv = self.toGraphViz(params=self.meta)
            markdownString += gv["markdown"]
            htmlString += gv["html"]
            
        elif self.meta["type"] == "list":
            # put the list title
            if self.name != "Prompt":
                verseSuperscript = self.addVerseNo()
                htmlString += verseSuperscript["html"] + self.name + "\n"
                markdownString += verseSuperscript["markdown"] + self.name + "\n"
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
                verseSuperscript = self.addVerseNo()
                referenceSuperscript = self.getReferenceSuperscript()
                htmlString     += verseSuperscript["html"]     + self.name + referenceSuperscript["html"]    
                markdownString += verseSuperscript["markdown"] + self.name + referenceSuperscript["markdown"]
                
                htmlString     += ". "
                markdownString += ". "
                
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
                
                # add paragraph tag
                htmlString += (
                    "<p align=\"justify\">"
                )    
                
                
            # dont forget the children
            for child in self.children:
                childMark = child.toMarkdown()
                markdownString += childMark["markdown"]
                htmlString     += childMark["html"]

            # add a new line between paragraphs
            if self._height > 0:
                # double newline after
                markdownString += "\n\n"
                htmlString     += "\n"
                
            # if its height is 1, add paragraph end
            if self._height != 0:
                htmlString += (
                    "</p>"
                )    
        
        else:
            print(self.meta["type"])
            die

        #if "font" in self.meta.keys():
        #    htmlString += "</p>"

        if self.depth == 0:
            htmlString += "</body>\n"
            htmlString += "</html>\n"
            
        return {"html":htmlString, "markdown":markdownString}

    def addVerseNo(self):
        markdownString = ""
        htmlString     = ""
            
        if hasattr(self.getApex(), "displayVerseNo"):
            verseNo = self.getApex().verseNo
            markdownString += (
                "<sup>" + str(verseNo) + "</sup> "
            )
            htmlString += (
                "<sup>" + str(verseNo) + "</sup> "
            )    
            print("incrementing")
            self.getApex().verseNo += 1
        return {"html":htmlString, "markdown":markdownString}
    
    def getReferenceSuperscript(self):
        markdownString = ""
        htmlString     = ""
            
        if "reference" in self.meta.keys():
            for reference in self.meta["reference"]:
                referenceNo = self.getApex().referenceNo
                referenceLetter = chr(referenceNo+97)
                self.getApex().referenceNo += 1
                markdownString += (
                    "<sup>" + referenceLetter + "</sup> "
                )
                htmlString += (
                    "<sup><a href=" + reference + ">" + referenceLetter + "</a></sup> "
                )    
                
        return {"html":htmlString, "markdown":markdownString}
    
    def asDotNotation(self, **kwargs):
        for k, v in kwargs.items():
            exec(k + " = v")
        dotNotationString = ""
        
        self.boxLabel = '"' + self.name + '"'
        self.meta["boxParams"]["label"] = self.boxLabel
        
        boxParamsString = " ["
        boxParamsStringFlat = ""
        for k, v in self.meta["boxParams"].items():
            boxParamsString += k + "=" + str(v) + ", "
            boxParamsStringFlat += k + "=" + str(v) + ";\n "
        # remove final comma and space
        boxParamsString = boxParamsString[:-2]
        boxParamsString += "]\n"
        
        
        #print(self.clusterName)
        
        if self.meta["ignore"]:
            return dotNotationString
        
        # everything is a box in descendance
        if not any([c.meta["relationship"] == "within" for c in self.children]):
            # translate box parameters
            dotNotationString += self.clusterName + boxParamsString
            
        # insert the child nodes
        # provided we havent reached max depth
        if "maxDepth" not in self.meta.keys() or (self.depth-startDepth) < self.meta["maxDepth"] :
            if any([c.meta["relationship"] == "within" for c in self.children]):
                # start subgraph string
                dotNotationString += "subgraph " + self.clusterName + "{\n"
                dotNotationString += boxParamsStringFlat
                    
                # relationships
                # do contains relationship first
                for c in self.children:
                    if c.meta["relationship"] == "within":
                        dotNotationString += c.asDotNotation(**kwargs)
                        
                # close subgraph
                dotNotationString += "}\n"

            for c in self.children:
                if c.meta["relationship"] == "descends":
                    c.meta["arrowParams"]["ltail"] = self.clusterName
                    c.meta["arrowParams"]["lhead"] = c.clusterName
                    
                    dotNotationString += c.asDotNotation(**kwargs)
                    dotNotationString += self.clusterName + " -> " + c.clusterName + " ["
                    for k, v in c.meta["arrowParams"].items():
                        dotNotationString += k + "=" + str(v) + ", "
                    # remove final comma and space
                    dotNotationString = dotNotationString[:-2]
                    dotNotationString += "]\n"
            
        return dotNotationString

    def toGraphViz(self, **kwargs):
        for k, v in kwargs.items():
            exec(k + " = v")
            
        print("graphing")
        dotString = ""
        dotString += "digraph D {\n"
                
        # translate graph parameters
        for k, v in self.meta["graphParams"].items():
            dotString += k + " = " + str(v) + "\n"
            
        # insert our own node
        #if self.meta["relationship"] == "within":
        #    dotString += "node [ fontname=\"Handlee\" ];\n"
            
        #kwargs["boxParams"] = self.meta["boxParams"]
        dotString += self.asDotNotation(startDepth=self.depth)
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
            runstring = self.meta["engine"] + " -Tpng '" + filename + "' -o " + "'" + imagename + "'"
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

    def toTableOfContents(self, minHeight=0):
            
        markdownString = ""
        htmlString = ""
        
        #if depth > kwargs["maxDepth"]:
        #    return {"html":htmlString, "markdown":markdownString}
        
        if self._height < minHeight:
            return {"html":htmlString, "markdown":markdownString}
        
        markdownString += "  " * self.depth
        markdownString += "- "
        markdownString += self.name + "\n"
        
        # do children markdown
        for c in self.children:
            markdownString +=  c.toTableOfContents(minHeight=minHeight)["markdown"]

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
                htmlString += c.toTableOfContents(minHeight=minHeight)["html"]
            htmlString += "</ul>\n"

        # end self as item
        htmlString += "</li>"
        
        return {"html":htmlString, "markdown":markdownString}
