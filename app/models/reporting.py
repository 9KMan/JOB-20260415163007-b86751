"""
Reporting Module Models
"""
from datetime import datetime
from app import db


class ReportConfiguration(db.Model):
    """Report configuration model for custom reports."""
    __tablename__ = 'report_configurations'

    id = db.Column(db.Integer, primary_key=True)
    report_code = db.Column(db.String(50), unique=True, nullable=False)
    report_name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # sales, inventory, financial, production, custom
    description = db.Column(db.Text)
    query_definition = db.Column(db.Text)  # JSON or SQL-like definition
    parameters = db.Column(db.Text)  # JSON string of required parameters
    column_definitions = db.Column(db.Text)  # JSON string of column definitions
    grouping = db.Column(db.String(200))
    sorting = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'report_code': self.report_code,
            'report_name': self.report_name,
            'report_type': self.report_type,
            'description': self.description,
            'query_definition': self.query_definition,
            'parameters': self.parameters,
            'column_definitions': self.column_definitions,
            'grouping': self.grouping,
            'sorting': self.sorting,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }