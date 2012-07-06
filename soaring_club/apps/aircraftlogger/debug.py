'''
Created on 30/mar/2009

@author: mauro
'''
import sys

debugToggle = 1
def debug_print(*values):
    if debugToggle == 0: return
    print >> sys.stderr, "DBG>", 
    for v in values: print >> sys.stderr,  v,
    print >> sys.stderr, '.'


def debug(func, *keys, **k):
    """prints the name,  input parameters and output of a function to 
       stdout."""

    #retrieve the names of functionarguments via reflection:
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    #retrieve the name of the function itself:
    fname = func.func_name

    def echo(*args, **kwargs):
        """instead of the original function, we return this echo function that 
        calls the original one. This way, we can add additional behaviour:"""

        #call the original function and store the result:
        result = func(*args, **kwargs)
        
        #create a string that explains input, e.g: a=5, b=6
        in_str = ', '.join('%s = %r' % entry
            for entry in zip(argnames,args) + kwargs.items())

        #print input and output:
        print "%s: Input: %s Output:%s"%(fname,in_str,result)
        return result
    #the function returned has the name 'echo'.
    #this is not very representative, so we rename it 
    # "<original function name> (debug echo)"
    echo.func_name = "%s (debug echo)"%func.func_name
    return echo

