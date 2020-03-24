import json
import os
import re

import cssutils
import requests
import xml.etree.ElementTree as ET


def class2score(s):
    # get num from str
    regex = r"\d+"
    score = int(re.search(regex, s).group())
    return "%.1f" % (score / 10)


def get_css(css_url):
    # css file already loaded
    if os.path.exists(f"./svg_info/{hash(css_url)}.dat"):
        print("load from existing")
        with open(f"./svg_info/{hash(css_url)}.dat", "r") as f:
            js = f.read()
            dic = json.loads(js)
            return dic

    print("load from new")
    css = requests.get(css_url).text

    css_dct = {}
    sheet = cssutils.parseString(css)
    svg_dct = {}
    for rule in sheet:
        selector = rule.selectorText
        styles = rule.style.cssText
        if "=" in selector:
            svg_dct[selector] = styles
        else:
            css_dct[selector] = styles
    # 将坐标与值对应
    pre_fix_re = r"\"([a-z]+)\""
    tmp = {}
    for k, v in svg_dct.items():
        _dct = {}
        for info in v.split("\n"):
            detail = info.split(":")
            _dct[detail[0]] = detail[1].strip().replace('"', "")

        key = re.search(pre_fix_re, k).group()
        tmp[key.replace('"', "")[:2]] = _dct
    svg_dct = tmp
    _mapping = {}
    for key, value in svg_dct.items():
        url = value["background-image"].replace("url(//", "").replace(");", "")
        page = requests.get(f"https://{url}").text
        tree = ET.fromstring(page)
        reference = []
        tag = tree.tag[:tree.tag.find('}') + 1]
        # 获取 Y 值
        paths = tree.findall(f'./{tag}defs/{tag}path')
        for path in paths:
            y = re.findall(r" (\d+) ", path.attrib['d'])[0]
            reference.append(y)

        text_paths = tree.findall(f'./{tag}text/{tag}textPath')
        count = 0
        x = 0
        for t in text_paths:
            y = reference[count]
            count += 1
            for c in t.text:
                _mapping[f"{key},{x},{y}"] = c
                x += 1
            x = 0
    _tmp = {}
    for key, value in css_dct.items():
        index_re = r".+?(\d+).+?(\d+).+"
        x, y = re.search(index_re, value).groups()
        x = int(abs(int(x)) / 14)
        y = abs(int(y)) + int(svg_dct[key[1:3]]["height"][:2]) - 1
        try:
            _tmp[key[1:]] = _mapping[f"{key[1:3]},{x},{y}"]
        except KeyError:
            # 干扰项目 跳过
            pass
    js_obj = json.dumps(_tmp)

    with open(f"./svg_info/{hash(css_url)}.dat", "w") as f:
        f.write(js_obj)

    return _tmp


if __name__ == "__main__":
    get_css(
        "http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/5731cfa5230095344e879b4622796f0b.css"
    )
