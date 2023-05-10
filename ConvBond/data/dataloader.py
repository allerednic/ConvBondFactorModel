# -*- coding: utf-8 -*- 


import pandas as pd
from sqlalchemy import create_engine

class DataLoader(object):
    
    def __init__(self, database, filed=None):
        self.database = database
        