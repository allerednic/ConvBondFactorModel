# -*- coding:utf-8 -*-

def api_checker(func):
    '''
    Function:
        Check if the api has responded successfully.
    '''
    def inner(*args, ** kwargs):
            