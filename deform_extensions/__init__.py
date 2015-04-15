# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
#
"""
Provide custom colander schemas and associated widgets to render forms
differently
"""
import cgi
import json
import warnings
import colander
import deform
import random
from string import lowercase

from deform.i18n import _
from translationstring import TranslationString
from deform.compat import url_quote
from deform.compat import string_types
from pyramid.renderers import render
from collections import OrderedDict
from itertools import izip_longest
from deform.schema import default_widget_makers as defaults


TEMPLATES_PATH = "deform_extensions:templates/"


def gen_random_string(size=15):
    """
    Generate random string

        size

            size of the resulting string
    """
    return ''.join(random.choice(lowercase) for _ in range(size))


def random_tag_id(size=15):
    """
    Return a random string supposed to be used as tag id
    """
    return gen_random_string(size)


def grouper(iterable, items, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks

    e.g:

        grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx

    Got it from https://docs.python.org/2/library/itertools.html#recipes
    """
    args = [iter(iterable)] * items
    return izip_longest(fillvalue=fillvalue, *args)


class DisabledInput(deform.widget.Widget):
    """
        A non editable input
    """
    template = TEMPLATES_PATH + "disabledinput.pt"

    def serialize(self, field, cstruct=None, readonly=True):
        if cstruct is colander.null:
            cstruct = u''
        quoted = cgi.escape(cstruct, quote='"')
        params = {'name': field.name, 'value': quoted}
        return field.renderer(self.template, **params)

    def deserialize(self, field, pstruct):
        return pstruct


class Inline(colander.Mapping):
    """
    Inline schema type, necessary to avoid our mapping to be render as tabs
    (see deform_bootstrap.utils.tabify function )
    """
    pass


class InlineMappingWidget(deform.widget.MappingWidget):
    """
    The custom widget we use to render our mapping
    """
    template = TEMPLATES_PATH + "inline_mapping.pt"
    item_template = TEMPLATES_PATH + "inline_mapping_item.pt"
    readonly_template = TEMPLATES_PATH + "inline_mapping.pt"
    readonly_item_template = TEMPLATES_PATH + "inline_mapping_item.pt"


class InlineMappingSchema(colander.MappingSchema):
    """
    Schema providing inline rendering of form elements
    """
    schema_type = Inline
    widget = InlineMappingWidget()


class VoidWidget(object):
    """
    Void widget used to fill our grid
    """
    def __init__(self, width=1):
        self.width = width

    def render_template(self, template):
        """
        Return a div of class span<width>
        """
        return u"<div class='span{0}'><br /></div>".format(self.width)


class TableMappingWidget(deform.widget.MappingWidget):
    """
    A custom widget rendering a mapping as a table

    :param cols: number of columns we want
    """
    default_cols = 3
    num_cols = 12
    template = TEMPLATES_PATH + "grid_mapping.pt"
    item_template = TEMPLATES_PATH + "grid_mapping_item.pt"
    readonly_template = TEMPLATES_PATH + "grid_mapping.pt"
    readonly_item_template = TEMPLATES_PATH + "grid_mapping_item.pt"

    def childgroup(self, field):
        """
        Return children grouped regarding the grid description
        """
        cols = getattr(self, "cols", self.default_cols)
        width = self.num_cols / cols
        for child in field.children:
            child.width = width
        res = list(grouper(field.children, cols, fillvalue=None))
        return res


class GridMappingWidget(TableMappingWidget):
    """
    A custom mapping widget rendering it as a grid

    :param tuple grid: A matrix describing the grid we want. The matrix should
    be composed of two dimensionnal vectors (width, filled) where filled is a
    boolean.

    :param tuple named_grid: A matrix describing the grid we want. The matrix
    should be composed of two dimensionnal vectors (name, width).


    .. code-block:: python

        class CompanyMainInformations(colander.MappingSchema):
            title = colander.SchemaNode(
                colander.String(),
                title=u'Nom entreprise',
            )
            address = colander.SchemaNode(
                colander.String(),
                title=u'Adresse',
                width="5",
            )
            lon_coord = colander.SchemaNode(
                colander.Float(),
                title=u"Longitude",
            )
            lat_coord = colander.SchemaNode(
                colander.Float(),
                title=u"Latitude",
            )

            GRID = (
                ((3, True), ),
                ((6, True), (2, False), (2, True), (2, True)),
                )

            class CompanySchema(colander.Schema):
                tab = CompanyMainInformations(
                    widget=GridMappingWidget(grid=GRID)
                )

            NAMED_GRID = (
                (('title', 3), ),
                (('address', 6), (None, 2), ('lon_coord', 2), ('lat_coord', 2)),
                )

            class CompanySchema(colander.Schema):
                tab = CompanyMainInformations(
                    widget=GridMappingWidget(named_grid=NAMED_GRID)
                    )


    Here, in both cases, we've got a two lines grid with 1 element on the first
    line and 3 on the second one. The second element of the second line will be
    a void cell of 2 units width
    """

    # The default bootstrap layout contains 12 columns
    num_cols = 12

    def _childgroup(self, children, grid):
        """
        Stores the children in a list following the grid's structure

        :param children: list of fields

        :param grid: a list of list corresponding of the layout to apply to the
        given children
        """
        result = []
        index = 0
        hidden_fields = []

        for row in grid:
            child_row = []
            width_sum = 0
            for width, filled in row:
                width_sum += width
                if width_sum > self.num_cols:
                    warnings.warn(u"It seems your grid configuration overlaps \
the bootstrap layout columns number. One of your lines is larger than {0}. \
You can increase this column number by compiling bootstrap css with \
lessc.".format(self.num_cols))

                if filled:
                    try:
                        child = children[index]
                    except IndexError:
                        warnings.warn(u"The grid items number doesn't \
match the number of children of our mapping widget")
                        break
                    if type(child.widget) == deform.widget.HiddenWidget:
                        hidden_fields.append(child)
                        index += 1
                        try:
                            child = children[index]
                        except IndexError:
                            warnings.warn(u"The grid items number doesn't \
match the number of children of our mapping widget")
                            break
                    child.width = width
                    index += 1
                else:
                    child = VoidWidget(width)
                child_row.append(child)
            if child_row != []:
                result.append(child_row)

        if index <= len(children):
            result.append(children[index:])

        if hidden_fields != []:
            result.append(hidden_fields)
        return result

    @staticmethod
    def _dict_children(children):
        """
        Format the given children list as a dict
        """
        return dict((elem.name, elem) for elem in children)

    def _childgroup_by_name(self, children, grid):
        """
        Group the children ordering them by name
        """
        children = self._dict_children(children)
        result = []

        for row in grid:
            child_row = []
            width_sum = 0
            for name, width in row:
                width_sum += width
                if width_sum > self.num_cols:
                    warnings.warn(u"It seems your grid configuration overlaps \
the bootstrap layout columns number. One of your lines is larger than {0}. \
You can increase this column number by compiling bootstrap css with \
lessc.".format(self.num_cols))

                if name is not None:
                    try:
                        child = children.pop(name)
                    except KeyError:
                        warnings.warn(u"No node {0} found".format(name))
                        child = VoidWidget(width)
                    child.width = width

                else:
                    child = VoidWidget(width)
                child_row.append(child)

            if child_row != []:
                result.append(child_row)

        # Add the field not configured in the grid
        for value in children.values():
            result.append([value])
        return result

    def childgroup(self, field):
        """
        Return a list of fields stored by row regarding the configured grid

        :param field: The original field this widget is attached to
        """
        grid = getattr(self, "grid", None)
        named_grid = getattr(self, "named_grid", None)

        if grid is not None:
            childgroup = self._childgroup(field.children, grid)
        elif named_grid is not None:
            childgroup = self._childgroup_by_name(field.children, named_grid)
        else:
            raise AttributeError(u"Missing the grid or named_grid argument")

        return childgroup


class AccordionMappingWidget(GridMappingWidget):
    """
    Render a mapping as an accordion and places inner fields in a grid

    .. code-block:: python

        class Mapping(colander.MappingSchema):
            field = colander.SchemaNode(...)

        class Schema(colander.Schema):
            mymapping = Mapping(title=u'The accordion header',
                widget = AccordionMappingWidget(grid=GRID)
                )

    you'll need to set the bootstrap_form_style to 'form-grid'

    Form(schema=Schema(), bootstrap_form_style='form-grid')
    """
    template = TEMPLATES_PATH + "accordion_mapping.pt"
    readonly_template = TEMPLATES_PATH + "accordion_mapping.pt"

    @property
    def tag_id(self):
        """
        Return a unique tag id for this mapping
        """
        if not hasattr(self, '_tag_id'):
            self._tag_id = random_tag_id()
        return self._tag_id


class TableFormWidget(TableMappingWidget):
    template = TEMPLATES_PATH + "grid_form.pt"
    readonly_template = TEMPLATES_PATH + "grid_form.pt"


class GridFormWidget(GridMappingWidget):
    """
    Render a form as a grid

    .. code-block:: python

        class CompanyMainInformations(colander.MappingSchema):
            title = colander.SchemaNode(
                colander.String(),
                title=u'Nom entreprise',
            )
            address = colander.SchemaNode(
                colander.String(),
                title=u'Adresse',
                width="5",
            )

        LAYOUT = (((2, True), (2, False), (2, True),),)

        schema = CompanyMainInformations()
        form = Form(schema)
        form.widget = GridFormWidget(grid=LAYOUT)

    .. warning::

        Here you need to set the widget after you initialize the form object

    """
    template = TEMPLATES_PATH + "grid_form.pt"
    readonly_template = TEMPLATES_PATH + "grid_form.pt"


class AccordionFormWidget(GridFormWidget):
    """
    AccordionFormWidget is supposed to be combined with colanderalchemy

    The way it works::

        In your SqlAlchemy models, enter the __colanderalchemy__ key under the
        info attribute.  All columns of a single model can have a section key.
        If so, an accordion will contain all columns under the same section key

        If you want each accordion to be rendered as a grid, you can optionnaly
        pass a grids or named_grids argument that should be a dict :
            {<section_name>: <associated_grid_object>}

        The associated_grid_object should be in the same format as for the
        GridMappingWidget


    .. code-block:: python

        class Model(DBBASE):
            coordonnees_emergency_name = Column(
                String(50),
                info={
                    'colanderalchemy':{
                        'title': u"Contact urgent : Nom",
                        'section': u'Coordonnées',
                    }
                }
            )
            coordonnees_emergency_phone = Column(
                String(14),
                info={
                    'colanderalchemy':{
                        'title': u'Contact urgent : Téléphone',
                        'section': u'Coordonnées',
                    }
                }
            )

            # STATUT
            statut_social_status_id = Column(
                ForeignKey('social_status_option.id'),
                info={
                    'colanderalchemy':
                    {
                        'title': u"Statut social à l'entrée",
                        'section': u'Statut',
                        'widget': get_deferred_select(SocialStatusOption),
                    }
                }
            )

        schema = SQLAlchemySchemaNode(Model)
        form = Form(schema)
        form.widget = AccordionMappingWidget()
    """
    num_cols = 12
    template = TEMPLATES_PATH + "accordion_form.pt"
    readonly_template = TEMPLATES_PATH + "accordion_form.pt"
    default_item_template = deform.widget.MappingWidget.item_template

    def accordions(self, form):
        """
        return the chlidren of the given form in a dict allowing to render them
        in accordions with a grid layout
        :param form: the form object
        """
        fixed = []
        accordions = OrderedDict()

        for child in form.children:
            section = getattr(child.schema, 'section', '')
            if not section:
                fixed.append(child)
            else:
                if section not in accordions.keys():
                    accordions[section] = {
                        'tag_id': random_tag_id(),
                        'children': [],
                        'name': section,
                        "error": False,
                    }
                if child.error:
                    accordions[section]['error'] = True
                accordions[section]['children'].append(child)

        grids = getattr(self, "grids", {})
        named_grids = getattr(self, 'named_grids', {})

        if grids is not {}:
            method = self._childgroup
        elif named_grids is not {}:
            method = self._childgroup_by_name
        else:
            warnings.warn(u"Missing both grids and named_grids argument")

        for accordion in accordions.values():
            name = accordion['name']
            grid = grids.get(name)
            if grid is not None:
                children = accordion.pop('children')
                accordion['rows'] = method(children, grid)

        return fixed, accordions


class LocalizationWidget(deform.widget.TextInputWidget):
    """
    A widget with a link for configuring localization picking it from a map
    A link will be provided, by clicking on it, we do some fancy html
    manipulation to replace the fields and have a pretty layout

    e.g:

        >>> widget = LocalizationWidget(
        ...     lat_field_name='lat_coord',
        ...     lon_field_name='lon_coord'
        ... )
        >>> class Schema():
        ...     lat_coord = colander.Schema(colander.Float())
        ...     lon_coord = colander.Schema(colander.Float(), widget=widget)
    """
    template = TEMPLATES_PATH + "localization.pt"
    readonly_template = TEMPLATES_PATH + "localization.pt"


class HiddenLocalizationWidget(deform.widget.TextInputWidget):
    """
    A hidden version
    """
    template = TEMPLATES_PATH + "hidden_localization.pt"
    readonly_template = TEMPLATES_PATH + "hidden_localization.pt"


class CustomDateInputWidget(deform.widget.Widget):
    """

    Renders a JQuery UI date picker widget
    (http://jqueryui.com/demos/datepicker/).  Most useful when the
    schema node is a ``colander.Date`` object.
    alt Tag is used to allow full customization of the displayed input

    **Attributes/Arguments**

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    options
        Options for configuring the widget (eg: date format)

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """
    template = TEMPLATES_PATH + 'dateinput.pt'
    readonly_template = 'readonly/textinput.pt'
    size = None
    requirements = (
        ('modernizr', None),
        ('jqueryui', None),
    )
    default_options = (('dateFormat', 'dd/mm/yy'),)

    def __init__(self, *args, **kwargs):
        self.options = dict(self.default_options)
        deform.widget.Widget.__init__(self, *args, **kwargs)

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (colander.null, None):
            cstruct = ''
        template = readonly and self.readonly_template or self.template
        options = self.options
        # Force iso format for colander compatibility
        options['altFormat'] = 'yy-mm-dd'
        return field.renderer(template,
                              field=field,
                              cstruct=cstruct,
                              options=self.options)

    def deserialize(self, field, pstruct):
        date = pstruct.get('date', colander.null)
        if date in ('', colander.null):
            return colander.null
        return date


class CustomDateTimeInputWidget(CustomDateInputWidget):
    """
    Renders a datetime picker widget.

    The default rendering is as a native HTML5 datetime  input widget,
    falling back to jQuery UI date picker with a JQuery Timepicker add-on
    (http://trentrichardson.com/examples/timepicker/).

    Used for ``colander.DateTime`` schema nodes.

    **Attributes/Arguments**

    options
        A dictionary of options that's passed to the datetimepicker.

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).

    style
        A string that will be placed literally in a ``style`` attribute on
        the text input tag.  For example, 'width:150px;'.  Default: ``None``,
        meaning no style attribute will be added to the input tag.

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """
    template = TEMPLATES_PATH + 'datetimeinput.pt'
    readonly_template = 'readonly/textinput.pt'
    type_name = 'datetime'
    size = None
    style = None
    requirements = (
        ('modernizr', None),
        ('jqueryui', None),
        ('datetimepicker', None),
        )

    # separator is only used for display purpose
    default_options = (('dateFormat', 'dd/mm/yy'),
                       ('timeFormat', 'HH:mm'),
                       ('separator', ' '))

    def serialize(self, field, cstruct, readonly=False):
        print("Cstruct : %s" % cstruct)
        if cstruct in (colander.null, None):
            cstruct = ''
        if cstruct:
            parsed = colander.iso8601.ISO8601_REGEX.match(cstruct)
            if parsed:  # strip timezone if it's there
                timezone = parsed.groupdict()['timezone']
                if timezone and cstruct.endswith(timezone):
                    cstruct = cstruct[:-len(timezone)]
        options = self.options
        options['altFormat'] = 'yy-mm-dd'
        separator = options.get('separator', ' ')
        cstruct = separator.join(cstruct.split('T'))
        options = json.dumps(options)
        template = readonly and self.readonly_template or self.template
        return field.renderer(
            template,
            field=field,
            cstruct=cstruct,
            options=options)

    def deserialize(self, field, pstruct):
        datetime_data = pstruct.get('datetime', colander.null)
        if datetime_data in ('', colander.null):
            return colander.null
        return datetime_data.replace(self.options['separator'], 'T')


class CustomChosenOptGroupWidget(deform.widget.SelectWidget):
    """
    Customize the chosenselectwidget to be able to provide a default value for
    unselection
    """
    template = TEMPLATES_PATH + 'chosen_optgroup.pt'


class CustomSequenceWidget(deform.widget.SequenceWidget):
    """
        See : https://github.com/Pylons/deform/pull/79
    """
    def prototype(self, field):
        """
            Build the prototype of a serialized sequence item
        """
        # we clone the item field to bump the oid (for easier
        # automated testing; finding last node)
        item_field = field.children[0].clone()
        proto = field.renderer(self.item_template, field=item_field,
                            cstruct=item_field.schema.serialize(colander.null),
                                                             parent=field)
        if isinstance(proto, string_types):
            proto = proto.encode('utf-8')
        proto = url_quote(proto)
        return proto

    def serialize(self, field, cstruct, readonly=False):
        """
            Overrided serialize method
        """
        if (self.render_initial_item and self.min_len is None):
            # This is for compat only: ``render_initial_item=True`` should
            # now be spelled as ``min_len = 1``
            self.min_len = 1

        if cstruct in (colander.null, None):
            if self.min_len is not None:
                cstruct = [colander.null] * self.min_len
            else:
                cstruct = []

        cstructlen = len(cstruct)

        if self.min_len is not None and (cstructlen < self.min_len):
            cstruct = list(cstruct) + \
                    ([colander.null] * (self.min_len - cstructlen))

        item_field = field.children[0]

        if getattr(field, 'sequence_fields', None):
            # this serialization is being performed as a result of a
            # validation failure (``deserialize`` was previously run)
            assert(len(cstruct) == len(field.sequence_fields))
            subfields = list(zip(cstruct, field.sequence_fields))
        else:
            # this serialization is being performed as a result of a
            # first-time rendering
            subfields = []
            for val in cstruct:
                if val is colander.null:
                    val = item_field.schema.serialize(val)
                subfields.append((val, item_field.clone()))

        template = readonly and self.readonly_template or self.template
        translate = field.translate
        add_template_mapping = dict(
            subitem_title=translate(item_field.title),
            subitem_description=translate(item_field.description),
            subitem_name=item_field.name)
        if isinstance(self.add_subitem_text_template, TranslationString):
            add_subitem_text = self.add_subitem_text_template % \
                add_template_mapping
        else:
            add_subitem_text = _(self.add_subitem_text_template,
                                 mapping=add_template_mapping)
        return field.renderer(template,
                              field=field,
                              cstruct=cstruct,
                              subfields=subfields,
                              item_field=item_field,
                              add_subitem_text=add_subitem_text)


def add_resources_to_registry():
    """
    Add resources to the deform registry
    """
    from deform.widget import default_resource_registry

    default_resource_registry.set_js_resources("jqueryui", None, None)
    default_resource_registry.set_js_resources("datetimepicker", None, None)

    from js.deform import resource_mapping
    # fix missing resource
    from js.select2 import select2
    resource_mapping['select2'] = select2
    # add the datetimepicker
    from js.jquery_timepicker_addon import timepicker
    resource_mapping['datetimepicker'] = timepicker


def set_default_widgets():
    """
    Set custom date and datetime input widgets for a better user-experience
    """
    defaults[colander.DateTime] = CustomDateTimeInputWidget
    defaults[colander.Date] = CustomDateInputWidget


def includeme(config):
    add_resources_to_registry()
    set_default_widgets()
