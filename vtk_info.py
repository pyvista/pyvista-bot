"""
Scrape VTK class definitions from the doxygen documentation from:
https://vtk.org/doc/nightly/html

"""
import os
import re
import requests
import pickle

from bs4 import BeautifulSoup


fd_name = re.compile('[a-zA-Z0-9]+::[a-zA-Z]+')

def get_cls_info(class_name):

    # cache the soup
    cache_filename = os.path.join('vtk_info', f'{class_name}.p')
    if os.path.isfile(cache_filename):
        with open(cache_filename, 'rb') as fid:
            soup = BeautifulSoup(fid.read(), 'html.parser')
    else:
        url = f'https://vtk.org/doc/nightly/html/class{class_name}.html'
        req = requests.get(url)

        if req.status_code == 404:
            raise RuntimeError('The requested URL was not found on this server.')

        soup = BeautifulSoup(req.content, 'html.parser')
        with open(cache_filename, 'wb') as fid:
            fid.write(req.content)

    soup.find(class_='textblock')
    tblock = soup.find(class_='textblock')
    details = tblock.getText()

    # just grab the first paragraph for now
    short_desc = details.split('\n')[0]
    long_desc = details.split('\n')[1]

    tags = soup.find_all(class_='memitem')

    cls = class_name
    fnames = {}
    for tag in tags:
        name = fd_name.findall(str(tag.find_all(class_='memname')))

        # extract the class name from a method
        if len(name):
            _, mth = name[0].split('::')
        else:
            continue

        if mth.endswith('On') or mth.endswith('Off'):
            continue
        # if mth.startswith('Get'):
        #     continue
        if mth.startswith('PrintSelf'):
            continue
        if mth.startswith('New'):
            continue
        if mth.startswith('SafeDownCast'):
            continue
        if mth.startswith('IsTypeOf'):
            continue
        if mth.startswith('IsA'):
            continue
        if mth.startswith('RequestData'):
            continue
        if mth.startswith('FillInputPort'):
            continue
        if mth.startswith('Superclass'):
            continue

        des = tag.find(class_='memdoc').getText().strip()
        if 'Definition at line' in des:
            des = des.split('Definition at line')[0].strip()

        fnames[mth] = des

    fnames.pop(cls, None)

    return {
        'cls_name': cls,
        'short_desc': short_desc,
        'long_desc': long_desc,
        'fnames': fnames
    }
