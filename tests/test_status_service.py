import pytest

from app.extensions import db
from app.models import (
    Category,
    Report,
    ReportStatusHistory,
    User,
)
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


@pytest.fixture
def reviewer(app):
    user = User(
        username="reviewer",
        email="reviewer@example.com",
        role=User.ROLE_REVIEWER,
        is_active=True,
    )

    user.set_password("TestPassword123!")

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def admin(app):
    user = User(
        username="admin",
        email="admin@example.com",
        role=User.ROLE_ADMIN,
        is_active=True,
    )

    user.set_password("TestPassword123!")

    db.session.add(user)
    db.session.commit()

    return user


def test_valid_status_transition(app, report, reviewer):

    updated_report = change_report_status(
        report_id=report.id,
        new_status=Report.STATUS_UNDER_REVIEW,
        changed_by_id=reviewer.id,
        note="بدأت مراجعة البلاغ.",
    )

    assert updated_report.status == Report.STATUS_UNDER_REVIEW

    history = ReportStatusHistory.query.filter_by(
        report_id=report.id
    ).first()

    assert history is not None
    assert history.old_status == Report.STATUS_SUBMITTED
    assert history.new_status == Report.STATUS_UNDER_REVIEW
    assert history.changed_by_id == reviewer.id


def test_invalid_status_transition(app, report, reviewer):

    with pytest.raises(StatusTransitionError):

        change_report_status(
            report_id=report.id,
            new_status=Report.STATUS_RESOLVED,
            changed_by_id=reviewer.id,
        )

    assert report.status == Report.STATUS_SUBMITTED

    assert ReportStatusHistory.query.filter_by(
        report_id=report.id
    ).count() == 0


def test_nonexistent_report(app, reviewer):

    with pytest.raises(StatusTransitionError):

        change_report_status(
            report_id=9999,
            new_status=Report.STATUS_UNDER_REVIEW,
            changed_by_id=reviewer.id,
        )


def test_missing_user_is_rejected(app, report):

    with pytest.raises(StatusTransitionError):

        change_report_status(
            report_id=report.id,
            new_status=Report.STATUS_UNDER_REVIEW,
            changed_by_id=None,
        )


def test_reviewer_cannot_publish_report(app, report, reviewer):

    # First move the report to verified.
    report.status = Report.STATUS_VERIFIED
    db.session.commit()

    with pytest.raises(StatusTransitionError):

        change_report_status(
            report_id=report.id,
            new_status=Report.STATUS_PUBLISHED,
            changed_by_id=reviewer.id,
        )

    assert report.status == Report.STATUS_VERIFIED
    assert report.is_public is False


def test_admin_can_publish_report(app, report, admin):

    report.status = Report.STATUS_VERIFIED
    db.session.commit()

    updated_report = change_report_status(
        report_id=report.id,
        new_status=Report.STATUS_PUBLISHED,
        changed_by_id=admin.id,
        note="تمت مراجعة البلاغ والموافقة على نشره.",
    )

    assert updated_report.status == Report.STATUS_PUBLISHED
    assert updated_report.is_public is True

    history = ReportStatusHistory.query.filter_by(
        report_id=report.id
    ).first()

    assert history is not None
    assert history.changed_by_id == admin.id
    assert history.is_public is True


def test_inactive_user_cannot_change_status(app, report, reviewer):

    reviewer.is_active = False
    db.session.commit()

    with pytest.raises(StatusTransitionError):

        change_report_status(
            report_id=report.id,
            new_status=Report.STATUS_UNDER_REVIEW,
            changed_by_id=reviewer.id,
        )

    assert report.status == Report.STATUS_SUBMITTED
