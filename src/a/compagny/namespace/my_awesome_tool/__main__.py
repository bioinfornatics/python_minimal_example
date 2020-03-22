from os import path
import sys
from pathlib import Path
from colorama import init
from typing import Dict

app_name = 'my_awesome_tool'


def get_fhs() -> Dict[str, Path]:
    nb_dirs_in_namespace = __name__.count('.')
    namespace_path = Path(path.dirname(path.abspath( __file__ )))
    site_packages = namespace_path.parent
    for i in range(0, nb_dirs_in_namespace - 1):
        site_packages = site_packages.parent
    python_lib_dir = site_packages.parent
    lib_dir = python_lib_dir.parent
    prefix_dir = lib_dir.parent
    bin_dir = prefix_dir / 'bin'
    conf_dir = prefix_dir / 'etc'
    share_dir = prefix_dir / 'share'
    
    return {
        'prefix':  prefix_dir,
        'bin': bin_dir,
        'lib': lib_dir,
        'etc': conf_dir,
        'share': share_dir
    }


def display_banner(app_share_dir: Path):
    init(autoreset=True)
    banner_lines = None
    banner_path = app_share_dir / 'banner.ansi'
    with open(str(banner_path), encoding='unicode-escape') as f:
        banner_lines = f.readlines()
    for line in banner_lines:
        print(fr'{line}')


def main():
    fhs = get_fhs()
    app_share_dir = fhs["share"] / app_name
    display_banner(app_share_dir)
    print('Hello!')
    print(f'''
Directories:
prefix    : {fhs["prefix"]}
bin       : {fhs["bin"]}
share     : {fhs["share"]}
app_share : {app_share_dir}
    ''')
