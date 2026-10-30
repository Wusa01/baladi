from app.extensions import db
from app.models import Category
from scripts.seed_categories import seed_categories, CATEGORIES


def test_seed_categories_creates_all_categories(app):
    seed_categories()

    assert Category.query.count() == len(CATEGORIES)


def test_seed_categories_is_idempotent(app):
    seed_categories()
    first_count = Category.query.count()

    seed_categories()
    second_count = Category.query.count()

    assert first_count == second_count


def test_categories_have_arabic_and_french_names(app):
    seed_categories()

    categories = Category.query.all()

    assert len(categories) == len(CATEGORIES)

    for category in categories:
        assert category.name_ar
        assert category.name_fr
        assert category.slug
        assert category.is_active is True
