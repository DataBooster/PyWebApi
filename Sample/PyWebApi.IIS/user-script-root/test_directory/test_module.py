
def module_level_function(arg1:int, arg11, arg12, arg2:str='default', *, arg3:int=3.14, **kwargs)->str:
    s1 = arg1 * arg3
    print('arg1 * arg3 = {}'.format(s1))
    print('arg2 = {}'.format(arg2))
    print('**kwargs = {}'.format(kwargs))
    return str(s1)

test_var1 = 0.618

class test_class:
    pass