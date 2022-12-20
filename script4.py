import inspect

SEARCHED = set()
CALLERS = set()


def find_function_calls(lib, func_name):
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

        elif inspect.isclass(obj) or inspect.ismodule(obj):
            # coverage recusive case
            if obj not in SEARCHED and 'pyvista' in str(obj):
                find_function_calls(obj, func_name)


# Example usage
import pyvista

find_function_calls(pyvista, 'vtkStripper')

