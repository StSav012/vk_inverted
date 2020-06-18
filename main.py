#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
import json
import os.path
import time
import urllib.error
import urllib.request
from typing import List, Dict, Any, Final

from css_color_inverter import invert

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
    'variables',
    'common',
    'apps',
    'mail',
    'oauth_base',
    'photo',
    'video',
]

VK_ME_FILES: List[str] = [
    'vkme',
]

VK_APPS_FILES: List[str] = [
    # https://vk.com/covid19
    'https://prod-app7362610-29fb8e8c3f65.pages.vk-apps.com/static/css/5.f639b753.chunk.css',
    'https://prod-app7362610-29fb8e8c3f65.pages.vk-apps.com/static/css/main.5c3a01c8.chunk.css',
    # https://vk.com/home
    'https://stayhome.production.vklanding.com/_next/static/css/25b9e58df5e514472871.css',
]

VK_FORMS_FILES: List[str] = [
    # https://vk.com/stayhome
    'https://stayathome.w83.vkforms.ru/app/static/css/5.5f0214b7.chunk.css',
    'https://stayathome.w83.vkforms.ru/app/static/css/main.03c15dc9.chunk.css',
]

VK_CONNECT_FILES: List[str] = [
    # https://connect.vk.com/account/
    'https://connect.vk.com/account/static/bundle.0803443e.css',
]

OVERWRITE_FILES: bool = True
LOCAL_ONLY: bool = False

BRANCH: Final[str] = 'master'
NAME: Final[str] = f'Auto Dark VK ({BRANCH})' if BRANCH != 'master' else 'Auto Dark VK'


def md5(string):
    import hashlib
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


out_dict: Dict[str, Any] = {'enabled': True,
                            'name': NAME,
                            'updateUrl': f'https://github.com/StSav012/vk_inverted/raw/{BRANCH}/vk_inverted.css.json',
                            'md5Url': f'https://github.com/StSav012/vk_inverted/raw/{BRANCH}/vk_inverted.css.md5',
                            'url': 'https://github.com/StSav012/vk_inverted',
                            'sections': []}
out_lines: List[str] = [f'''\
/* ==UserStyle==
@name         {NAME}
@description  Mostly automatically created dark style for the desktop version of vk.com. Testing a new algorithm.
@namespace    github.com/stsav012/vk_inverted
@version      0.3.{time.strftime('%Y%m%d%H%M%S')}
@updateURL    https://github.com/StSav012/vk_inverted/raw/{BRANCH}/vk_inverted.user.css
==/UserStyle== */''']
for path in ('css/pages', 'css/landings', 'css/api', 'css/al', 'css', ):
    if not os.path.exists(path):
        d_path = ''
        for d in path.split('/'):
            d_path += d
            if not os.path.exists(d_path):
                os.mkdir(d_path)
            d_path += '/'
    for fn in FILES:
        filename: str = f'{path}/{fn}.css'
        if OVERWRITE_FILES and os.path.exists(filename):
            os.remove(filename)
        if not os.path.exists(filename):
            try:
                urllib.request.urlretrieve(f'https://vk.com/{filename}', filename)
            except urllib.error.HTTPError:
                continue
        if not os.path.exists(filename):
            print(f'failed to get {filename}')
            continue
        with open(filename, 'r') as f_in:
            print(f'processing {filename}', end=' ' * (20 - len(fn)), flush=True)
            inverted_css: str = invert(''.join(f_in.readlines()), url_root='https://vk.com')
            # remove properties starting from asterisk unsupported by Stylus add-on
            # remove lines containing “progid:DXImageTransform.Microsoft” unsupported by Stylus add-on
            inverted_css = '\n'.join(filter(lambda l: (not l.strip().startswith('*')
                                                       and 'progid:DXImageTransform.Microsoft' not in l),
                                            inverted_css.splitlines()))
            print(f'{inverted_css.count("}")} rules')
            if not inverted_css.strip('\n'):
                continue
            out_lines.append('@-moz-document domain("vk.com") {\n')
            section_css: str = f'/* auto generated from {filename} */\n' + inverted_css
            out_dict['sections'].append({'code': section_css, 'domains': ['vk.com']})
            out_lines.append(section_css)
            out_lines.append('}\n')

fn = 'vk_inverted_manual.css'
if os.path.exists(fn):
    with open(fn, 'r') as f_in:
        out_lines.append('@-moz-document domain("vk.com") {\n')
        manual_css = f_in.readlines()
        section_css: str = f'/*  manual part */\n' +\
                           ''.join(manual_css)
        out_dict['sections'].append({'code': section_css, 'domains': ['vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

path: str = 'css/mobile'
if not os.path.exists(path):
    d_path = ''
    for d in path.split('/'):
        d_path += d
        if not os.path.exists(d_path):
            os.mkdir(d_path)
        d_path += '/'
for fn in MOBILE_FILES:
    filename: str = f'{path}/{fn}.css'
    if OVERWRITE_FILES and os.path.exists(filename):
        os.remove(filename)
    if not os.path.exists(filename):
        try:
            urllib.request.urlretrieve(f'https://m.vk.com/{filename}', filename)
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(filename):
        print(f'failed to the get mobile version of {fn}.css')
        continue
    with open(filename, 'r') as f_in:
        print(f'processing {filename}', end=' ' * (20 - len(fn)), flush=True)
        inverted_css: str = invert(''.join(f_in.readlines()), url_root='https://m.vk.com')
        print(f'{inverted_css.count("}")} rules')
        if not inverted_css:
            continue
        # remove properties starting from asterisk unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("m.vk.com") {\n')
        section_css: str = f'/* auto generated from the mobile version of {fn}.css */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['m.vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for fn in VK_ME_FILES:
    filename: str = f'me.{fn}.css'
    if OVERWRITE_FILES and os.path.exists(filename):
        os.remove(filename)
    if not os.path.exists(filename):
        try:
            urllib.request.urlretrieve(f'https://vk.me/css/al/{fn}.css', filename)
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(filename):
        print(f'failed to {fn}.css from vk.me')
        continue
    with open(filename, 'r') as f_in:
        inverted_css: str = invert(''.join(f_in.readlines()), url_root='https://vk.me')
        if not inverted_css:
            continue
        # remove properties starting from asterisk unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("vk.me") {\n')
        section_css: str = f'/* auto generated from the {fn}.css from vk.me */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vk.me']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for path in VK_APPS_FILES:
    fn: str = path.rsplit('/', maxsplit=1)[-1]
    url_root: str = '/'.join(path.split('/')[:3]) + '/'
    filename: str = f'app.{fn.split(".")[0]}.css'
    if OVERWRITE_FILES and os.path.exists(filename):
        os.remove(filename)
    if not os.path.exists(filename):
        try:
            urllib.request.urlretrieve(path, filename)
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(filename):
        print(f'failed to get {path} from vk-apps.com')
        continue
    with open(filename, 'r') as f_in:
        inverted_css: str = invert(''.join(f_in.readlines()),
                                   url_root=url_root)
        if not inverted_css:
            continue
        # remove properties starting from asterisk unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("vk-apps.com") {\n')
        section_css: str = f'/* auto generated from the {fn}.css ' \
                           f'from {url_root} */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vk-apps.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for path in VK_FORMS_FILES:
    fn: str = path.rsplit('/', maxsplit=1)[-1]
    url_root: str = '/'.join(path.split('/')[:4]) + '/'
    filename: str = f'forms.{fn.split(".")[0]}.css'
    if OVERWRITE_FILES and os.path.exists(filename):
        os.remove(filename)
    if not os.path.exists(filename):
        try:
            urllib.request.urlretrieve(path, filename)
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(filename):
        print(f'failed to get {path} from vkforms.ru')
        continue
    with open(filename, 'r') as f_in:
        inverted_css: str = invert(''.join(f_in.readlines()),
                                   url_root=url_root)
        if not inverted_css:
            continue
        # remove properties starting from asterisk unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("vkforms.ru") {\n')
        section_css: str = f'/* auto generated from the {fn}.css ' \
                           f'of {url_root} */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['vkforms.ru']})
        out_lines.append(section_css)
        out_lines.append('}\n')

for path in VK_CONNECT_FILES:
    fn: str = path.rsplit('/', maxsplit=1)[-1]
    url_root: str = '/'.join(path.split('/')[:4]) + '/'
    filename: str = f'connect.{fn.split(".")[0]}.css'
    if OVERWRITE_FILES and os.path.exists(filename):
        os.remove(filename)
    if not os.path.exists(filename):
        try:
            urllib.request.urlretrieve(path, filename)
        except urllib.error.HTTPError:
            pass
    if not os.path.exists(filename):
        print(f'failed to get {path} from connect.vk.com')
        continue
    with open(filename, 'r') as f_in:
        inverted_css: str = invert(''.join(f_in.readlines()),
                                   url_root=url_root)
        if not inverted_css:
            continue
        # remove properties starting from asterisk unsupported by Stylus add-on
        inverted_css = '\n'.join(filter(lambda l: not l.strip().startswith('*'), inverted_css.splitlines()))
        out_lines.append('@-moz-document domain("connect.vk.com") {\n')
        section_css: str = f'/* auto generated from the {fn}.css ' \
                           f'of {url_root} */\n' + inverted_css
        out_dict['sections'].append({'code': section_css, 'domains': ['connect.vk.com']})
        out_lines.append(section_css)
        out_lines.append('}\n')

with open('vk_inverted.user.css', 'w') as f_out:
    f_out.write('\n'.join(out_lines))

with open('vk_inverted.css', 'w') as f_out:
    f_out.write('\n'.join(out_lines[1:]))

css_md5 = md5('\n'.join(out_lines[1:]))
with open('vk_inverted.css.json', 'w') as f_out:
    out_dict['originalMd5'] = css_md5
    json.dump(out_dict, f_out, indent='\t')
with open('vk_inverted.json', 'w') as f_out:
    out_dict['originalMd5'] = css_md5
    json.dump([out_dict], f_out, indent='\t')
with open('vk_inverted.css.md5', 'w') as f_out:
    f_out.write(css_md5)
