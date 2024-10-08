import pickle
import os
import json

here = os.path.dirname(os.path.abspath(__file__))


class Exportable:

    def preformatListRecurse(self, depth=0):
        textString = ""
        if not len(self.children):
            return self.name
        
        for i, c in enumerate(self.children):
            textString += c.preformatListRecurse(depth=depth+1)
            if i < len(self.children)-1:
                textString += ", " # includes oxford comma

        return textString

    def listRecurse(self, relationship = "contains", depth=0):
        textString = ""
        if not len(self.children):
            return self.name

        if depth > 0:
            textString += f"{self.name}, which {relationship}"
        else:
            textString += f"{self.name}, {relationship} "
        for i, c in enumerate(self.children):
            if i == len(self.children) and "and" not in self.name.lower():
                textString += ", and "
            textString += c.listRecurse(relationship=relationship, depth=depth+1)
            textString += "\n" # includes oxford comma

        return textString

    def toMarkdown(self, **kwargs):
        # print(self.name)

        # for k, v in kwargs.items():
        #    exec("self." + k + " = v")

        markdownString = ""
        htmlString = ""
        textString = ""

        if hasattr(self, "meta") and "ignore" in self.meta:
            if self.meta["ignore"]:
                return {"html": htmlString, "markdown": markdownString, "text": textString}
            
        if self.depth == 0:
            htmlString += "<html>\n"
            htmlString += (
                f'<body style="color: {self.fromAbove("textColor")} ;align:{self.fromAbove("align")}">\n'
            )

        # if "font" in self.meta.keys():
        #    htmlString += "<span style=\""
        #    for k, v in self.meta["font"].items():
        #        htmlString += k + ":" + str(v) + ";"
        #    htmlString += "\">"

        if self.meta["type"] == "lineage":
            # put the graph title
            # markdownString += self.name + "\n"
            # htmlString += self.name + "\n"
            markdownString += "\n"
            htmlString += "\n"
            # and include the graph!
            gv = self.toGraphViz(params=self.meta)
            markdownString += gv["markdown"]
            htmlString += gv["html"]
            textString += f"Here is our {self.name}. "
            for c in self.children:
                textString += c.listRecurse(depth=0)

        elif self.meta["type"] == "prompt":
            htmlString += "<i>"
            htmlString += '<ol style="list-style: none;padding-left: 0;">'

            referenceSuperscript = self.getReferenceSuperscript()
            htmlString += referenceSuperscript["html"]
            markdownString += referenceSuperscript["markdown"]

            textString += self.preformatListRecurse()
            htmlString += "</i>"

            # double newline after
            markdownString += "\n\n"
            htmlString += "\n\n"

        elif self.meta["type"] == "list":
            # put the list title
            verseSuperscript = self.addVerseNo()
            #print(self.name)
            htmlString += verseSuperscript["html"] + self.name + "\n"
            markdownString += verseSuperscript["markdown"] + self.name + "\n"
            textString += self.name + "\n"
            if self.meta["topology"] != "flat":
                htmlString += "<ol>"

            # start listing
            if self.meta["topology"] == "flat":
                htmlString += "<ol>\n"
                for child in self.flatten()[1:]:
                    htmlString += "<li>" + child.name + "</li>\n"
                    markdownString += "- " + child.name + "\n"
                htmlString += "</ol>\n"
            else:
                for child in self.children:
                    markdownString += child.toList(depth=0)["markdown"]
                    htmlString += child.toList(depth=0)["html"]
                htmlString += "</ol>"

            referenceSuperscript = self.getReferenceSuperscript()
            htmlString += referenceSuperscript["html"]
            markdownString += referenceSuperscript["markdown"]

            textString += self.preformatListRecurse()

            # double newline after
            markdownString += "\n\n"
            htmlString += "\n\n"

        elif self.meta["type"] == "eval":
            toEval = self.meta["command"]
            out = eval(toEval)
            markdownString += out["markdown"] + "\n"
            htmlString += out["html"] + "\n"

        elif self.meta["type"] == "wisdom":
            # print verse number and name
            verseSuperscript = self.addVerseNo()
            referenceSuperscript = self.getReferenceSuperscript()
            htmlString += (
                verseSuperscript["html"] + str(self.name) + referenceSuperscript["html"]
            )
            markdownString += (
                verseSuperscript["markdown"]
                + str(self.name)
                + referenceSuperscript["markdown"]
            )

            if markdownString[-1] not in [".", "!", ":", ",", ">", "?", "\n"]:
                htmlString += ". "
                markdownString += ". "

            htmlString += "<br>"
            markdownString += "\n\n"

        elif self.meta["type"] == "default":
            # if its height is 0, this is normal text
            if self._maxheight == 0:
                # print verse number and name
                verseSuperscript = self.addVerseNo()
                referenceSuperscript = self.getReferenceSuperscript()
                textString += self.name.replace("<br>", '')
                htmlString += (
                    verseSuperscript["html"]
                    + str(self.name)
                    + referenceSuperscript["html"]
                )
                markdownString += (
                    verseSuperscript["markdown"]
                    + str(self.name)
                    + referenceSuperscript["markdown"]
                )

                if markdownString[-1] not in [".", "!", ":", ",", ">", "?", "\n"]:
                    htmlString += ". "
                    markdownString += ". "

            # otherwise its a title / heading
            else:
                markdownString += "\n"
                markdownString += "#" * (self.depth) + " " + self.name + "\n\n"
                if self.depth == 0:
                    htmlString += "<title>" + self.name + "</title>\n"
                self.genURL()
                htmlString += (
                    "<h"
                    + str(self.depth + 1)
                    + ">"
                    + "<a href=" 
                    + self.url
                    + ">"
                    + self.name
                    + "</a>"
                    + "</h"
                    + str(self.depth + 1)
                    + ">\n"
                )
                self.getApex().verseNo = 0
                # htmlString     += "\n<hr>"

                # add paragraph tag
                #htmlString += f'<p align="{self.getApex().align}">'
                # markdownString += (
                #    "<p align=\"justify\">"
                # )

            # dont forget the children
            for child in self.children:
                childMark = child.toMarkdown()
                markdownString += childMark["markdown"]
                htmlString += childMark["html"]

            # add a new line between paragraphs
            if self._maxheight > 0:
                # double newline after
                markdownString += "\n\n"
                htmlString += "\n"

            # if its height is 1, add paragraph end
            if self._maxheight != 0:
                pass
                #htmlString += "</p>"
                # markdownString += (
                #    "</p>"
                # )

        else:
            print(self.meta["type"])
            die

        # if "font" in self.meta.keys():
        #    htmlString += "</p>"

        if self.depth == 0:
            htmlString += "</body>\n"
            htmlString += "</html>\n"

        return {"html": htmlString, "markdown": markdownString, "text": textString}

    def addVerseNo(self):
        markdownString = ""
        htmlString = ""

        if hasattr(self.getApex(), "displayVerseNo"):
            verseNo = self.getApex().verseNo
            markdownString += "<sup>" + str(verseNo) + "</sup> "
            htmlString += "<sup>" + str(verseNo) + "</sup> "
            # print("incrementing")
            self.getApex().verseNo += 1
        return {"html": htmlString, "markdown": markdownString}

    def getReferenceSuperscript(self):
        markdownString = ""
        htmlString = ""

        if "reference" in self.meta.keys():
            for reference in self.meta["reference"]:
                referenceNo = self.getApex().referenceNo
                referenceLetter = f"{referenceNo}"
                self.getApex().referenceNo += 1
                markdownString += (
                    "<sup>[" + referenceLetter + "](" + reference + ")</sup> "
                )
                htmlString += (
                    "<sup><a href=" + reference + ">" + referenceLetter + "</a></sup> "
                )

        return {"html": htmlString, "markdown": markdownString}

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

        # print(self.clusterName)

        if self.meta["ignore"]:
            return dotNotationString

        # everything is a box in descendance
        if not any([c.meta["relationship"] == "within" for c in self.children]):
            # translate box parameters
            dotNotationString += self.clusterName + boxParamsString

        # insert the child nodes
        # provided we havent reached max depth
        if (
            "maxDepth" not in self.meta.keys()
            or (self.depth - startDepth) < self.meta["maxDepth"]
        ):
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
                    dotNotationString += (
                        self.clusterName + " -> " + c.clusterName + " ["
                    )
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
        # if self.meta["relationship"] == "within":
        #    dotString += "node [ fontname=\"Handlee\" ];\n"

        # kwargs["boxParams"] = self.meta["boxParams"]
        for c in self.children:
            dotString += c.asDotNotation(startDepth=c.depth)
        dotString += "}"

        self.imageName = os.path.join(
            self.getApex().graphsDir, self.name.replace(" ", "_") + ".png"
        )
        # print(self.imageName)
        # dont regenerate graphs if indicated
        if hasattr(self.getApex(), "skipGraphs") and self.getApex().skipGraphs:
            pass
        else:
            buildGraphDir = os.path.join(
                self.getApex().buildDir,
                self.getApex().graphsDir)
            os.makedirs(buildGraphDir, exist_ok=True)
            # write out the dot notation file
            dotFilename = os.path.join(
                buildGraphDir,
                self.name.replace(" ", "_") + ".dot",
            )
            print(dotFilename)
            if "build" not in dotFilename:
                die
            with open(dotFilename, "w+") as f:
                f.write(dotString)

            self.buildImageName = os.path.join(self.getApex().buildDir, self.imageName)
            # convert to image
            runstring = f"{self.meta['engine']} -Tpng {dotFilename} -o '{self.buildImageName}'"
            print(runstring)
            os.system(runstring)

        # reference it in the markdown
        markdownString = (
            self.name
            + "\n"
            + ("\n![" + self.name + "](/" + self.imageName + "?raw=true)\n\n")
        )

        # and HTML
        htmlString = (
            "<br>"
            + '<figure><img src="'
            + "/" 
            + self.imageName
            + f'" width="100%"><figcaption>{self.name}</figcaption></figure>\n'
        )

        return {"html": htmlString, "markdown": markdownString}

    def toList(self, depth=0):
        markdownString = ""
        markdownString += "  " * depth
        markdownString += "- "
        markdownString += self.name + "\n"

        # do children markdown
        for c in self.children:
            markdownString += c.toList(depth=depth + 1)["markdown"]

        # make self as item
        htmlString = ""
        htmlString += "<li>\n"
        htmlString += self.name

        referenceSuperscript = self.getReferenceSuperscript()
        htmlString += referenceSuperscript["html"]
        markdownString += referenceSuperscript["markdown"]

        # create a list of children, if applicable
        if len(self.children):
            htmlString += "<ol>\n"
            for c in self.children:
                htmlString += c.toList(depth=depth + 1)["html"]
            htmlString += "</ol>\n"

        # end self as item
        htmlString += "</li>"

        return {"html": htmlString, "markdown": markdownString}

    def toTableOfContents(self, minHeight=0, maxDepth=-1):
        markdownString = ""
        htmlString = ""
        if "tableOfContentsSkip" in self.meta.keys():
            return {"html": htmlString, "markdown": markdownString}

        if self.depth > maxDepth and maxDepth >= 0:
            return {"html": htmlString, "markdown": markdownString}

        if self._maxheight < minHeight:
            return {"html": htmlString, "markdown": markdownString}

        markdownString += "  " * self.depth
        markdownString += "- "
        markdownString += self.name + "\n"

        # do children markdown
        for c in self.children:
            markdownString += c.toTableOfContents(
                minHeight=minHeight, maxDepth=maxDepth
            )["markdown"]

        # make self as item
        htmlString += "<li>\n"
        if hasattr(self.getApex(), "link"):
            htmlString += (
                "<a href=#" + self.name.replace(" ", "_") + ">" + self.name + "</a>"
            )
        else:
            htmlString += self.name

        # create a list of children, if applicable
        if len(self.children):
            htmlString += "<ol>\n"
            for c in self.children:
                htmlString += c.toTableOfContents(
                    minHeight=minHeight, maxDepth=maxDepth
                )["html"]
            htmlString += "</ol>\n"

        # end self as item
        htmlString += "</li>"

        return {"html": htmlString, "markdown": markdownString}


def fromDict(name, indict, parent=None):
    if type(indict) is dict:
        thisNode = Exportable(name=name, parent=parent)
        for k, v in indict.items():
            thisNode.children += [fromDict(name=k, indict=v, parent=thisNode)]
    else:
        thisNode = Exportable(name=name, parent=parent)

    return thisNode
