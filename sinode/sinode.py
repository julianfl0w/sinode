import pickle
import os
here = os.path.dirname(os.path.abspath(__file__))


class Generic(object):
    def __init__(self, **kwargs):
        self.children = []
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

#def dict2node(source, parent=None):
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

class Node(Generic):
    
    def sortChildrenByPriority(self):
        for c in self.children:
            c.sortChildrenByPriority()
        
        self.children.sort(key=lambda x: x.meta["priority"], reverse=False)
    
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

    def getApex(self):
        if self.parent is None:
            return self
        return self.parent.getApex()
    
    def computeHeight(self):
        if not len(self.children):
            self._height = 0
        else:
            self._height = 1 + max([c.computeHeight() for c in self.children])
            
        return self._height
    
    def computeHeightNoLists(self):
        if self.children == [] or self.meta["type"] != "default":
            self._height = 0
        else:
            self._height = 1 + max([c.computeHeightNoLists() for c in self.children])
            
        return self._height
    
    def fromAbove(self, key):
        if hasattr(self, key):
            return self.key
        elif self.parent is not None:
            return self.parent.fromAbove(key)
        else:
            raise Exception("Key not found above")
        
    def flatten(self):
        toret = [self]
        for c in self.children:
            toret += c.flatten()
        return toret
        
def NodeFromFile(filename):
    # open a file, where you ant to store the data
    with open(filename, "rb") as f:
        # dump information to that file
        a = pickle.load(f)
    return a


class Sinode(Node):
    def __init__(self, **kwargs):
        Node.__init__(self)
        self.parent = kwargs.get("parent") # enforce single inheritance
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

    def toAbove(self, fnName, kwargs = {}):
        # if this class has the function, 
        # call it on v
        fn = getattr(self, fnName, None)
        if callable(fn):
            if kwargs == {}:
                return fn()
            else:
                return fn(kwargs)
        
        #otherwise, try the parent
        else:
            return self.parent.toAbove(fnName, kwargs)

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

