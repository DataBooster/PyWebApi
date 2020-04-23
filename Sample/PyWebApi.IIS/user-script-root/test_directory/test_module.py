from datetime import datetime

def module_level_function(arg1:int, arg11, arg12, arg2:str='default', *, arg3:int=3.14, **kwargs)->str:
    s1 = int(arg1) * arg3
    print('arg1 * arg3 = {}'.format(s1))
    print('arg2 = {}'.format(arg2))
    print('**kwargs = {}'.format(kwargs))
    return {'result1':str(s1), 'current time': datetime.now(), 'other kws': kwargs}

test_var1 = 0.618

class test_class:
    pass