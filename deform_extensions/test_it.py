# -*- coding: utf-8 -*-
# * Authors:
#       * TJEBBES Gaston <g.t@majerti.fr>
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
import colander
import deform


class Dummy():
    def __init__(self, **kw):
        self.__dict__.update(kw)

def test_grouper():
    from deform_extensions import grouper

    a = range(5)
    assert list(grouper(a, 3, 'x')) == [(0, 1, 2), (3, 4, 'x')]


def test_grid_childgroup_by_name():
    from deform_extensions import GridMappingWidget, VoidWidget

    NAMED_GRID = (
        (('title', 3), ),
        (('address', 6), (None, 2), ('lon_coord', 2), ('lat_coord', 2)),
    )

    children = [
        Dummy(name="title", widget=None),
        Dummy(name="address", widget=None),
        Dummy(name="lat_coord", widget=None),
        Dummy(name="telephone", widget=None),
    ]

    mapping = GridMappingWidget(named_grid=NAMED_GRID)

    childgroups = mapping._childgroup_by_name(children, NAMED_GRID)
    assert childgroups[0][0].name == "title"
    assert len(childgroups) == 3
    assert isinstance(childgroups[1][1], VoidWidget)
    assert len(childgroups[1]) == 4


def test_test_grid_childgroup_by_name_void_row():
    from deform_extensions import GridMappingWidget
    NAMED_GRID = (
        (('title', 3), ),
        (('unexisting', 6),)
    )
    children = [
        Dummy(name="title", widget=None),
    ]

    mapping = GridMappingWidget(named_grid=NAMED_GRID)

    childgroups = mapping._childgroup_by_name(children, NAMED_GRID)
    assert childgroups[0][0].name == "title"
    assert len(childgroups) == 1


def test_test_grid_childgroup_by_name_static_widget():
    from deform_extensions import GridMappingWidget, StaticWidget

    NAMED_GRID = (
        (('title', 3), ),
        ((StaticWidget("hello world"), 6),)
    )
    children = [
        Dummy(name="title", widget=None),
    ]

    mapping = GridMappingWidget(named_grid=NAMED_GRID)

    childgroups = mapping._childgroup_by_name(children, NAMED_GRID)
    assert childgroups[0][0].name == "title"
    assert len(childgroups) == 2
    assert isinstance(childgroups[1][0], StaticWidget)


def test_grid_childgroup():
    from deform_extensions import GridMappingWidget, VoidWidget

    children = [
        Dummy(name="title", widget=None),
        Dummy(name="address", widget=None),
        Dummy(name="lat_coord", widget=None),
        Dummy(name="telephone", widget=None),
        Dummy(name="fax", widget=deform.widget.HiddenWidget())
    ]
    GRID = (
        ((3, True), ),
        ((6, True), (2, False), (2, True), (2, True)),
    )
    mapping = GridMappingWidget(grid=GRID)

    childgroups = mapping._childgroup(children, GRID)
    assert childgroups[0][0].name == "title"
    assert len(childgroups) == 3
    assert isinstance(childgroups[1][1], VoidWidget)
    assert childgroups[1][3].name == "telephone"
    assert childgroups[2][0].name == "fax"
    assert len(childgroups[1]) == 4
