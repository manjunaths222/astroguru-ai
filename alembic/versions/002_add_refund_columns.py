"""Add refund columns to payments table

Revision ID: 002_add_refund
Revises: 001_initial
Create Date: 2026-02-13 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_refund'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add refund columns to payments table
    op.add_column('payments', sa.Column('razorpay_refund_id', sa.String(length=255), nullable=True))
    op.add_column('payments', sa.Column('refund_amount', sa.Float(), nullable=True))
    op.add_column('payments', sa.Column('refund_status', sa.String(length=50), nullable=True))
    
    # Create index on razorpay_refund_id
    op.create_index(op.f('ix_payments_razorpay_refund_id'), 'payments', ['razorpay_refund_id'], unique=False)


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_payments_razorpay_refund_id'), table_name='payments')
    
    # Drop columns
    op.drop_column('payments', 'refund_status')
    op.drop_column('payments', 'refund_amount')
    op.drop_column('payments', 'razorpay_refund_id')

