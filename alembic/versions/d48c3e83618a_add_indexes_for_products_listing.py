"""add indexes for products listing

Revision ID: d48c3e83618a
Revises: 4d3a288ebf04
Create Date: 2025-09-21 15:45:45.970064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd48c3e83618a'
down_revision: Union[str, None] = '4d3a288ebf04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_products_created_at", "products", ["created_at"], unique=False)
    op.create_index("ix_products_price_cents", "products", ["price_cents"], unique=False)
    op.create_index("ix_products_brand_id", "products", ["brand_id"], unique=False)
    op.create_index("ix_products_category_id", "products", ["category_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_brand_id", table_name="products")
    op.drop_index("ix_products_price_cents", table_name="products")
    op.drop_index("ix_products_created_at", table_name="products")
