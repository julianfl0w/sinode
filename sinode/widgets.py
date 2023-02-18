from . import sinode

import kivy.uix as uix
#from uix.floatlayout import FloatLayout
#from uix.gridlayout import GridLayout
#from uix.textinput import TextInput
#from uix.label import Label
#from uix.treeview import TreeView
#from uix.treeview import TreeViewNode
#from uix.treeview import TreeViewLabel
#from uix.scrollview import ScrollView
#from uix.behaviors import DragBehavior
#from uix.widget import Widget
#from uix.boxlayout import BoxLayout
#from uix.stencilview import StencilView
#from uix.slider import Slider
#from uix.spinner import Spinner
#from uix.button import Button
#from uix.dropdown import DropDown

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

num2colorList = [color2rgba(c) for c in num2color]



class Slider(uix.slider.Slider, sinode.Sinode):
    def __init__(self, **kwargs):
        sinode.Sinode.__init__(self, parent=self.parent)
        self.register_event_type("on_release")
        uix.slider.Slider.__init__(self, **kwargs)

    def on_release(self):
        pass

    def on_touch_up(self, touch):
        super(ModifiedSlider, self).on_touch_up(touch)
        if touch.grab_current == self:
            self.dispatch("on_release")
            return True

class TextInput(uix.textinput.TextInput, sinode.Sinode):
    def __init__(self, **kwargs):
        sinode.Sinode.__init__(self, **kwargs)
        uix.textinput.TextInput.__init__(self, **kwargs)

class TreeViewLabel(sinode.Sinode, uix.treeviewlabel.TreeViewLabel):
    def __init__(self, **kwargs):
        sinode.Sinode.__init__(self, **kwargs)
        TreeViewLabel.__init__(self, **kwargs)

class LabeledTextEntry(sinode.Sinode, uix.gridview.GridView):
    def __init__(self, **kwargs):
        sinode.Sinode.__init__(self, **kwargs)
        uix.gridview.GridView.__init__(self, **kwargs)
        
        #self.attackTimeInput = TextInput(text=".002", multiline=False)
        #self.attackTimeInput.bind(on_text_validate=on_enter)
        #self.add_widget(Label(text="Attack Time (s)"))
        #self.add_widget(self.attackTimeInput)
        
        self.input = TextInput(**kwargs)
        self.input.bind(on_text_validate=on_enter)
        self.label = Label(text=text)
        self.add_widget(self.label)
        self.add_widget(self.input)
        
    
class LabeledSlider(uix.gridview.GridView, sinode.Sinode):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=2)
        sinode.Sinode.__init__(self, parent=self.parent)
        
        self.input = uix.slider.Slider(**kwargs)
        self.input.bind(on_text_validate=on_enter)
        self.label = Label(text=text)
        self.add_widget(self.label)
        self.add_widget(self.input)



class TreeView(sinode.Sinode, uix.treeview.TreeView):
    def __init__(self, **kwargs):
        TreeView.__init__(self, **kwargs)
        sinode.Sinode.__init__(self, **kwargs)

    def populate(self, indict, path=[]):
        
        # if the supplied "dictionary" is a SamplePatch, create a button for it
        if isinstance(indict, SamplePatch):
            newNode = SinodeTreeViewButton(text=indict.displayName, size_hint_y=None, parent = self)
            self.add_node(newNode, self.parent)

            def mf_callback(instance):
                instance.toAbove("loadPatch", {"patch": instance.patch})

            newNode.patch = indict
            newNode.bind(on_release=mf_callback)
            return

        # otherwise, create a recursive label
        for k, v in indict.items():
            if self.parent is None:
                newNode = TreeViewLabel(text=k, is_open=False, size_hint_y=None)
            else:
                newNode = TreeViewLabel(
                    text=k, is_open=False, size_hint_y=None, parent=self.parent
                )
            self.add_node(newNode)
            newNode.populate(self, tree_node, v, path=path + [k])


class ScrollView(sinode.Sinode, ScrollView):
    def __init__(self, **kwargs):
        uix.scrollview.ScrollView.__init__(self, **kwargs)
        sinode.Sinode.__init__(self, **kwargs)


class TreeViewButton(sinode.Sinode, Button, uix.treeview.TreeViewNode):
    def __init__(self, **kwargs):
        uix.treeview.TreeViewNode.__init__(self)
        Button.__init__(self)
        sinode.Sinode.__init__(self, **kwargs)


class DragLabel(DragBehavior, uix.label.Label, uix.treeview.TreeViewNode):
    pass

# This class is unused. You should use TreeView instead
class RecursiveDropdown(DropDown):
    def __init__(self, q, indict, mainButton, jpath=[]):
        self.q = q
        self.mainButton = mainButton
        self.jpath = jpath
        DropDown.__init__(self)

        for k, v in indict.items():
            if type(v) == dict:
                print("FFFFUUUUU")
                # patchDropdown = RecursiveDropdown(q=q, indict=v, mainButton=mainButton, jpath = jpath + [k])
                openButton = Button(text=k)
                # openButton.patchDropdown = patchDropdown
                # openButton.bind(on_release=patchDropdown.open)
                openButton.bind(on_release=self.printSelf)
                self.add_widget(openButton)

            else:
                print("UUUCCCCKKKK")
                print(k)
                patchButton = Button(text=k)
                patchButton.jpath = jpath + [k]

                # for each button, attach a callback that will call the select() method
                # on the dropdown. We'll pass the text of the button as the data of the
                # selection.
                patchButton.bind(
                    on_release=lambda selectRecurse: self.selectRecurse(patchButton)
                )
                self.add_widget(patchButton)

    def printSelf(self, patchButton):
        print(patchButton)

        ## default value shown
        # text=patch.displayName,
        ## available values
        # values=([p.displayName for p in self.patches]),
        # patchDropdown.index = i
        # patchDropdown.bind(text=show_selected_value)

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

def color2rgba(c):
    # return [c.r,c.b,c.g,c.a]
    return [c.r, c.b, c.g, 1]


def guiFromDict(indict, parent):
    
    meta = indict["meta"]
    meta["parent"] = parent
    node = meta["class"](meta)
    for k, v in indict.items():
        if k == "meta":
            continue
        
        node.children += guiFromDict(v, self)

