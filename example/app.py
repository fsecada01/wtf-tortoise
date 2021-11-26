import secure
from models import Book
from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from tortoise import Tortoise
from tortoise.contrib.starlette import register_tortoise

from wtftortoise.orm import model_form

# Security Headers are HTTP response headers that, when set,
# can enhance the security of your web application
# by enabling browser security policies.
# more on https://secure.readthedocs.io/en/latest/headers.html
secure_headers = secure.Secure()

templates = Jinja2Templates(directory="templates")


async def list_all(request):
    menu = Tortoise.apps.get("models")
    model_describe = Tortoise.describe_model(Book)
    fk_fields = [m["name"] for m in model_describe.get("fk_fields")]
    backward_fk_fields = [m["name"] for m in model_describe.get("backward_fk_fields")]
    field_name_list = [i for i in Book._meta.fields_map if i not in backward_fk_fields]
    if fk_fields:
        results = await Book.all().prefetch_related(*fk_fields)
    else:
        results = await Book.all().values(*field_name_list)
    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "results": results,
            "field_name_list": [i for i in field_name_list],
            "menu": [i for i in menu],
        },
    )


async def create(request):
    BookForm = model_form(Book, exclude=["id", "created"])
    data = await request.form()
    form = BookForm(data)
    instance = Book()
    if request.method == "POST":
        form.populate_obj(instance)
        await instance.save()
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "create.html",
        {"request": request, "form": form, "model_name": Book.__name__},
    )


async def edit(request):
    id = request.path_params["id"]
    item = await Book.get(id=id)
    data = await request.form()
    BookForm = model_form(Book, exclude=["id", "created"])
    form = BookForm(obj=item, formdata=data)
    if request.method == "POST" and form.validate():
        form.populate_obj(item)
        await item.save()
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "form": form, "model_name": Book.__name__},
    )


async def delete(request):
    id = request.path_params["id"]
    await Book.filter(id=id).delete()
    response = RedirectResponse(url="/", status_code=302)
    return response


routes = [
    Route("/", endpoint=list_all, methods=["GET"], name="list_all"),
    Route("/create", endpoint=create, methods=["GET", "POST"], name="create"),
    Route("/{id:int}/edit", endpoint=edit, methods=["GET", "POST"], name="edit"),
    Route("/{id:int}/delete", endpoint=delete, methods=["GET"], name="delete"),
]

app = Starlette(debug=True, routes=routes)


@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.starlette(response)
    return response


register_tortoise(
    app,
    db_url="sqlite://example_db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
)
