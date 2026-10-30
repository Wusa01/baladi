from datetime import datetime, timezone

from app.extensions import db


class Report(db.Model):

    __tablename__ = "reports"

    # Report statuses
    STATUS_SUBMITTED = "submitted"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_VERIFIED = "verified"
    STATUS_PUBLISHED = "published"
    STATUS_REFERRED = "referred"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"
    STATUS_REJECTED = "rejected"
    STATUS_DUPLICATE = "duplicate"

    id = db.Column(db.Integer, primary_key=True)

    # Public reference number
    reference_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # Report content
    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    language = db.Column(
        db.String(2),
        nullable=False,
        default="ar"
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    # Location information
    neighborhood = db.Column(
        db.String(150),
        nullable=True
    )

    exact_latitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    exact_longitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    public_latitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    public_longitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    # Private reporter information
    reporter_name = db.Column(
        db.String(120),
        nullable=True
    )

    reporter_phone = db.Column(
        db.String(30),
        nullable=True
    )

    reporter_email = db.Column(
        db.String(120),
        nullable=True
    )

    tracking_token_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # Workflow
    status = db.Column(
        db.String(30),
        nullable=False,
        default=STATUS_SUBMITTED,
        index=True
    )

    is_public = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True
    )

    submitted_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    reviewed_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    submitted_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    category = db.relationship(
        "Category",
        backref=db.backref("reports", lazy="dynamic")
    )

    submitted_by = db.relationship(
        "User",
        foreign_keys=[submitted_by_id]
    )

    reviewed_by = db.relationship(
        "User",
        foreign_keys=[reviewed_by_id]
    )

    def __repr__(self):
        return f"<Report {self.reference_number}>"
