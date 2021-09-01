from tortoise.models import Model
from tortoise import fields


class ImageURLField(fields.TextField):
    def to_db_value(self, value, _):
        return value.split("/attachments/")[-1]

    def to_python_value(self, value):
        return f"https://cdn.discordapp.com/attachments/{value}"


class ToonUser(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField()
    avatar = fields.TextField()


class ToonChannel(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField()


class ToonData(Model):
    id = fields.IntField(pk=True)
    url = ImageURLField()
    user = fields.ForeignKeyField("models.ToonUser")
    channel = fields.ForeignKeyField("models.ToonChannel")
    created_at = fields.DatetimeField()
