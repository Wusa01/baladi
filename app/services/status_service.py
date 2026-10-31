from app.extensions import db
from app.models import Report, ReportStatusHistory, User


ALLOWED_TRANSITIONS = {
    Report.STATUS_SUBMITTED: {
        Report.STATUS_UNDER_REVIEW,
        Report.STATUS_REJECTED,
    },
    Report.STATUS_VERIFIED: {
        Report.STATUS_REJECTED,
    },
    Report.STATUS_UNDER_REVIEW: {
        Report.STATUS_VERIFIED,
        Report.STATUS_REJECTED,
        Report.STATUS_DUPLICATE,
    },
    Report.STATUS_VERIFIED: {
        Report.STATUS_PUBLISHED,
        Report.STATUS_REJECTED,
    },
    Report.STATUS_PUBLISHED: {
        Report.STATUS_REFERRED,
        Report.STATUS_IN_PROGRESS,
        Report.STATUS_CLOSED,
    },
    Report.STATUS_REFERRED: {
        Report.STATUS_IN_PROGRESS,
        Report.STATUS_RESOLVED,
        Report.STATUS_CLOSED,
    },
    Report.STATUS_IN_PROGRESS: {
        Report.STATUS_RESOLVED,
        Report.STATUS_CLOSED,
    },
    Report.STATUS_RESOLVED: {
        Report.STATUS_CLOSED,
        Report.STATUS_IN_PROGRESS,
    },
    Report.STATUS_CLOSED: set(),
    Report.STATUS_REJECTED: set(),
    Report.STATUS_DUPLICATE: set(),
}


# Transitions available to reviewers.
# Publishing remains an administrator-only action.
REVIEWER_TRANSITIONS = {
    Report.STATUS_SUBMITTED: {
        Report.STATUS_UNDER_REVIEW,
        Report.STATUS_REJECTED,
    },
    Report.STATUS_UNDER_REVIEW: {
        Report.STATUS_VERIFIED,
        Report.STATUS_REJECTED,
        Report.STATUS_DUPLICATE,
    },
    Report.STATUS_PUBLISHED: {
        Report.STATUS_REFERRED,
        Report.STATUS_IN_PROGRESS,
        Report.STATUS_CLOSED,
    },
    Report.STATUS_REFERRED: {
        Report.STATUS_IN_PROGRESS,
        Report.STATUS_RESOLVED,
        Report.STATUS_CLOSED,
    },
    Report.STATUS_IN_PROGRESS: {
        Report.STATUS_RESOLVED,
        Report.STATUS_CLOSED,
    },
    Report.STATUS_RESOLVED: {
        Report.STATUS_CLOSED,
        Report.STATUS_IN_PROGRESS,
    },
}


class StatusTransitionError(Exception):
    pass


def change_report_status(
    report_id,
    new_status,
    changed_by_id,
    note=None,
):
    # Verify the report exists.
    report = db.session.get(Report, report_id)

    if report is None:
        raise StatusTransitionError("البلاغ غير موجود.")

    # Require an authenticated database user.
    if changed_by_id is None:
        raise StatusTransitionError(
            "يجب تحديد المستخدم المسؤول عن تغيير الحالة."
        )

    user = db.session.get(User, changed_by_id)

    if user is None or not user.is_active:
        raise StatusTransitionError(
            "المستخدم غير موجود أو حسابه غير نشط."
        )

    # Verify the user's role.
    if user.role not in User.VALID_ROLES:
        raise StatusTransitionError(
            "ليس لديك صلاحية لتغيير حالة البلاغ."
        )

    old_status = report.status

    allowed = ALLOWED_TRANSITIONS.get(old_status, set())

    # Verify the requested transition.
    if new_status not in allowed:
        raise StatusTransitionError(
            f"لا يمكن الانتقال من {old_status} إلى {new_status}."
        )

    # Apply role-specific restrictions.
    if user.role == User.ROLE_REVIEWER:

        reviewer_allowed = REVIEWER_TRANSITIONS.get(
            old_status,
            set(),
        )

        if new_status not in reviewer_allowed:
            raise StatusTransitionError(
                "لا تملك صلاحية تنفيذ هذا الإجراء."
            )

    # Publishing is exclusively an administrator action.
    if new_status == Report.STATUS_PUBLISHED:
        if user.role != User.ROLE_ADMIN:
            raise StatusTransitionError(
                "نشر البلاغ متاح للمشرف فقط."
            )

    history = ReportStatusHistory(
        report_id=report.id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=user.id,
        note=note,
        is_public=(new_status == Report.STATUS_PUBLISHED),
    )

    try:
        report.status = new_status

        # A report becomes publicly visible only after publication.
        if new_status == Report.STATUS_PUBLISHED:
            report.is_public = True

        db.session.add(history)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return report
