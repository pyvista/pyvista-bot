import re
import requests
from bs4 import BeautifulSoup


def get_cls_info(class_name):
    url = f'https://vtk.org/doc/nightly/html/class{class_name}.html'
    req = requests.get(url)  #, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    soup.find(class_='textblock')
    tblock = soup.find(class_='textblock')
    details = tblock.getText()

    # just grab the first paragraph for now
    short_desc = details.split('\n')[0]
    long_desc = details.split('\n')[1]

    tags = soup.find_all(class_='memitem')

    fnames = {}
    for tag in tags:
        fd_name = re.compile('[a-zA-Z]+::[a-zA-Z]+')
        name = fd_name.findall(str(tag.find_all(class_='memname')))
        if name:
            cls, mth = name[0].split('::')
        if mth.endswith('On') or mth.endswith('Off'):
            continue
        if mth.startswith('Get'):
            continue
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

        des = tag.find(class_='memdoc').getText().strip()
        if 'Definition at line' in des:
            continue

        fnames[mth] = des

    fnames.pop(cls, None)

    return {
        'cls_name': cls,
        'short_desc': short_desc,
        'long_desc': long_desc,
        'fnames': fnames
    }
