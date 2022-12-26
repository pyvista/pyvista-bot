import importlib.util
import sys
import glob
import os
from tqdm import tqdm
import pyvista
import os
import inspect

def find_function_calls(lib, func_name, recursive=True):
    SEARCHED = set()
    CALLERS = set()

    def _find_function_calls(lib, func_name, recursive=True):
        """
        Finds all functions in a library that call a certain function
        :param lib: The library to search
        :param func_name: The function to search for
        :return: A list of functions that call the specified function
        """
        SEARCHED.add(lib)
        for _, obj in inspect.getmembers(lib):
            if inspect.isfunction(obj) or inspect.ismethod(obj):

                try:
                    source = inspect.getsource(obj)
                except OSError:
                    continue

                if func_name in source:
                    CALLERS.add(obj)

            if recursive:
                if inspect.isclass(obj) or inspect.ismodule(obj):
                    # cover recusive case
                    if obj not in SEARCHED and 'pyvista' in str(obj):
                        _find_function_calls(obj, func_name, recursive)

    _find_function_calls(lib, func_name, recursive)

    return list(CALLERS)


# load tests as modules
TEST_PATH = os.path.expanduser('~/python/pyvista/tests/**.py')
test_files = glob.glob(TEST_PATH, recursive=True)

test_modules = []
for test_file in test_files:
    mod_name = os.path.basename(test_file).split('.')[0]
    spec = importlib.util.spec_from_file_location(mod_name, test_file)
    mod = importlib.util.module_from_spec(spec)
    test_modules.append(mod)
    spec.loader.exec_module(mod)

# Example usage


vtk_class = 'vtkAppendPolyData'

# identify function in pyvista
out = find_function_calls(pyvista, vtk_class)
pv_func = out[0]

# identify any tests that use this method
func_name = pv_func.__name__


test_funcs = []
for test_mod in test_modules:
    funcs = find_function_calls(test_mod, func_name, recursive=False)
    for func in funcs:
        if func.__name__.startswith('test_'):
            test_funcs.append(func)

if not len(test_funcs):
    raise RuntimeError(f'Unable to locate test for {func_name}')

# prioritize the test whose name includes the function
ideal_name = f'test_{pv_func.__name__}'

test_func = None
for func in test_funcs:
    if ideal_name == func.__name__:
        test_func = func

if test_func is None:
    for func in test_funcs:
        if ideal_name in func.__name__:
            test_func = func

if test_func is None:
    test_func = test_funcs[0]


return pv_func, test_func

