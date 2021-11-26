from tortoise import fields
from tortoise.models import Model


class Book(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    created = fields.DatetimeField(auto_now_add=True)
    pages = fields.IntField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-id"]
