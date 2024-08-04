import pickle
import os
import json
import re

here = os.path.dirname(os.path.abspath(__file__))

from inspect import getframeinfo, stack
from . import exportable

class Generic(exportable.Exportable):
    def __init__(self, **kwargs):
        if not hasattr(self, "children"):
            self.children = []
        self.proc_kwargs(**kwargs)
        if hasattr(self, "parent"):
            if self.parent is not None:
                self.index = len(self.getSiblings())
                if self not in self.parent.children:
                    self.parent.children += [self]

    def proc_kwargs(self, **kwargs):
        overwrite = kwargs.get("overwrite") == True
        propagate = kwargs.get("propagate") == True
        if overwrite:
            die
        for key, value in kwargs.items():
            if not hasattr(self, key) or overwrite:
                if key[0] in ["0","1","2","3","4","5","6","7","8","9"]:
                    key = "_" + key
                exec(f"self.{key} = value")

        if propagate:
            self.kwargs = kwargs.copy()
            for c in self.children:
                c.proc_kwargs(**self.kwargs)

    def setDefaults(self, **kwargs):
        self.proc_kwargs(**kwargs)


def copyDictUnique(indict, modifier):
    outdict = {}
    if type(indict) == dict:
        for k, v in indict.items():
            outdict[k + modifier] = copyDictUnique(v, modifier)
        return outdict
    else:
        return indict + modifier


def depthFirstDictMerge(priority, additions):
    if type(priority) is dict:
        retval = priority.copy()
        for k, v in additions.items():
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

def toJsonDict(self):
    if isinstance(self, Node):
        attributes_dict = {}  # Initialize an empty dictionary
        for attr in dir(self):
            if attr.startswith('__') or callable(getattr(self, attr)):
                continue
            if attr == "apex" or attr == "ancestors":
                continue

            attr_value = getattr(self, attr)  # Retrieve the value of the attribute
            print(f"Attribute: {attr}, Type: {type(attr_value).__name__}")  # Print the attribute name and type
            attributes_dict[attr] = toJsonDict(attr_value)  # Add the attribute and its value to the dictionary
        return attributes_dict
    
    elif isinstance(self, list):
        return [toJsonDict(e) for e in self]

    elif isinstance(self, dict):
        attributes_dict = {}  # Initialize an empty dictionary
        for k, v in self.items():
            attributes_dict[k] = toJsonDict(v)
        return attributes_dict
    
    elif str(type(self))== "<class 'numpy.ndarray'>":
        from . import mathnode
        if self.ndim == 1:
            return mathnode.numpy_array_to_base64(self)
        elif self.ndim == 2:
            return [mathnode.numpy_array_to_base64(self[i, :]) for i in range(self.shape[0])]

    return self

# def dict2node(source, parent=None):
#    retNodes = []
#    if type(source) == dict:
#        for k, v in source.items():
#            print("Processing " + k)
#            # dont record meta block
#            if k == "meta":
#                for k0, v0 in v:
#                    exec("self.parent." + k0 + " = v0")
#                    #parent.meta = v
#                continue
#            thisNode = Node(name=k, parent=parent)
#            thisNode.children = dict2node(v, parent=thisNode)
#            retNodes += [thisNode]
#        return retNodes
#    elif type(source) == list:
#        for i in source:
#            retNodes += [dict2node(i, parent=parent)]
#        return retNodes
#
#    else:
#        return Node(name=source)


class Upward(object):
    def get(self):
        retdict = {}
        if hasattr(self, "value"):
            retdict["value"] = self.value
        if hasattr(self, "text"):
            retdict["text"] = self.text

        if hasattr(self, "name"):
            key = self.name
        else:
            key = str(type(self))
        if hasattr(self, "index"):
            key += str(self.index)

        for c in self.children:
            if hasattr(c, "get"):
                k, cdict = c.get()
                retdict[k] = cdict

        return key, retdict

    def toAbove(self, fnName, kwargs={}):
        # if this class has the function,
        # call it on v
        fn = getattr(self, fnName, None)
        if callable(fn):
            if kwargs == {}:
                return fn()
            else:
                return fn(kwargs)

        # otherwise, try the parent
        else:
            return self.parent.toAbove(fnName, kwargs)

    def setAbove(self, varName, value):
        # if this class has the value, set it
        if hasattr(self, varName):
            exec("self." + varName + " = value")

        # otherwise, try the parent
        else:
            return self.parent.setAbove(varName, value)

    def getApex(self):
        if self.parent is None:
            return self
        return self.parent.getApex()

    #def debug(self, *args):
    #    self.fromAbove("_debug")(*args)

    def debug(self, *args):
        if hasattr(self.getApex(), "DEBUG") and self.getApex().DEBUG:
            caller = getframeinfo(stack()[1][0])
            print(
                "%s:%d - %s" % (os.path.basename(caller.filename), caller.lineno, args)
            )  # python3 syntax self.debug


class Leaf(Generic, Upward):
    def __init__(self, **kwargs):
        self.proc_kwargs(**kwargs)

import sys
def demunch(node):
    sys.setrecursionlimit(60)
    if isinstance(node, Generic):
        user_attributes = {key: value for key, value in node.__dict__.items() if not key.startswith('__')}
        for k, v in user_attributes.items():
            if k in ["parent", "children"]:
                continue
            print(k)
            user_attributes[k] = demunch(v)
        return user_attributes
    elif type(node) is list:
        return [demunch(e) for e in node]
    else:
        return node

            
def munch(name, indict, parent, depth=0):
    if type(indict) is dict:
        thisNode = Sinode(name=name, parent=parent, depth=depth+1, meta={"type":"default"})
        for k, v in indict.items():
            setattr(thisNode, k, munch(name=k, indict=v, parent=thisNode, depth=depth+1))
    elif type(indict) is list:
        return [munch(str(i), v, parent = parent, depth=depth+1) for i, v in enumerate(indict)]
    else:
        return indict
    thisNode.depth= depth
    return thisNode

class Node(Generic, Upward):
    def getByField(self, name, val):
        if hasattr(self, name):
            print(eval("self." + name))
            if eval("self." + name) == val:
                return self
        elif len(self.children):
            for c in self.children:
                retval = c.getByField(name, val)
                if retval is not None:
                    return retval
        return None

    def dump(self):
        print(json.dumps(self.asDict(), indent=2))

    def sortChildrenByPriority(self):
        for c in self.children:
            c.sortChildrenByPriority()

        self.children.sort(key=lambda x: x.meta["priority"], reverse=False)

    def __str__(self):
        retstr = str(type(self)) + "\n"
        for child in self.children:
            retstr += "  " + str(child).replace("\n", "  \n") + "\n"

        return retstr

    def asDict(self, depth=0):
        childrenList = {}
        for i, child in enumerate(self.children):
            if isinstance(child, Generic):
                for childName, child in child.asDict(depth=depth + 1).items():
                    childrenList[childName] = child
            else:
                if hasattr(child, "name"):
                    childrenList[child.name] = {}
                else:
                    childrenList[str(child)] = {}

        retDict = {}
        if hasattr(self, "name"):
            retDict[self.name] = childrenList
        else:
            retDict[str(type(self))] = childrenList
        return retDict


    def asDictNumbered(self, depth=0):
        childrenList = {}
        for i, child in enumerate(self.children):
            if isinstance(child, Generic):
                for childName, child in child.asDict(depth=depth + 1).items():
                    childrenList[str(i) + ":" + childName] = child
            else:
                if hasattr(child, "name"):
                    childrenList[str(i) + ":" + child.name] = {}
                else:
                    childrenList[str(i) + ":" + str(child)] = {}

        retDict = {}
        if hasattr(self, "name"):
            retDict[self.name] = childrenList
        else:
            retDict[str(type(self))] = childrenList
        return retDict

    def asFlare(self, index=0, value=1000.0):
        print(self.name)
        retdict = dict(
            name=self.name,
            children=[],
            text=self.toMarkdown()["html"],
            indexedName=f"{index}\n\n{self.name}",
            meta=self.meta
        )

        if self._maxheight <= 1:
            retdict["value"] = value
            if self.parent is not None:
                retdict["parent"] = self.parent.name

            return retdict

        sfSum = sum(["skipFlare" not in c.meta.keys() for c in self.children])

        value = value / sfSum
        index = 0
        for c in self.children:
            if "skipFlare" not in c.meta.keys():
                retdict["children"] += [c.asFlare(index=index, value=value)]
                index += 1

        return retdict

    def asNamedDict(self):
        retList = []
        for child in self.children:
            try:
                retList += [child.asNamedDict()]
            except:
                retList += [str(child.name)]  # + " " + hex(id(child))]

        retDict = {}
        retDict[self.name] = retList
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

    def toJsonDict(self):
        return toJsonDict(self)

    def __repr__(self):
        return json.dumps(self.toJsonDict())

    def toJson(self, filename = None):
        attributes_dict = self.toJsonDict()
        if filename is None:
            return attributes_dict
        with open(filename, 'w') as file:
            json.dump(attributes_dict, file)

    def getDecendentGenerationCount(self):
        return self.getHeight()

    def getHeight(self):
        if self.children == []:
            return 0
        else:
            return max([c.getHeight() for c in children])

    def getHeightNoLists(self):
        if self.children == [] or self.meta["type"] != "default":
            return 0
        else:
            return max([c.getHeightNoLists() for c in children])

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

    def computeHeight(self):
        if not len(self.children):
            self._maxheight = 0
        else:
            self._maxheight = 1 + max([c.computeHeight() for c in self.children])
            self._minheight = 1 + min([c.computeHeight() for c in self.children])

        return self._maxheight

    def computeHeightNoLists(self):
        if self.children == [] or self.meta["type"] != "default":
            self._maxheight = 0
            self._minheight = 0
        else:
            self._maxheight = 1 + max([c.computeHeightNoLists() for c in self.children])
            self._minheight = 1 + min([c.computeHeightNoLists() for c in self.children])

        return self._maxheight

    def fromAbove(self, key):
        if hasattr(self, key):
            return eval("self." + key)

        curr = self
        while hasattr(curr, "parent") and curr.parent is not None:
            curr = curr.parent
            if hasattr(curr, key):
                return eval("curr." + key)

        raise Exception(f"Key {key} not found above")

    def flatten(self):
        toret = [self]
        for c in self.children:
            toret += c.flatten()
        return toret

    def update(self):
        for c in self.children:
            c.update()

    def getKeys(self, keyname):
        retlist = []
        print(dir(self))
        print(self.children)
        for c in self.children:
            retlist += c.getKeys(keyname)
        print(self.name)
        if self.name == keyname:
            retlist += [self]
        return retlist

    def munch(self, indict, depth=0):
        if type(indict) is dict:
            for k, v in indict.items():
                print(k)
                setattr(self, k, munch(name=k, parent=self, indict=v, depth=depth+1))
        elif type(indict) is list:
            for i, v in enumerate(indict):
                setattr(self, k, munch(name=str(i), parent=self, indict=v, depth=depth+1))
    
def NodeFromFile(filename):
    # open a file, where you ant to store the data
    with open(filename, "rb") as f:
        # dump information to that file
        a = pickle.load(f)
    return a

def fromDict(name, indict, parent=None, depth=0):
    print(" "*depth + name)
    if type(indict) is dict:
        thisNode = Sinode(name=name, parent=parent, depth=depth+1, meta={"type":"default"})
        for k, v in indict.items():
            thisNode.children += [fromDict(name=k, indict=v, parent=thisNode, depth=depth+1)]
    elif type(indict) is list:
        thisNode = Sinode(name=name, parent=parent, depth=depth+1, meta={"type":"default"})
        print(indict)
        thisNode.children = [fromDict(name=str(i), indict=v, parent=thisNode, depth=depth+1) for i, v in enumerate(indict)]
    else:
        thisNode = Sinode(name=name, parent=parent, depth=depth+1, meta={"type":"default"}, data=indict)
    thisNode.depth= depth
    return thisNode


def printdict(name, inval, depth=0):
    print(" "*depth + name)
    depth +=1
    if type(inval) is dict:
        for k, v in inval.items():
            printdict(k, v, depth)
    elif type(inval) is list:
        for i, item in enumerate(inval):
            printdict(str(i), item, depth)
    else:
        print(" "*depth + str(inval) + str(type(inval)))

class Sinode(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        self.parent = kwargs.get("parent")  # enforce single inheritance
        if not hasattr(self, "index"):
            self.index = 0
        # accumulate path
        if self.parent is not None:
            self.ancestors = self.parent.ancestors + [self.parent]
            self.path = self.parent.path + [self.index]
        else:
            self.ancestors = []
            self.path = [self.index]

        self.apex = self.getApex()

    def toAbove(self, fnName, kwargs={}):
        print(self)
        # if this class has the function,
        # call it on v
        fn = getattr(self, fnName, None)
        if callable(fn):
            if kwargs == {}:
                return fn()
            else:
                return fn(kwargs)

        # otherwise, try the parent
        else:
            return self.parent.toAbove(fnName, kwargs)
        
    def children2obj(self):
        for c in self.children:
            c.children2obj()
            # remove leading letters
            newName = re.sub(r'[^a-zA-Z]', '_', c.name)
            print(newName)
            command = f"self.{newName} = c"
            exec(command)


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
