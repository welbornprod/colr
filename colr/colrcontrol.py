#!/usr/bin/env python3

""" colr/colrcontrol.py
    The ColrControl object, a mix of Colr and Control.
    Documentation would be the same as Colr/Control.
    -Christopher Welborn 05-23-2019
"""
from typing import (
    Optional,
)
from .colr import (
    Colr,
    ColorArg,
)
from .controls import (
    Control,
)


class ColrControl(Colr, Control):
    """ A Colr that also has all the methods of a Control object.
        Documentation for the methods will be found on the subclass they come
        from (Colr or Control).
    """
    def __init__(
            self,
            text: Optional[str] = None,
            fore: Optional[ColorArg] = None,
            back: Optional[ColorArg] = None,
            style: Optional[str] = None,
            no_closing: Optional[bool] = False) -> None:
        """ Initialize a ColrControl object with text and color options.
            This is the same __init__ method as Colr.__init__.
        """
        Colr.__init__(
            self,
            text=text,
            fore=fore,
            back=back,
            style=style,
            no_closing=no_closing,
        )
