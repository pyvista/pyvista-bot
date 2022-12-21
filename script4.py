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
            print(obj)
            if inspect.isfunction(obj) or inspect.ismethod(obj):

                try:
                    source = inspect.getsource(obj)
                except OSError:
                    continue

                if func_name in source:
                    CALLERS.add(obj)

            elif inspect.isclass(obj) or inspect.ismodule(obj):
                # coverage recusive case
                if obj not in SEARCHED and 'pyvista' in str(obj):
                    _find_function_calls(obj, func_name, recursive)

    _find_function_calls(lib, func_name, recursive)

    return CALLERS


import importlib.util
import sys
import glob
import os

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
import pyvista


# identify function in pyvista
out = find_function_calls(pyvista, 'vtkStripper')
func = out.pop()
inspect.getsource(func)

# identify any tests that use this method
func_name = func.__name__

test_funcs = []
for test_mod in test_modules:
    funcs = find_function_calls(test_mod, func_name)
    
    # test_funcs.append(
