import unittest

from tortoise import fields
from tortoise.models import Model
from wtforms import fields as f

from wtftortoise.orm import model_form


class Book(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()


class WTFTortoiseTestCase(unittest.TestCase):
    def test_input(self):
        BookForm = model_form(Book, only=["title"])

        form = BookForm(title="Book title")
        self.assertEqual(form.data, {"title": "Book title"})

    def test_book_form(self):
        BookForm = model_form(Book)
        form = BookForm()
        self.assertEqual(list(form._fields.keys()), ["id", "title", "content"])
        self.assertEqual(
            form.data, {"id": None, "title": None, "content": None}
        )

    def test_exclude(self):
        BookForm = model_form(Book, exclude=["id", "content"])

        form = BookForm()
        self.assertEqual(list(form._fields.keys()), ["title"])
        self.assertNotEqual(
            list(form._fields.keys()), ["id", "title", "content"]
        )
        self.assertEqual(form.data, {"title": None})

    def test_only(self):
        BookForm = model_form(Book, only=["title", "content"])

        form = BookForm()
        self.assertEqual(list(form._fields.keys()), ["title", "content"])
        self.assertNotEqual(
            list(form._fields.keys()), ["id", "title", "content"]
        )
        self.assertEqual(form.data, {"title": None, "content": None})

    def test_new_label_field_args(self):
        BookForm = model_form(
            Book,
            only=["title"],
            field_args={"title": {"label": "Your new label"}},
        )

        form = BookForm()
        for field in form:
            self.assertEqual(field.label.text, "Your new label")
            self.assertNotEqual(field.label.text, "Title")

    def test_field_types(self):
        BookForm = model_form(Book)

        form = BookForm()
        self.assertTrue(isinstance(form.id, f.IntegerField))
        self.assertTrue(isinstance(form.title, f.StringField))
        self.assertTrue(isinstance(form.content, f.TextAreaField))

    def test_validators(self):
        BookForm = model_form(Book)

        form = BookForm()
        self.assertEqual(
            form.data, {"id": None, "title": None, "content": None}
        )
        self.assertFalse(form.validate())

    def test_book_form_input(self):
        BookForm = model_form(Book, exclude=["id"])
        form = BookForm(title="Book1", content="Content1")
        self.assertEqual(
            form.data,
            {
                "title": "Book1",
                "content": "Content1",
            },
        )
        self.assertTrue(form.validate())
