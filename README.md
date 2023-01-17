# sinode
simple importable node class

## installation  
```pip install git+https://github.com/julianfl0w/sinode/```

## Usage

## For Graphing

![The_Four_Paragraph_Essay](https://user-images.githubusercontent.com/8158655/213007806-793693df-c4e5-41a9-aa5e-4295db3210ba.png)

The following code exports a hierarchy to Dot notation, and renders it with GraphViz. Result above

```python 
# make sure to create "graph" directory

import sinode.sinode as sinode

fourParagraph = {
    "The Four Paragraph Essay": {
        "Introduction": {
            "Hook": {},
            "Bridge": {},
            "Thesis": {"Author": {}, "Title": {}, "Focus": {}, "Theme": {}},
        },
        # "(Methods)": {},
        "Evidence": {},
        "Analysis": {},
        "Conclusion": {
            "Reenforcing Arguements": {},
            "Effectiveness statement": {},
            "Universal Statement": {},
        },
        "meta": {
            "type": "lineage",
            "graphParams": {
                "rankdir": "LR",
                "style": "filled",
                "color": "lightgrey",
                "fillcolor": "\"darkgray:gold\"",
                "gradientangle": 0,
            },
            "boxParams": {
                "shape": "box",
                "color": "blue",
                "fillcolor": "\"yellow:green\"",
                "style": "filled",
                "gradientangle": 270,
            },
        },
    }
}

m = sinode.dict2node(fourParagraph)[0]
print(m.asList())
m.toGraphViz()
```

