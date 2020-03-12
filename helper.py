import json
import os
import re

import cssutils
import requests
from lxml import etree


def class2score(s):
    # get num from str
    regex = r"\d+"
    score = int(re.search(regex, s).group())
    return '%.1f' % (score / 10)


def get_css(css_url):
    # css file already loaded
    if os.path.exists(f'./svg_info/{hash(css_url)}.dat'):
        print('load from existing')
        with open(f'./svg_info/{hash(css_url)}.dat', 'r') as f:
            js = f.read()
            dic = json.loads(js)
            return dic

    print('load from new')
    css = requests.get(css_url).text

    css_dct = {}
    sheet = cssutils.parseString(css)
    svg_dct = {}
    for rule in sheet:
        selector = rule.selectorText
        styles = rule.style.cssText
        if '=' in selector:
            svg_dct[selector] = styles
        else:
            css_dct[selector] = styles
    # 将坐标与值对应
    pre_fix_re = r"\"([a-z]+)\""
    tmp = {}
    for k, v in svg_dct.items():
        _dct = {}
        for info in v.split('\n'):
            detail = info.split(':')
            _dct[detail[0]] = detail[1].strip().replace('"', '')

        key = re.search(pre_fix_re, k).group()
        tmp[key.replace('"', '')[:2]] = _dct
    svg_dct = tmp
    _mapping = {}
    for key, value in svg_dct.items():
        url = value['background-image'].replace('url(//', '').replace(');', '')
        html = etree.HTML(bytes(requests.get(f'https://{url}').text, 'utf-8'))
        result = html.xpath('//text')
        x = 0
        for txt in result:
            y = txt.attrib['y']
            for c in txt.text:
                _mapping[f'{key},{x},{y}'] = c
                x += 1
            x = 0
    _tmp = {}
    for key, value in css_dct.items():
        index_re = r'.+?(\d+).+?(\d+).+'
        x, y = re.search(index_re, value).groups()
        x = int(abs(int(x)) / 14)
        y = abs(int(y)) + int(svg_dct[key[1:3]]['height'][:2]) - 1
        try:
            _tmp[key[1:]] = _mapping[f'{key[1:3]},{x},{y}']
        except KeyError:
            # 干扰项目 跳过
            pass
    js_obj = json.dumps(_tmp)

    with open(f'./svg_info/{hash(css_url)}.dat', 'w') as f:
        f.write(js_obj)

    return _tmp
