from . import sinode

import kivy
#from kivy.uix.floatlayout import FloatLayout
#from kivy.uix.gridlayout import GridLayout
#from kivy.uix.textinput import TextInput
#from kivy.uix.label import Label
#from kivy.uix.treeview import TreeView
#from kivy.uix.treeview import TreeViewNode
#from kivy.uix.treeview import TreeViewLabel
#from kivy.uix.scrollview import ScrollView
#from kivy.uix.behaviors import DragBehavior
#from kivy.uix.widget import Widget
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.stencilview import StencilView
#from kivy.uix.slider import Slider
#from kivy.uix.button import Button
#from kivy.uix.dropdown import DropDown

from kivy.properties import (
    OptionProperty,
    NumericProperty,
    StringProperty,
    ListProperty,
    BooleanProperty,
)

# A Widget is the base building block
# of GUI interfaces in Kivy.
# It provides a Canvas that
# can be used to draw on screen.
from kivymd.uix.behaviors import TouchBehavior
from kivy.lang import Builder
from kivy.clock import Clock
import inspect

# From graphics module we are importing
# Rectangle and Color as they are
# basic building of canvas.
from kivy.graphics import Rectangle, Color, Line

num2color = [
    Color(0, 1, 0, mode="hsv"),  # black
    Color(0, 1, 1, mode="hsv"),  # red
    Color(30 / 360, 1, 1, mode="hsv"),  # orange
    Color(60 / 360, 1, 1, mode="hsv"),  # yellow
    Color(120 / 360, 1, 1, mode="hsv"),  # green
    Color(240 / 360, 1, 1, mode="hsv"),  # blue
    Color(300 / 360, 1, 1, mode="hsv"),  # violet
    Color(0, 0, 0.5, mode="hsv"),  # grey
    Color(0.5, 0.5, 0.5, mode="hsv"),  # brown
    Color(0, 0, 1, mode="hsv"),  # white
    Color(0, 1, 0, mode="hsv"),  # black
    Color(0, 1, 1, mode="hsv"),  # red
    Color(30 / 360, 1, 1, mode="hsv"),  # orange
    Color(60 / 360, 1, 1, mode="hsv"),  # yellow
    Color(120 / 360, 1, 1, mode="hsv"),  # green
    Color(240 / 360, 1, 1, mode="hsv"),  # blue
    Color(300 / 360, 1, 1, mode="hsv"),  # violet
    Color(0, 0, 0.5, mode="hsv"),  # grey
]

def color2rgba(c):
    # return [c.r,c.b,c.g,c.a]
    return [c.r, c.b, c.g, 1]

num2colorList = [color2rgba(c) for c in num2color]


from kivy.uix.gridlayout import GridLayout
class GridLayout(kivy.uix.gridlayout.GridLayout, sinode.Sinode):
    def __init__(self, **kwargs):
        sinode.Sinode.__init__(self, **kwargs)
        kivy.uix.gridlayout.GridLayout.__init__(self, **kwargs)


from kivy.uix.slider import Slider
class Slider(kivy.uix.slider.Slider, sinode.Leaf):
    def __init__(self, **kwargs):
        sinode.Leaf.__init__(self, parent=self.parent)
        kivy.uix.slider.Slider.__init__(self, **kwargs)
        self.register_event_type("on_release")

    def on_release(self):
        pass

    def on_touch_up(self, touch):
        kivy.uix.slider.Slider.on_touch_up(self,touch)
        if touch.grab_current == self:
            self.dispatch("on_release")
            return True

from kivy.uix.textinput import TextInput
class TextInput(kivy.uix.textinput.TextInput, sinode.Leaf):
    def __init__(self, **kwargs):
        sinode.Leaf.__init__(self)
        kivy.uix.textinput.TextInput.__init__(self, **kwargs)



class LabeledTextEntry(sinode.Sinode, kivy.uix.gridlayout.GridLayout):
    def __init__(self, **kwargs):
        kivy.uix.gridlayout.GridLayout.__init__(self, **kwargs)
        
        #self.attackTimeInput = TextInput(text=".002", multiline=False)
        #self.attackTimeInput.bind(on_text_validate=on_enter)
        #self.add_widget(Label(text="Attack Time (s)"))
        #self.add_widget(self.attackTimeInput)
        
        self.input = TextInput(**kwargs)
        self.input.bind(on_text_validate=on_enter)
        self.label = Label(text=text)
        self.add_widget(self.label)
        self.add_widget(self.input)
        
    
class LabeledSlider(kivy.uix.gridlayout.GridLayout, sinode.Sinode):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=2)
        sinode.Sinode.__init__(self, parent=self.parent)
        
        self.input = kivy.uix.slider.Slider(**kwargs)
        self.input.bind(on_text_validate=on_enter)
        self.label = Label(text=text)
        self.add_widget(self.label)
        self.add_widget(self.input)


from kivy.uix.label import Label
class Label(kivy.uix.label.Label, sinode.Leaf):
    def __init__(self, **kwargs):
        sinode.Leaf.__init__(self, parent=self.parent)
        kivy.uix.label.Label.__init__(self, **kwargs)


from kivy.uix.spinner import Spinner
class Spinner(kivy.uix.spinner.Spinner, sinode.Leaf):
    def __init__(self, **kwargs):
        sinode.Leaf.__init__(self, parent=self.parent)
        kivy.uix.spinner.Spinner.__init__(self, **kwargs)

from kivy.uix.treeview import TreeViewLabel
class TreeViewLabel(sinode.Leaf, kivy.uix.treeview.TreeViewLabel):
    def __init__(self, **kwargs):
        sinode.Sinode.__init__(self, **kwargs)
        kivy.uix.treeview.TreeViewLabel.__init__(self, **kwargs)

class TreeView(sinode.Sinode, kivy.uix.treeview.TreeView):
    def __init__(self, **kwargs):
        #sinode.Sinode.__init__(self, **kwargs)
        kivy.uix.treeview.TreeView.__init__(self, **kwargs)

    def populate(self, indict, parent=None):
        print(indict)
        # if the supplied "dictionary" is a SamplePatch, create a button for it
        if type(indict) is not dict:
            newNode = TreeViewButton(text=indict.displayName, size_hint_y=None)
            self.add_node(node = newNode, parent=parent )

            def mf_callback(instance):
                instance.toAbove("changePatch", {"patch": instance.patch})

            newNode.patch = indict
            newNode.bind(on_release=mf_callback)
            return

        # otherwise, create a recursive label
        for k, v in indict.items():
            newNode = TreeViewLabel(text=k, is_open=True, size_hint_y=None)

            self.populate(indict = v, parent=newNode) 
            if parent is None:
                self.add_node(node = newNode)
            else:
                self.add_node(node = newNode, parent=parent)

from kivy.uix.scrollview import ScrollView
class ScrollView(sinode.Sinode, kivy.uix.scrollview.ScrollView):
    def __init__(self, **kwargs):
        kivy.uix.scrollview.ScrollView.__init__(self, **kwargs)
        sinode.Sinode.__init__(self, **kwargs)


from kivy.uix.button import Button
class Button(sinode.Sinode, kivy.uix.button.Button):
    def __init__(self, **kwargs):
        kivy.uix.button.Button.__init__(self, **kwargs)
        sinode.Sinode.__init__(self, **kwargs)

class TreeViewButton(sinode.Sinode, kivy.uix.button.Button, kivy.uix.treeview.TreeViewNode):
    def __init__(self, **kwargs):
        sinode.Leaf.__init__(self, **kwargs)
        kivy.uix.treeview.TreeViewNode.__init__(self)
        kivy.uix.button.Button.__init__(self)


#class DragLabel(DragBehavior, kivy.uix.label.Label, kivy.uix.treeview.TreeViewNode):
#    pass

# This class is unused. You should use TreeView instead
#class RecursiveDropdown(DropDown):
#    def __init__(self, q, indict, mainButton, jpath=[]):
#        self.q = q
#        self.mainButton = mainButton
#        self.jpath = jpath
#        DropDown.__init__(self)
#
#        for k, v in indict.items():
#            if type(v) == dict:
#                print("FFFFUUUUU")
#                # patchDropdown = RecursiveDropdown(q=q, indict=v, mainButton=mainButton, jpath = jpath + [k])
#                openButton = Button(text=k)
#                # openButton.patchDropdown = patchDropdown
#                # openButton.bind(on_release=patchDropdown.open)
#                openButton.bind(on_release=self.printSelf)
#                self.add_widget(openButton)
#
#            else:
#                print("UUUCCCCKKKK")
#                print(k)
#                patchButton = Button(text=k)
#                patchButton.jpath = jpath + [k]
#
#                # for each button, attach a callback that will call the select() method
#                # on the dropdown. We'll pass the text of the button as the data of the
#                # selection.
#                patchButton.bind(
#                    on_release=lambda selectRecurse: self.selectRecurse(patchButton)
#                )
#                self.add_widget(patchButton)
#
#    def printSelf(self, patchButton):
#        print(patchButton)
#
#        ## default value shown
#        # text=patch.displayName,
#        ## available values
#        # values=([p.displayName for p in self.patches]),
#        # patchDropdown.index = i
#        # patchDropdown.bind(text=show_selected_value)



def guiFromDict(indict, parent):
    
    meta = indict["meta"]
    theclass = meta["klass"]
    print(theclass)
    node = theclass(**meta["kivy"])
    node.proc_kwargs(**meta)

    if "callbacks" in meta.keys():
        for k, v in meta["callbacks"].items():
            exec("node.bind("+k+"=v)")
    
    for k, v in indict.items():
        if k == "meta":
            continue

        if "count" in meta.keys:
            for i in range(meta["count"]):
                newChild = guiFromDict(v, node)
                node.add_widget(newChild)

        else:
            newChild = guiFromDict(v, node)
            node.add_widget(newChild)

    return node

class Point:
    def __init__(self, coords):
        self.x = coords[0]
        self.y = coords[1]
        self.coords = coords

    def move(self, coords):
        self.x = coords[0]
        self.y = coords[1]
        self.coords = coords

    def findNeighbors(self, points):
        self.leftwardPoint = points[0]
        self.rightwardPoint = points[-1]
        for p in points:
            if p.x < self.x:
                if (self.x - p.x) < (self.x - self.leftwardPoint.x):
                    self.leftwardPoint = p
            elif p.x > self.x:
                if (p.x - self.x) < (self.rightwardPoint.x - self.x):
                    self.rightwardPoint = p

    def closestPoint(self, points):
        closestPoint = points[0]
        for p in points:
            if abs(p.x - self.x) > abs(closestPoint.x - self.x):
                closestPoint = p
        return closestPoint

