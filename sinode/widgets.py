from . import sinode

import kivy.uix as uix
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
#from kivy.uix.spinner import Spinner
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


# From graphics module we are importing
# Rectangle and Color as they are
# basic building of canvas.
from kivy.graphics import Rectangle, Color, Line


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

class TreeViewLabel(sinode.Sinode, TreeViewLabel):
    def __init__(self, **kwargs):
        TreeViewLabel.__init__(self, **kwargs)
        sinode.Sinode.__init__(self, **kwargs)


class TreeView(sinode.Sinode, TreeView):
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
        kivy.uix.scrollview.ScrollView.__init__(self, **kwargs)
        sinode.Sinode.__init__(self, **kwargs)


class TreeViewButton(sinode.Sinode, Button, kivy.uix.treeview.TreeViewNode):
    def __init__(self, **kwargs):
        kivy.uix.treeview.TreeViewNode.__init__(self)
        Button.__init__(self)
        sinode.Sinode.__init__(self, **kwargs)


class DragLabel(DragBehavior, kivy.uix.label.Label, kivy.uix.treeview.TreeViewNode):
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
