"""CHAR to VARCHAR

Revision ID: 7fcb2b0fd473
Revises: 64fe5bf689d7
Create Date: 2024-06-16 18:31:25.667734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7fcb2b0fd473'
down_revision: Union[str, None] = '64fe5bf689d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
context = op.get_context()


def upgrade() -> None:
    if context.dialect.name != "sqlite":
        op.alter_column(
            'subscribes', 'name',
            existing_type=sa.CHAR(length=128),
            type_=sa.VARCHAR(length=128),
            existing_nullable=True
        )
    else:
        with op.batch_alter_table("subscribes") as batch_op:
            batch_op.alter_column(
                'name',
                existing_type=sa.CHAR(length=128),
                type_=sa.VARCHAR(length=128),
                existing_nullable=True
            )


def downgrade() -> None:
    if context.dialect.name != "sqlite":
        op.alter_column('subscribes', 'name',
                        existing_type=sa.VARCHAR(length=128),
                        type_=sa.CHAR(length=128),
                        existing_nullable=True
                        )
    else:
        with op.batch_alter_table("subscribes") as batch_op:
            batch_op.alter_column(
                'name',
                existing_type=sa.VARCHAR(length=128),
                type_=sa.CHAR(length=128),
                existing_nullable=True
            )
