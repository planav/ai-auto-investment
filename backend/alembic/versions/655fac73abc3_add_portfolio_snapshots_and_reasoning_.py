"""add_portfolio_snapshots_and_reasoning_columns

Revision ID: 655fac73abc3
Revises: bc06f0c36814
Create Date: 2026-04-22 09:13:17.430232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '655fac73abc3'
down_revision = 'bc06f0c36814'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('portfolio_snapshots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('portfolio_id', sa.Integer(), nullable=False),
    sa.Column('total_value', sa.Float(), nullable=False),
    sa.Column('cash_value', sa.Float(), nullable=False, server_default='0.0'),
    sa.Column('stocks_value', sa.Float(), nullable=False, server_default='0.0'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_snapshots_id'), 'portfolio_snapshots', ['id'], unique=False)
    op.add_column('portfolios', sa.Column('stock_reasoning', sa.Text(), nullable=True))
    op.add_column('portfolios', sa.Column('market_context', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('portfolios', 'market_context')
    op.drop_column('portfolios', 'stock_reasoning')
    op.drop_index(op.f('ix_portfolio_snapshots_id'), table_name='portfolio_snapshots')
    op.drop_table('portfolio_snapshots')
