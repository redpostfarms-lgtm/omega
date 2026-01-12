# Sample code with issues for testing
import os
from some_module import *

global_variable = "bad"

def badFunctionName():
    x = 1
    if x > 0:
        if x < 10:
            if x == 5:
                if x != 3:
                    return "too nested"
    return "done"

class badClassName:
    def method(self):
        very_long_line_that_exceeds_the_maximum_recommended_line_length_and_should_be_split_into_multiple_lines = "example"
        pass
