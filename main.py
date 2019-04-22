#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
from typing import List, Dict, Any
import urllib.request
import urllib.error
import os.path
from css_color_inverter import invert
import time
import json
import hashlib

FILES: List[str] = [
    # 'aes_light',
    'apps',
    'article',
    'article_editor',
    'audio',
    'bookmarks',
    'common',
    'datepicker',
    'dev',
    'docs',
    'feed',
    'fonts_cnt',
    'groups',
    'im',
    'market',
    'module',
    'mrtarg',
    'notifier',
    'page',
    'page_help',
    'photos',
    'photos_add',
    'photoview',
    'post',
    'pretty_cards',
    'privacy',
    'profile',
    'public',
    'reports',
    'search',
    'settings',
    'stories',
    'tooltips',
    'ui_common',
    'ui_controls',
    'ui_gallery',
    'ui_media_selector',
    'video',
    'videocat',
    'videoplayer',
    'videoview',
    'wide_dd',
    'widget_post',
    'wk',
    'wk_editor',
    'wkview',
    'writebox',
]

MOBILE_FILES: List[str] = [
    'common',
]

OVERWRITE_FILES: bool = True
LOCAL_ONLY: bool = False


def md5(string):
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


out_dict: Dict[str, Any] = {'enabled': True,
                            'name': 'Auto Dark VK',
                            'updateUrl': 'https://github.com/StSav012/vk_inverted/raw/master/vk_inverted.css.json',
                            'md5Url': 'https://github.com/StSav012/vk_inverted/raw/master/vk_inverted.css.md5',
                            'url': 'https://github.com/StSav012/vk_inverted',
                            'sections': []}
out_lines: List[str] = [f'''\
/* ==UserStyle==
@name         Auto Dark VK
@description  Mostly automatically created dark style for the desktop version of vk.com. Testing a new algorithm.
@namespace    github.com/stsav012/vk_inverted
@version      0.2.{time.strftime('%Y%m%d%H%M%S')}
@updateURL    https://github.com/StSav012/vk_inverted/raw/master/vk_inverted.user.css
==/UserStyle== */''']
for fn in FILES:
    if OVERWRITE_FILES and os.path.exists(f'{fn}.css'):
        os.remove(f'{fn}.css')
    if not os.path.exists(f'{fn}.css'):
        try:
            urllib.request.urlretrieve(f'https://vk.com/css/al/{fn}.css', f'{fn}.css')
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(f'{fn}.css'):
        try:
            urllib.request.urlretrieve(f'https://vk.com/css/{fn}.css', f'{fn}.css')
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(f'{fn}.css'):
        print(f'failed to get {fn}.css')
        continue
    with open(f'{fn}.css', 'r') as fin:
        print(f'processing {fn}.css', end=' ' * (20 - len(fn)), flush=True)
        inverted_css: str = invert(''.join(fin.readlines()))
        # remove properties starting from asterix unsupported by Stylus add-on
        # remove lines containing “progid:DXImageTransform.Microsoft” unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: (not l.strip().startswith('*')
                                                   and 'progid:DXImageTransform.Microsoft' not in l),
                                        inverted_css.splitlines()))
        print(f'{inverted_css.count("}")} rules')
        if not inverted_css.strip('\n'):
            continue
        out_lines.append('@-moz-document domain("vk.com") {\n')
        section_css: str = f'/* auto generated from {fn}.css */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

fn = 'vk_inverted_manual.css'
if os.path.exists(fn):
    with open(fn, 'r') as fin:
        out_lines.append('@-moz-document domain("vk.com") {\n')
        manual_css = fin.readlines()
        section_css: str = f'/*  manual part */\n' +\
                           ''.join(manual_css)
        out_dict['sections'].append({'code': section_css, 'domains': ['vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for fn in MOBILE_FILES:
    # FIXME: getting wrong file
    # if not os.path.exists(f'm.{fn}.css'):
    #     try:
    #         urllib.request.urlretrieve(f'https://m.vk.com/css/mobile/{fn}.css', f'm.{fn}.css')
    #     except urllib.error.HTTPError:
    #         pass
    if not os.path.exists(f'm.{fn}.css'):
        print(f'failed to the get mobile version of {fn}.css')
        continue
    with open(f'm.{fn}.css', 'r') as fin:
        inverted_css: str = invert(''.join(fin.readlines()))
        if not inverted_css:
            continue
        # remove properties starting from asterix unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("m.vk.com") {\n')
        section_css: str = f'/* auto generated from the mobile version of {fn}.css */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['m.vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

with open('vk_inverted.user.css', 'w') as fout:
    fout.write('\n'.join(out_lines))

with open('vk_inverted.css', 'w') as fout:
    fout.write('\n'.join(out_lines[1:]))

css_md5 = md5('\n'.join(out_lines[1:]))
with open('vk_inverted.css.json', 'w') as fout:
    out_dict['originalMd5'] = css_md5
    json.dump(out_dict, fout, indent='\t')
with open('vk_inverted.json', 'w') as fout:
    out_dict['originalMd5'] = css_md5
    json.dump([out_dict], fout, indent='\t')
with open('vk_inverted.css.md5', 'w') as fout:
    fout.write(css_md5)
