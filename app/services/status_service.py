from app.extensions import db
from app.models import Report, ReportStatusHistory


ALLOWED_TRANSITIONS = {
    Report.STATUS_SUBMITTED: {
        Report.STATUS_UNDER_REVIEW,
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


class StatusTransitionError(Exception):
    pass


def change_report_status(
    report_id,
    new_status,
    changed_by_id=None,
    note=None,
    is_public=False,
):
    report = db.session.get(Report, report_id)

    if report is None:
        raise StatusTransitionError("البلاغ غير موجود.")

    old_status = report.status

    allowed = ALLOWED_TRANSITIONS.get(old_status, set())

    if new_status not in allowed:
        raise StatusTransitionError(
            f"لا يمكن الانتقال من {old_status} إلى {new_status}."
        )

    history = ReportStatusHistory(
        report_id=report.id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=changed_by_id,
        note=note,
        is_public=is_public,
    )

    try:
        report.status = new_status
        db.session.add(history)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return report
