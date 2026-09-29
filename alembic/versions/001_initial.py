"""Initial audit schema."""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None


def upgrade():
    op.create_table("predictions", sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("customer_id", sa.String(80), nullable=False),
                    sa.Column("probability", sa.Float, nullable=False),
                    sa.Column("risk", sa.String(10), nullable=False),
                    sa.Column("model_version", sa.String(80), nullable=False),
                    sa.Column("features", sa.JSON, nullable=False),
                    sa.Column("value_at_risk", sa.Float, nullable=False),
                    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
                    sa.Column("label", sa.Integer))
    op.create_index("ix_predictions_customer_id", "predictions", ["customer_id"])
    op.create_index("ix_predictions_model_version", "predictions", ["model_version"])
    op.create_table("monitoring_runs", sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
                    sa.Column("report", sa.JSON, nullable=False))
    op.create_table("model_versions", sa.Column("version", sa.String(80), primary_key=True),
                    sa.Column("metadata_json", sa.JSON, nullable=False))


def downgrade():
    op.drop_table("model_versions")
    op.drop_table("monitoring_runs")
    op.drop_table("predictions")
