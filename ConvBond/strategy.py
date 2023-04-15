#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Author: c.s.yang
Updated : 20220911
Function:
    define the signal class
    and the signal test methods
'''
import numbers
import numpy as np
import pandas as pd
from datetime import date, datetime
from abc import ABC, abstractmethod
# from .dataloader import DataLoader
from .lib.utils import *

import pandas_bokeh
import seaborn as sns
import matplotlib.pyplot as plt
from copy import deepcopy
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import  column
from bokeh.io import output_notebook
from bokeh.resources import  INLINE
output_notebook(INLINE)