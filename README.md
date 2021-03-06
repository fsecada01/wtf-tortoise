# WTF Tortoise

Form generation utilities for Tortoise ORM Model class.
Based on the code found in wtforms.ext and provides a bridge between Tortoise ORM models and wtforms.

Packaged from [Sinisaos](https://github.com/sinisaos/wtf-tortoise), who did all the work. Please support his efforts.

For testing/direct usage, just download repo, unzip and put in root of your project.  Otherwise, just run: `pip install wtf-toroise`.

Now you can import wtftortoise.orm like in edit example below.

Example usage:

```shell
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
```

Generate a form based on the model.

```shell
BookForm = model_form(Book)
```

Properties from the model can be excluded from the generated form, or it can
include just a set of properties. For example:

Generate a form based on the model, excluding 'id' and 'created'.

```shell
BookForm = model_form(Book, exclude=['id', 'created'])
```
Generate a form based on the model, only including 'title' and 'content'.

```shell
BookForm = model_form(Book, only=['title', 'content'])
```
The form can be generated setting field arguments:

```shell
BookForm = model_form(Book, only=['title', 'content'], field_args={
    'title': {
        'label': 'Your new label',
    },
    'content': {
        'label': 'Your new label',
    }
})
```
Example implementation for an edit view using Starlette:

```shell
# other imports
from wtftortoise.orm import model_form

@app.route("/{id:int}/edit", methods=["GET", "POST"])
async def edit(request):
    id = request.path_params.get("id", None)
    book = await Book.get(id=id)
    data = await request.form()
    BookForm = model_form(Book, exclude=["id", "created"])
    form = BookForm(obj=book, formdata=data)
    if request.method == "POST" and form.validate():
        form.populate_obj(book)
        await book.save()
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        "edit.html", {
            "request": request,
            "form": form
        }
    )
```

Example template for above view using Jinja and Bootstrap:

```shell
{% extends "base.html" %}
{% block content %}
<main role="main">
    <br><br>
    <div class="container">
        <h2>Edit Book</h2>
        <br>
        <form method="POST">
            {% for field in form %}
            <div class="form-group">
                {{ field.label }}:
                {{ field(class="form-control") }}
                {% for error in field.errors %}
                <span style="color: red;">*{{ error }}</span>
                {% endfor %}
            </div>
            {% endfor %}
            <p><input class="btn btn-primary" type="submit" value="Submit"></p>
        </form>
    </div> <!-- /container -->
    <hr>
</main>
{% endblock %}
```