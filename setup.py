from pathlib import Path
from setuptools import setup, find_packages

README_md = Path(__file__).parent / "README.md"
README = README_md.read_text(encoding='utf-8')

setup(
  name='autoSME',
  version="1.0.0",

  url="https://github.com/shaharjacob/autoSME",
  description="Mapping entities project",
  long_description=README,
  long_description_content_type="text/markdown",

  author="Shahar Jacob",
  author_email="shahar.jacob@mail.huji.ac.il",

  packages=find_packages(),
  python_requires='>=3.7',
  install_requires=[
    'tqdm',
    'click',
    'flask',
    'pyyaml',
    'pandas',
    'inflect',
    'requests',
    'graphviz',
    'networkx',
    'beautifulsoup4',
    'sentence_transformers',
  ],

  entry_points={
    "console_scripts": [
      'mapping = mapping:main'
    ]
  },

  include_package_data=True,
)