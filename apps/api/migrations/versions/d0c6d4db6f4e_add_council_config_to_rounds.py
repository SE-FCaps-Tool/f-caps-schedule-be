"""Add council_config to rounds"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd0c6d4db6f4e'
down_revision: Union[str, None] = '0044_project_topic_seniority'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'rounds',
        sa.Column('council_config', sa.dialects.postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb"))
    )

def downgrade() -> None:
    op.drop_column('rounds', 'council_config')

