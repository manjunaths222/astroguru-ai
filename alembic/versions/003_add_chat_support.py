"""Add chat support - order type and chat_messages table

Revision ID: 003_add_chat
Revises: 002_add_refund
Create Date: 2026-02-13 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_chat'
down_revision = '002_add_refund'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add type column to orders table
    op.add_column('orders', sa.Column('type', sa.String(length=50), nullable=False, server_default='full_report'))
    
    # Create index on type column
    op.create_index(op.f('ix_orders_type'), 'orders', ['type'], unique=False)
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('message_number', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes on chat_messages
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_order_id'), 'chat_messages', ['order_id'], unique=False)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_chat_messages_order_id',
        'chat_messages', 'orders',
        ['order_id'], ['id']
    )


def downgrade() -> None:
    # Drop foreign key
    op.drop_constraint('fk_chat_messages_order_id', 'chat_messages', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_chat_messages_order_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    
    # Drop chat_messages table
    op.drop_table('chat_messages')
    
    # Drop index on orders.type
    op.drop_index(op.f('ix_orders_type'), table_name='orders')
    
    # Drop type column from orders
    op.drop_column('orders', 'type')

