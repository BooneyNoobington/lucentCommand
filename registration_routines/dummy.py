#!/bin/env python3

def customRegister(**kwargs):
    print("It works!")

    print("Available keys are:")
    for k, v in kwargs.items():
        print("keyword argument: {} = {}".format(k, v))

