"""
Form generation utilities for Tortoise ORM Model class.

Example usage:

.. code-block:: python

    from tortoise.models import Model
    from tortoise import fields


    class Book(Model):
        id = fields.IntField(pk=True)
        title = fields.CharField(max_length=255)
        content = fields.TextField()
        created = fields.DatetimeField(auto_now_add=True)

        def __str__(self):
            return self.title

        class Meta:
            ordering = ["-id"]

   # Generate a form based on the model.
   BookForm = model_form(Book)

   # Get a form populated with model data.
   item = await Book.get(id=id)
   form = BookForm(obj=item)

Properties from the model can be excluded from the generated form, or it can
include just a set of properties. For example:

.. code-block:: python

   # Generate a form based on the model, excluding 'id' and 'created'.
   BookForm = model_form(Book, exclude=['id', 'created'])

   # or...

   # Generate a form based on the model, only including 'title' and 'content'.
   BookForm = model_form(Book, only=['title', 'content'])

The form can be generated setting field arguments:

.. code-block:: python

   BookForm = model_form(Book, only=['title', 'content'], field_args={
       'title': {
           'label': 'Your new label',
       },
       'content': {
           'label': 'Your new label',
       }
   })
"""
from wtforms import Form
from wtforms import fields as f
from wtforms import validators
from wtforms.validators import DataRequired


def convert_IntField(model, prop, kwargs):
    """Returns a form field for a IntField."""
    return f.IntegerField()


def convert_SmallIntField(model, prop, kwargs):
    """Returns a form field for a SmallIntField."""
    return f.IntegerField()


def convert_BigIntField(model, prop, kwargs):
    """Returns a form field for a BigIntField."""
    return f.IntegerField()


def convert_CharField(model, prop, kwargs):
    """Returns a form field for a CharField."""
    kwargs["validators"].append(validators.length(max=255))
    return f.StringField(**kwargs)


def convert_TextField(model, prop, kwargs):
    """Returns a form field for a TextField."""
    return f.TextAreaField(**kwargs)


def convert_UUIDField(model, prop, kwargs):
    """Returns a form field for a CharField."""
    kwargs["validators"].append(validators.length(max=36))
    return f.StringField(**kwargs)


def convert_BooleanField(model, prop, kwargs):
    """Returns a form field for a BooleanField."""
    return f.BooleanField(**kwargs)


def convert_FloatField(model, prop, kwargs):
    """Returns a form field for a FloatField."""
    return f.FloatField(**kwargs)


def convert_DecimalField(model, prop, kwargs):
    """Returns a form field for a DecimalField."""
    return f.FloatField(**kwargs)


def convert_DateTimeField(model, prop, kwargs):
    """Returns a form field for a DateTimeField."""
    return f.DateTimeField(**kwargs)


def convert_DateField(model, prop, kwargs):
    """Returns a form field for a DateField."""
    return f.DateField(**kwargs)


class ModelConverter:
    """
    Converts properties from a Model class to form fields.
    Default conversions between properties and fields:
    """

    default_converters = {
        "CharField": convert_CharField,
        "TextField": convert_TextField,
        "UUIDField": convert_UUIDField,
        "BooleanField": convert_BooleanField,
        "IntField": convert_IntField,
        "SmallIntField": convert_IntField,
        "BigIntField": convert_IntField,
        "FloatField": convert_FloatField,
        "DatetimeField": convert_DateTimeField,
        "DateField": convert_DateField,
    }

    def __init__(self, converters=None):
        """
        Constructs the converter, setting the converter callables.

        :param converters:
            A dictionary of converter callables for each property type. The
            callable must accept the arguments (model, prop, kwargs).
        """
        self.converters = converters or self.default_converters

    def convert(self, model, prop, field_args):
        """
        Returns a form field for a single model property.

        :param model:
            The Model class that contains the property.
        :param prop:
            The model property: a ``db.fields`` instance.
        :param field_args:
            Optional keyword arguments to construct the field.
        """
        prop_type_name = type(prop).__name__
        kwargs = {
            "label": prop.model_field_name.title(),
            "default": prop.default,
            "validators": [],
        }
        if field_args:
            kwargs.update(field_args)

        if prop.required:
            kwargs["validators"].append(DataRequired())

        converter = self.converters.get(prop_type_name, None)
        if converter is not None:
            return converter(model, prop, kwargs)


def model_fields(
    model, only=None, exclude=None, field_args=None, converter=None
):
    """
    Extracts and returns a dictionary of form fields for a given
    Model class.

    :param model:
        The Model class to extract fields from.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to a keyword arguments
        used to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, ModelConverter is used.
    """
    converter = converter or ModelConverter()
    field_args = field_args or {}

    # Get the field names we want to include or exclude, starting with the
    # full list of model properties.
    props = model._meta.fields_map
    field_names = [prop for prop in props]

    if only:
        field_names = [f for f in only if f in field_names]

    elif exclude:
        field_names = [f for f in field_names if f not in exclude]

    # Create all fields.
    field_dict = {}
    for name in field_names:
        field = converter.convert(model, props[name], field_args.get(name))
        if field is not None:
            field_dict[name] = field
    return field_dict


def model_form(
    model,
    base_class=Form,
    only=None,
    exclude=None,
    field_args=None,
    converter=None,
):
    """
    Creates and returns a dynamic ``wtforms.Form`` class for a given
    Model class. The form class can be used as it is or serve as a base
    for extended form classes, which can then mix non-model related fields,
    subforms with other model forms, among other possibilities.

    :param model:
        The Model class to generate a form for.
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments
        used to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, ModelConverter is used.
    """
    # Extract the fields from the model.
    field_dict = model_fields(model, only, exclude, field_args, converter)

    # Return a dynamically created form class, extending from base_class and
    # including the created fields as properties.
    return type(model.__name__ + "Form", (base_class,), field_dict)
