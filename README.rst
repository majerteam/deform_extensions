================================
Deform extension tools
================================

Note : since version 0.4 deform_extensions is now compatible with python 3

.. image::
    https://secure.travis-ci.org/majerteam/deform_extensions.png?branch=master
   :target: http://travis-ci.org/majerteam/deform_extensions
   :alt: Travis-ci: continuous integration status.

This package provides custom widgets and form layout widgets.

It aims to extend deform 2 and replaces the former deform_bootstrap_extensions
(that was dedicated to deform_bootstrap and deform 0.* serie)

Install
-------

.. code-block:: console

    pip install deform_extensions


Custom widgets
--------------

    * LocalizationWidget : Map location

    * CustomDateTimeInputWidget : Datetime widget

    * RadioToggleWidget


Date related widgets were added to allow a better support for
internationalization and different format support.

The RadioToggleWidget is a common radio widget that allow to hide show form
nodes on selection. It's very similar to deform base Radio widget, the
difference is that values parameters is a list of 3-uples (instead of 2-uples),
allowing to specify the name of a form node to hide/show.


Layout Tools
--------------

Layout tools:

    * DisabledInput (that really doesn't allow edition)

    * InlineMappingWidget

    * VoidWidget that is used by GridWidgets to fill void cells

    * TableMappingWidget

    * GridMappingWidget

    * AccordionMappingWidget

    * TableFormWidget

    * GridFormWidget

    * AccordionFormWidget


See __init__.py source code for some docs or ping me on Freenode @tonthon

Run tests
----------

.. code-block:: console

    pip3 install pytest
    py.test -xv
