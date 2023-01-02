import ast
from astunparse import unparse
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

            if inspect.isclass(obj):
                for item in obj.__mro__:
                    item_name = item.__name__
                    if func_name in item_name:
                        CALLERS.add(obj)
                else:
                    try:
                        source = inspect.getsource(obj)
                    except TypeError:
                        continue
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


def get_funcs(vtk_class_name, find_test=False):
    """Return any PyVista function and tests that uses the vtk_class_name."""
    # identify function in pyvista
    pv_funcs = find_function_calls(pyvista, vtk_class_name)
    if not len(pv_funcs):
        raise RuntimeError(
            f'Unable to locate any PyVista functions calling. {vtk_class_name}'
        )

    # exclude any __init__
    pv_funcs = [f for f in pv_funcs if f.__name__ != '__init__']

    # prioritize any classes that directly subclass the vtk class
    pv_func = None
    for obj in pv_funcs:
        if obj.__class__ is type and 'pyvista' in obj.__module__:
            if obj.__mro__[1].__name__.endswith(vtk_class_name):
                pv_func = obj
                break

    if pv_func is None:  # pick the obj containing containing the pyvista module
        for obj in pv_funcs:
            if 'pyvista' in obj.__module__ and obj.__class__ is not type:
                pv_func = obj
                break

    if pv_func is None:
        # simply get the first object using the pyvista module
        for obj in pv_funcs:
            if 'pyvista' in obj.__module__:
                pv_func = obj
                break

    if pv_func is None:
        raise RuntimeError(
            f'Unable to identify any pyvista functions containing {vtk_class_name}'
        )

    func_name = pv_func.__name__

    if not find_test:
        return pv_funcs, pv_func

    # identify any tests that use this method
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

    return pv_funcs, pv_func, test_funcs, test_func


def get_body(f, doc_string=False):
    """
    Get the body text of a function, i.e. without the signature.
    NOTE: Comments are stripped.
    """
    source = inspect.getsource(f)
    if f.__doc__ is None:
        return source
    doc = f.__doc__
    code = source.split(':',1)
    body = code[1].replace(doc, "")
    body = body.replace('""""""',"")  
    return code[0] + body

# example usage
# pv_funcs, pv_func, test_funcs, test_func = get_funcs('vtkAppendPolyData')
