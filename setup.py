import shutil
import subprocess
from distutils.command.clean import clean
from glob import glob
from os import path, walk, remove

from typing import List

from setuptools import setup, Command, find_namespace_packages
from setuptools.config import read_configuration


def get_files(directory: str) -> List[str]:
    results = []
    items=[ (root, files) for root, dirs, files in walk('resources') if len(files) > 0]
    for root_files in items:
        root, files = root_files
        for f in files:
            results.append(path.join(root, f))
    return results


class ExtendedClean(clean):
    """
    This class extend clean command in order to remove all __pycache__ directories.
    Indeed these directories contains pre-computed file with module path write in
    unix or windows style. Depends of latest os which build the file.
    In multi-OS environment this could lead to strange behavior.
    """

    @staticmethod
    def _find_all_directories(dir_name: str, path_to_scan: str) -> List[str]:
        result = []
        for root, dirs, files in walk(path_to_scan):
            if dir_name in dirs:
                result.append(path.join(root, dir_name))
        return result

    def run(self) -> None:
        clean.run(self)
        c = clean(self.distribution)
        c.finalize_options()
        c.run()
        # sources directories
        for directory in self.distribution.package_dir.values():
            for file_path in self._find_all_directories('__pycache__', directory):
                shutil.rmtree(file_path)
            for file_path in self._find_all_directories(self.distribution.metadata.name+'.egg-info', directory):
                shutil.rmtree(file_path)
        # tests directory
        if path.exists('tests'):
            for file_path in self._find_all_directories('__pycache__', 'tests'):
                shutil.rmtree(file_path)
        if path.exists('.coverage'):
            remove('.coverage')
        if path.exists('htmlcov'):
            shutil.rmtree('htmlcov')
        if path.exists('.eggs'):
            shutil.rmtree('.eggs')
        if path.exists('.pytest_cache'):
            shutil.rmtree('.pytest_cache')


class Coverage(Command):
    description = 'generate report'

    user_options = [
        ('source=', 's', 'source directory')
    ]

    _sources = ''

    def initialize_options(self):
        self._sources = None

    def finalize_options(self):
        if self._sources is None:
            self._sources = ['--source={dir}'.format(dir=directory) for directory in
                             self.distribution.package_dir.values()]

    def run(self) -> None:
        subprocess.call(['coverage', 'stats'] + self._sources + ['setup.py', 'test'])
        subprocess.call(['coverage', 'report'])
        subprocess.call(['coverage', 'html'])


if __name__ == '__main__':
    conf = read_configuration('setup.cfg')
    app_name = conf['metadata']['name']
    setup(
        name=app_name,
        version=conf['metadata']['version'],
        description=conf['metadata']['description'],
        author=conf['metadata']['author'],
        license=conf['metadata']['license'],
        classifiers=conf['metadata']['classifiers'],
        keywords=conf['metadata']['keywords'],
        cmdclass={'clean': ExtendedClean, 'coverage': Coverage},
        packages=find_namespace_packages(where='./src/'),
        package_dir={'': 'src'},
        include_package_data=True,
        zip_safe=False,
        data_files=[(f'share/{app_name}/', get_files('resources'))],
        install_requires=['colorama        >= 0.4.3'],
        setup_requires=['pytest-runner     >= 5.1',
                        'wheel             >= 0.34.2',
                        'setuptools        >= 40.8.0'],
        tests_require=['pytest             >= 3.6',
                       'pytest-dependency  >= 0.3',
                       'pytest-mock        >= 1.10',
                       'coverage           >= 4.5',
                       'flake8             >= 2.6'],
        extras_require={}
    )
