import pytest

from app.extensions import db
from app.models import Category, Report, ReportStatusHistory
from app.services.report_service import create_report
from app.services.status_service import (
    StatusTransitionError,
    change_report_status,
)


@pytest.fixture
def report(app):
    category = Category(
        name_ar="الطرق",
        name_fr="Routes",
        slug="roads",
        is_active=True,
    )

    db.session.add(category)
    db.session.commit()

    created_report, token = create_report(
        title="طريق متضرر",
        description="وجود حفرة كبيرة في الطريق.",
        category_id=category.id,
    )

    return created_report


def test_valid_status_transition(app, report):
    updated_report = change_report_status(
        report_id=report.id,
        new_status=Report.STATUS_UNDER_REVIEW,
        note="بدأت مراجعة البلاغ.",
    )

    assert updated_report.status == Report.STATUS_UNDER_REVIEW

    history = ReportStatusHistory.query.filter_by(
        report_id=report.id
    ).first()

    assert history is not None
    assert history.old_status == Report.STATUS_SUBMITTED
    assert history.new_status == Report.STATUS_UNDER_REVIEW


def test_invalid_status_transition(app, report):
    with pytest.raises(StatusTransitionError):
        change_report_status(
            report_id=report.id,
            new_status=Report.STATUS_RESOLVED,
        )

    assert report.status == Report.STATUS_SUBMITTED

    assert ReportStatusHistory.query.filter_by(
        report_id=report.id
    ).count() == 0


def test_nonexistent_report(app):
    with pytest.raises(StatusTransitionError):
        change_report_status(
            report_id=9999,
            new_status=Report.STATUS_UNDER_REVIEW,
        )
