"""add_content_items_count_to_newsletters

Revision ID: 4a408dda0acd
Revises: 
Create Date: 2025-10-16 20:14:27.382348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a408dda0acd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add content_items_count column to newsletters table."""
    # Check if column exists before adding (idempotent)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('newsletters')]

    if 'content_items_count' not in columns:
        op.add_column('newsletters',
            sa.Column('content_items_count', sa.Integer(), nullable=False, server_default='0')
        )

        # Add comment
        op.execute("""
            COMMENT ON COLUMN newsletters.content_items_count
            IS 'Number of content items included in this newsletter'
        """)

        # Refresh Supabase PostgREST schema cache
        op.execute("NOTIFY pgrst, 'reload schema'")


def downgrade() -> None:
    """Remove content_items_count column from newsletters table."""
    op.drop_column('newsletters', 'content_items_count')
