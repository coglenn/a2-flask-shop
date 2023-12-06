from flaskshop.database import Column, Model, db


class recipes(Model):
    __tablename__ = "recipes"
    recipe_title = Column(db.String(80), unique=True, nullable=False, comment="recipe`s name")
    