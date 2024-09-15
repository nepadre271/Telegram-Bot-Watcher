"""Update PaymentsHistory

Revision ID: e53e895fca78
Revises: 9f2de88b89be
Create Date: 2024-09-15 16:00:36.167122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e53e895fca78'
down_revision: Union[str, None] = '9f2de88b89be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments_history', sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.drop_column('payments_history', 'provider_payment_charge_id')
    op.drop_column('payments_history', 'telegram_payment_charge_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments_history', sa.Column('telegram_payment_charge_id', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.add_column('payments_history', sa.Column('provider_payment_charge_id', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.drop_column('payments_history', 'extra_data')
    # ### end Alembic commands ###