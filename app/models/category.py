from app.extensions import db


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name_ar = db.Column(
        db.String(100),
        nullable=False
    )

    name_fr = db.Column(
        db.String(100),
        nullable=False
    )

    slug = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    description_ar = db.Column(
        db.Text,
        nullable=True
    )

    description_fr = db.Column(
        db.Text,
        nullable=True
    )

    icon = db.Column(
        db.String(50),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    def __repr__(self):
        return f"<Category {self.slug}>"
