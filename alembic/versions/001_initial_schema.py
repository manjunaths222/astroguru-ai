"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('picture_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('razorpay_order_id', sa.String(length=255), nullable=True),
        sa.Column('razorpay_payment_id', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)
    op.create_index(op.f('ix_payments_razorpay_order_id'), 'payments', ['razorpay_order_id'], unique=True)
    op.create_index(op.f('ix_payments_razorpay_payment_id'), 'payments', ['razorpay_payment_id'], unique=True)
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'], unique=False)
    
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('birth_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_payments_status'), table_name='payments')
    op.drop_index(op.f('ix_payments_razorpay_payment_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_razorpay_order_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

