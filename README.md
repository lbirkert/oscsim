## oscsim

A physics based simulation game to play around with
oscillating things written in Python.

----

### Quickstart

0. (optional) setup python venv
```
$ python3 -m venv .venv
```
**Please use .venv/bin/python3 as <path/to/python3> if you choose to go with this route!**

1. Install the required dependencies
```
$ <path/to/python3> -m pip install -r requirements.txt
```

2. Launch the application
```
$ <path/to/python3> src/main.py
```

### Hacking Guide

#### Adding your own springs

`src/sim.py`
```py
class YourSpring(Spring):
    def __init__(self, stiffness: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness

    def magnitude(self, dist: float) -> float:
        # return the magnitude of the force, which the spring applies
        # if this is negative, the spring will push outwards instead of pull
        return math.exp(dist) / (dist ** 2) * self.stiffness
```

`src/main.py`
```py
springs = [
    ("constant", ConstantSpring),
    ("proportional", HookesSpring),
    ("quadratic", QuadraticSpring),
    ("hyperbolic", HyperbolicSpring),
    # we can use the hyperbolic spring's icon for now
    ("hyperbolic", YourSpring),
]
```

Now you can try it out and see how it behaves.

#### Custom icons

Paste `your_icon.png` into `imgs/`.

`src/main.py`
```py
springs = [
    ("constant", ConstantSpring),
    ("proportional", HookesSpring),
    ("quadratic", QuadraticSpring),
    ("hyperbolic", HyperbolicSpring),
    ("your_icon.png", YourSpring),
]
```

### Controls

#### Adding anchors

Pro-Tip: disable gravity or pause the simulation (space key) for easier handling of anchors

Hold and drag from the anchor icon on the bottom right corner
to spawn a new anchor at your cursor, which you can then drag around the scene.

Select at least two anchors and click on one of the spring icons in the bottom right
corner to connect these anchors with the given spring type.

key|function
--|--
space|show/hide settings menu
space|pause/resume simulation
right mouse button|navigate around the scene
right mouse button|select anchor
right mouse button|move anchor
right mouse button|end selection
shift|extend selection
backspace|delete selected
scroll wheel|zoom in/out


----

&copy; 2024 Lucas Birkert - All Rights Reserved
