"""修改 entitlement_rules 表中的 course_name 字段

Revision ID: alter_entitlement_rules_course_name
Revises: 
Create Date: 2024-03-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'alter_entitlement_rules_course_name'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # SQLite 不支持直接修改列，需要创建新表并迁移数据
    # 1. 创建新表
    op.execute("""
        CREATE TABLE entitlement_rules_new (
            rule_id VARCHAR(50) NOT NULL, 
            course_id VARCHAR(50) NOT NULL,
            course_name VARCHAR(50) NOT NULL,
            ai_product_id VARCHAR(50) NOT NULL,
            product_name VARCHAR(20) NOT NULL,
            daily_limit INTEGER NOT NULL,
            validity_days INTEGER NOT NULL,
            created_at DATETIME,
            is_deleted BOOLEAN,
            PRIMARY KEY (rule_id)
        )
    """)
    
    # 2. 迁移数据
    op.execute("""
        INSERT INTO entitlement_rules_new 
        SELECT * FROM entitlement_rules
    """)
    
    # 3. 删除旧表
    op.execute("DROP TABLE entitlement_rules")
    
    # 4. 重命名新表
    op.execute("ALTER TABLE entitlement_rules_new RENAME TO entitlement_rules")
    
    # 5. 创建索引
    op.execute("CREATE INDEX ix_entitlement_rules_rule_id ON entitlement_rules (rule_id)")


def downgrade():
    # 回滚：将 course_name 字段的长度改回 20
    # 1. 创建新表
    op.execute("""
        CREATE TABLE entitlement_rules_new (
            rule_id VARCHAR(50) NOT NULL, 
            course_id VARCHAR(50) NOT NULL,
            course_name VARCHAR(20) NOT NULL,
            ai_product_id VARCHAR(50) NOT NULL,
            product_name VARCHAR(20) NOT NULL,
            daily_limit INTEGER NOT NULL,
            validity_days INTEGER NOT NULL,
            created_at DATETIME,
            is_deleted BOOLEAN,
            PRIMARY KEY (rule_id)
        )
    """)
    
    # 2. 迁移数据
    op.execute("""
        INSERT INTO entitlement_rules_new 
        SELECT * FROM entitlement_rules
    """)
    
    # 3. 删除旧表
    op.execute("DROP TABLE entitlement_rules")
    
    # 4. 重命名新表
    op.execute("ALTER TABLE entitlement_rules_new RENAME TO entitlement_rules")
    
    # 5. 创建索引
    op.execute("CREATE INDEX ix_entitlement_rules_rule_id ON entitlement_rules (rule_id)") 