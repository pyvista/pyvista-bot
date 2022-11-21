from vtk_info import get_cls_info
import openai
from key import API_KEY

openai.api_key = API_KEY


def get_src(vtk_info_in, vtk_info_out):
    gpt_prompt = f"""
Input:
{vtk_info_in['cls_name']}
{vtk_info_in['fnames']}

Output:
alg = _vtk.vtkStripper()
alg.SetInputDataObject(self)
alg.SetJoinContiguousSegments(join)
alg.SetMaximumLength(max_length)
alg.SetPassCellDataAsFieldData(pass_cell_data)
alg.SetPassThroughCellIds(pass_cell_ids)
alg.SetPassThroughPointIds(pass_point_ids)
_update_alg(alg, progress_bar, 'Stripping Mesh')
return _get_output(alg)

Input:
{vtk_info_out['cls_name']}
{vtk_info_out['fnames']}

Output:
"""

    src_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=gpt_prompt,
        temperature=0.5,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        # stop='\n\n',
        stop='Input:',
    )

    return src_response['choices'][0]['text']


def get_docstr(vtk_info_in, vtk_info_out, verbose=False):
    gpt_prompt = f'''
Input:
{vtk_info_in['cls_name']}
{vtk_info_in['short_desc']}
{vtk_info_in['long_desc']}
{vtk_info_in['fnames']}

Output:
def strip(
    self,
    join=False,
    max_length=1000,
    pass_cell_data=False,
    pass_cell_ids=False,
    pass_point_ids=False,
    progress_bar=False,
):
    """Strip poly data cells.

    Generates triangle strips and/or poly-lines from input
    polygons, triangle strips, and lines.

    Polygons are assembled into triangle strips only if they are
    triangles; other types of polygons are passed through to the
    output and not stripped. (Use ``triangulate`` filter to
    triangulate non-triangular polygons prior to running this
    filter if you need to strip all the data.) The filter will
    pass through (to the output) vertices if they are present in
    the input polydata.

    Also note that if triangle strips or polylines are defined in
    the input they are passed through and not joined nor
    extended. (If you wish to strip these use ``triangulate``
    filter to fragment the input into triangles and lines prior to
    running this filter.)

    This filter implements `vtkStripper
    <https://vtk.org/doc/nightly/html/classvtkStripper.html>`_

    Parameters
    ----------
    join : bool, optional
        If ``True``, the output polygonal segments will be joined
        if they are contiguous. This is useful after slicing a
        surface. The default is ``False``.

    max_length : int, optional
        Specify the maximum number of triangles in a triangle
        strip, and/or the maximum number of lines in a poly-line.

    pass_cell_data : bool, optional
        Enable/Disable passing of the CellData in the input to the
        output as FieldData. Note the field data is transformed.
        Default is ``False``.

    pass_cell_ids : bool, optional
        If ``True``, the output polygonal dataset will have a
        celldata array that holds the cell index of the original
        3D cell that produced each output cell. This is useful for
        picking. The default is ``False`` to conserve memory.

    pass_point_ids : bool, optional
        If ``True``, the output polygonal dataset will have a
        pointdata array that holds the point index of the original
        vertex that produced each output vertex. This is useful
        for picking. The default is ``False`` to conserve memory.

    progress_bar : bool, optional
        Display a progress bar to indicate progress.

    Returns
    -------
    pyvista.PolyData
        Stripped mesh.

    Examples
    --------
    >>> from pyvista import examples
    >>> mesh = examples.load_airplane()
    >>> slc = mesh.slice(normal='z', origin=(0, 0, -10))
    >>> stripped = slc.strip()
    >>> stripped.n_cells
    1
    >>> stripped.plot(show_edges=True, line_width=3)

    """

Input:
{vtk_info_out['cls_name']}
{vtk_info_out['short_desc']}
{vtk_info_out['long_desc']}
{vtk_info_out['fnames']}

Output:

'''

    if verbose:
        print(gpt_prompt)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=gpt_prompt,
        temperature=0.5,
        max_tokens=1024,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop='Input:',
    )

    text = response['choices'][0]['text']
    if verbose:
        print(text)
    return text

print('Acquiring VTK class definitions...')
vtk_info_in = get_cls_info('vtkStripper')
vtk_info_out = get_cls_info('vtkEllipseArcSource')

print('Querying OpenAI...')
docstr = get_docstr(vtk_info_in, vtk_info_out, verbose=True)
src = get_src(vtk_info_in, vtk_info_out)

fname = 'bane1.py'
with open(fname, 'w') as fid:
    fid.write('import vtk as _vtk\n')
    fid.write('from pyvista.core.filters import _get_output, _update_alg\n')
    fid.write(docstr)
    fid.write('\n')
    fid.write('\n'.join(['    ' + line for line in src.splitlines()]))

