Agoraplex Sphinx Theme
======================

This repository contains themes for `Agoraplex`_ projects, based on
the `Pylons project Sphinx themes <pylons_sphinx_theme>`_. To use a
theme in your Sphinx documentation, follow this guide:

1. put this directory as _themes into your docs folder.  Alternatively
   you can also use git submodules to check out the contents there
   or symlink this directory as _themes.

2. add this to your conf.py::

    sys.path.append(os.path.abspath('_themes'))
    html_theme_path = ['_themes']
    html_theme = 'agoraplex'

The following themes exist:

- **agoraplex** - the generic Agoraplex documentation theme

.. _Agoraplex: https://agoraplex.github.com/
.. _pylons_sphinx_theme: https://github.com/Pylons/pylons_sphinx_theme
