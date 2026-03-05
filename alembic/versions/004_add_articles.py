"""Add articles table

Revision ID: 004
Revises: 003_add_chat_support
Create Date: 2024-03-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003_add_chat_support'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('excerpt', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False, server_default='AstroGuru Team'),
        sa.Column('featured_image', sa.String(length=500), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indices
    op.create_index(op.f('ix_articles_title'), 'articles', ['title'], unique=False)
    op.create_index(op.f('ix_articles_slug'), 'articles', ['slug'], unique=True)
    op.create_index(op.f('ix_articles_category'), 'articles', ['category'], unique=False)


def downgrade() -> None:
    # Drop indices
    op.drop_index(op.f('ix_articles_category'), table_name='articles')
    op.drop_index(op.f('ix_articles_slug'), table_name='articles')
    op.drop_index(op.f('ix_articles_title'), table_name='articles')
    
    # Drop table
    op.drop_table('articles')
