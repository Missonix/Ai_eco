"""add ai_product_id to user_entitlements

Revision ID: add_ai_product_id_to_user_entitlements
Revises: 
Create Date: 2025-04-22 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_ai_product_id_to_user_entitlements'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 添加 ai_product_id 字段
    op.add_column('user_entitlements', sa.Column('ai_product_id', sa.String(50), nullable=True))
    
    # 更新现有记录，从权益规则表中获取对应的 ai_product_id
    op.execute("""
        UPDATE user_entitlements 
        SET ai_product_id = (
            SELECT ai_product_id 
            FROM entitlement_rules 
            WHERE entitlement_rules.rule_id = user_entitlements.rule_id
        )
    """)

def downgrade():
    # 删除 ai_product_id 字段
    op.drop_column('user_entitlements', 'ai_product_id') 