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
    'addresses',
    'aes_light',
    'apps',
    'apps_feed_blocks',
    'article',
    'article_editor',
    'audio',
    'base',
    'board',
    'bookmarks',
    'common',
    'datepicker',
    'dev',
    'docs',
    'feed',
    'fonts_cnt',
    'fonts_utf',
    'graffiti_new',
    'groups',
    'im',
    'index',
    'join',
    'language',
    'login',
    'market',
    'module',
    'mrtarg',
    'notifier',
    'ny_2020',
    'oauth_popup',
    'owner_photo',
    'page',
    'page_help',
    'pages',
    'photo_editor',
    'photos',
    'photos_add',
    'photoview',
    'play_safe_at_home',
    'post',
    'pretty_cards',
    'privacy',
    'products',
    'profile',
    'public',
    'reports',
    'restore',
    'search',
    'settings',
    'stories',
    'tickets',
    'tooltips',
    'top_logo',
    'transparency',
    'ui_common',
    'ui_controls',
    'ui_gallery',
    'ui_media_selector',
    'video',
    'video_edit',
    'videocat',
    # 'videoplayer',  # is it needed at all? it's overloaded manually anyway
    'videoview',
    'wide_dd',
    'widget_post',
    'wiki',
    'wk',
    'wk_editor',
    'wkview',
    'writebox',
]

MOBILE_FILES: List[str] = [
    'common',
]

VK_ME_FILES: List[str] = [
    'vkme',
]

VK_APPS_FILES: List[str] = [
    'https://prod-app7362610-94b36b33bcd1.pages.vk-apps.com/static/css/5.f639b753.chunk.css',
    'https://prod-app7362610-94e6b785785f.pages.vk-apps.com/static/css/main.28d79a88.chunk.css',
    # https://vk.com/home
    'https://stayhome.juice.vk-apps.com/_next/static/css/391e853485aaddf3ed73.css',
]

VK_FORMS_FILES: List[str] = [
    # https://vk.com/stayhome
    'https://stayathome.w83.vkforms.ru/app/static/css/5.5f0214b7.chunk.css',
    'https://stayathome.w83.vkforms.ru/app/static/css/main.9530138d.chunk.css'
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
@version      0.3.{time.strftime('%Y%m%d%H%M%S')}
@updateURL    https://github.com/StSav012/vk_inverted/raw/master/vk_inverted.user.css
==/UserStyle== */''']
for path in ('css', 'css/al', 'css/api', 'css/landings', 'css/pages'):
    if not os.path.exists(path):
        d_path = ''
        for d in path.split('/'):
            d_path += d
            if not os.path.exists(d_path):
                os.mkdir(d_path)
            d_path += '/'
    for fn in FILES:
        if OVERWRITE_FILES and os.path.exists(f'{path}/{fn}.css'):
            os.remove(f'{path}/{fn}.css')
        if not os.path.exists(f'{path}/{fn}.css'):
            try:
                urllib.request.urlretrieve(f'https://vk.com/{path}/{fn}.css', f'{path}/{fn}.css')
            except urllib.error.HTTPError:
                continue
        if not os.path.exists(f'{path}/{fn}.css'):
            print(f'failed to get {path}/{fn}.css')
            continue
        with open(f'{path}/{fn}.css', 'r') as fin:
            print(f'processing {path}/{fn}.css', end=' ' * (20 - len(fn)), flush=True)
            inverted_css: str = invert(''.join(fin.readlines()), url_root='https://vk.com')
            # remove properties starting from asterisk unsupported by Stylus add-on
            # remove lines containing “progid:DXImageTransform.Microsoft” unsupported by Stylus add-on
            inverted_css = '\n'.join(filter(lambda l: (not l.strip().startswith('*')
                                                       and 'progid:DXImageTransform.Microsoft' not in l),
                                            inverted_css.splitlines()))
            print(f'{inverted_css.count("}")} rules')
            if not inverted_css.strip('\n'):
                continue
            out_lines.append('@-moz-document domain("vk.com") {\n')
            section_css: str = f'/* auto generated from {path}/{fn}.css */\n' + inverted_css
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
        inverted_css: str = invert(''.join(fin.readlines()), url_root='https://m.vk.com')
        if not inverted_css:
            continue
        # remove properties starting from asterix unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("m.vk.com") {\n')
        section_css: str = f'/* auto generated from the mobile version of {fn}.css */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['m.vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for fn in VK_ME_FILES:
    if not os.path.exists(f'me.{fn}.css'):
        try:
            urllib.request.urlretrieve(f'https://vk.me/css/al/{fn}.css', f'me.{fn}.css')
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(f'me.{fn}.css'):
        print(f'failed to {fn}.css from vk.me')
        continue
    with open(f'me.{fn}.css', 'r') as fin:
        inverted_css: str = invert(''.join(fin.readlines()), url_root='https://vk.me')
        if not inverted_css:
            continue
        # remove properties starting from asterix unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("vk.me") {\n')
        section_css: str = f'/* auto generated from the {fn}.css of vk.me*/\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vk.me']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for path in VK_APPS_FILES:
    fn: str = path.rsplit('/', maxsplit=1)[-1]
    url_root: str = '/'.join(path.split('/')[:3]) + '/'
    if not os.path.exists(f'app.{fn.split(".")[0]}.css'):
        try:
            urllib.request.urlretrieve(path,
                                       f'app.{fn.split(".")[0]}.css')
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(f'app.{fn.split(".")[0]}.css'):
        print(f'failed to get {path} from vk-apps.com')
        continue
    with open(f'app.{fn.split(".")[0]}.css', 'r') as fin:
        inverted_css: str = invert(''.join(fin.readlines()),
                                   url_root=url_root)
        if not inverted_css:
            continue
        # remove properties starting from asterix unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("vk-apps.com") {\n')
        section_css: str = f'/* auto generated from the {fn}.css ' \
                           f'of {url_root} */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vk-apps.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for path in VK_FORMS_FILES:
    fn: str = path.rsplit('/', maxsplit=1)[-1]
    url_root: str = '/'.join(path.split('/')[:4]) + '/'
    if not os.path.exists(f'forms.{fn.split(".")[0]}.css'):
        try:
            urllib.request.urlretrieve(path,
                                       f'forms.{fn.split(".")[0]}.css')
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(f'forms.{fn.split(".")[0]}.css'):
        print(f'failed to get {path} from vkforms.ru')
        continue
    with open(f'forms.{fn.split(".")[0]}.css', 'r') as fin:
        inverted_css: str = invert(''.join(fin.readlines()),
                                   url_root=url_root)
        if not inverted_css:
            continue
        # remove properties starting from asterix unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("vkforms.ru") {\n')
        section_css: str = f'/* auto generated from the {fn}.css ' \
                           f'of {url_root} */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vkforms.ru']})
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
