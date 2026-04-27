"""add_is_verified_to_users

Revision ID: ea0a0dc2a7e9
Revises: 655fac73abc3
Create Date: 2026-04-27 07:20:02.146680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea0a0dc2a7e9'
down_revision = '655fac73abc3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite: add column with a server_default so existing rows get FALSE
    op.add_column(
        'users',
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('users', 'is_verified')
