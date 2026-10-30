import pytest

from app.extensions import db
from app.models import Category, Report
from app.services.report_service import (
    ReportServiceError,
    create_report,
    verify_tracking_token,
)


@pytest.fixture
def category(app):
    item = Category(
        name_ar="المياه",
        name_fr="Eau",
        slug="water",
        is_active=True,
    )

    db.session.add(item)
    db.session.commit()

    return item


def test_create_report_success(app, category):
    report, token = create_report(
        title="انقطاع المياه",
        description="انقطاع المياه في الحي منذ يومين.",
        category_id=category.id,
    )

    assert report.id is not None
    assert report.status == Report.STATUS_SUBMITTED
    assert report.is_public is False
    assert report.reference_number.startswith("BLD-")
    assert token
    assert report.tracking_token_hash != token


def test_create_report_rejects_empty_title(app, category):
    with pytest.raises(ReportServiceError):
        create_report(
            title=" ",
            description="وصف البلاغ",
            category_id=category.id,
        )


def test_create_report_rejects_invalid_category(app):
    with pytest.raises(ReportServiceError):
        create_report(
            title="مشكلة مياه",
            description="وصف المشكلة",
            category_id=9999,
        )


def test_tracking_token_verification(app, category):
    report, token = create_report(
        title="مشكلة كهرباء",
        description="انقطاع الكهرباء",
        category_id=category.id,
    )

    verified = verify_tracking_token(
        report.reference_number,
        token,
    )

    rejected = verify_tracking_token(
        report.reference_number,
        "wrong-token",
    )

    assert verified is not None
    assert verified.id == report.id
    assert rejected is None
