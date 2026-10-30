from app import create_app
from app.extensions import db
from app.models import Category


CATEGORIES = [
    {
        "slug": "water-sanitation",
        "name_ar": "المياه والصرف الصحي",
        "name_fr": "Eau et assainissement",
        "description_ar": "مشكلات المياه وشبكات الصرف الصحي.",
        "description_fr": "Problèmes d'eau et de réseaux d'assainissement.",
        "icon": "droplets",
        "sort_order": 1,
    },
    {
        "slug": "electricity-lighting",
        "name_ar": "الكهرباء والإنارة",
        "name_fr": "Électricité et éclairage",
        "description_ar": "انقطاع الكهرباء وأعطال الإنارة العامة.",
        "description_fr": "Coupures d'électricité et pannes d'éclairage public.",
        "icon": "zap",
        "sort_order": 2,
    },
    {
        "slug": "roads-transport",
        "name_ar": "الطرق والنقل",
        "name_fr": "Routes et transport",
        "description_ar": "الطرق المتضررة والحفر ومشكلات النقل.",
        "description_fr": "Routes endommagées, nids-de-poule et problèmes de transport.",
        "icon": "road",
        "sort_order": 3,
    },
    {
        "slug": "cleanliness-waste",
        "name_ar": "النظافة والنفايات",
        "name_fr": "Propreté et déchets",
        "description_ar": "تراكم النفايات ومشكلات النظافة العامة.",
        "description_fr": "Accumulation de déchets et problèmes de propreté publique.",
        "icon": "trash-2",
        "sort_order": 4,
    },
    {
        "slug": "public-facilities",
        "name_ar": "المرافق العامة",
        "name_fr": "Équipements publics",
        "description_ar": "مشكلات الحدائق والمرافق والخدمات العامة.",
        "description_fr": "Problèmes liés aux parcs et aux équipements publics.",
        "icon": "building",
        "sort_order": 5,
    },
    {
        "slug": "other",
        "name_ar": "أخرى",
        "name_fr": "Autre",
        "description_ar": "مشكلات عامة لا تندرج ضمن التصنيفات السابقة.",
        "description_fr": "Autres problèmes ne correspondant pas aux catégories précédentes.",
        "icon": "circle-help",
        "sort_order": 6,
    },
]


def seed_categories():
    for data in CATEGORIES:
        category = Category.query.filter_by(
            slug=data["slug"]
        ).first()

        if category is None:
            category = Category(slug=data["slug"])

        for field, value in data.items():
            setattr(category, field, value)

        category.is_active = True
        db.session.add(category)

    db.session.commit()


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        try:
            seed_categories()
            print("Categories seeded successfully.")
        except Exception:
            db.session.rollback()
            raise
