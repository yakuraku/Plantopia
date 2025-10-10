"""Add chat tables for AI chat feature (Iteration 3 - Session 3)

Revision ID: b9d2f7e8a3c1
Revises: a8f3e4b1c5d2
Create Date: 2025-10-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9d2f7e8a3c1'
down_revision: Union[str, None] = 'a8f3e4b1c5d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_plant_chats table
    op.create_table(
        'user_plant_chats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_plant_instance_id', sa.Integer(), nullable=True),
        sa.Column('chat_type', sa.String(length=20), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_plant_instance_id'], ['user_plant_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_plant_chats_user', 'user_plant_chats', ['user_id'], unique=False)
    op.create_index('idx_user_plant_chats_type', 'user_plant_chats', ['chat_type'], unique=False)
    op.create_index('idx_user_plant_chats_active', 'user_plant_chats', ['is_active'], unique=False)
    op.create_index('idx_user_plant_chats_expires', 'user_plant_chats', ['expires_at'], unique=False)
    op.create_index('idx_user_plant_chats_created', 'user_plant_chats', ['created_at'], unique=False)

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('has_image', sa.Boolean(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['user_plant_chats.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_chat_messages_chat', 'chat_messages', ['chat_id'], unique=False)
    op.create_index('idx_chat_messages_created', 'chat_messages', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_index('idx_chat_messages_created', table_name='chat_messages')
    op.drop_index('idx_chat_messages_chat', table_name='chat_messages')
    op.drop_table('chat_messages')

    op.drop_index('idx_user_plant_chats_created', table_name='user_plant_chats')
    op.drop_index('idx_user_plant_chats_expires', table_name='user_plant_chats')
    op.drop_index('idx_user_plant_chats_active', table_name='user_plant_chats')
    op.drop_index('idx_user_plant_chats_type', table_name='user_plant_chats')
    op.drop_index('idx_user_plant_chats_user', table_name='user_plant_chats')
    op.drop_table('user_plant_chats')
