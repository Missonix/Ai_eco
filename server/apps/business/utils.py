import uuid
from datetime import datetime

def generate_uuid(prefix: str = None) -> str:
    """
    生成UUID
    :param prefix: UUID前缀，可选
    :return: 生成的UUID字符串
    """
    uuid_str = str(uuid.uuid4()).replace('-', '')
    if prefix:
        return f"{prefix}_{uuid_str}"
    return uuid_str

def generate_course_id() -> str:
    """生成课程ID"""
    return generate_uuid("COURSE")

def generate_ai_product_id() -> str:
    """生成AI产品ID"""
    return generate_uuid("AI")

def generate_rule_id() -> str:
    """生成权益规则ID"""
    return generate_uuid("RULE")

def generate_order_id() -> str:
    """生成订单ID"""
    return generate_uuid("ORDER")

def generate_entitlement_id() -> str:
    """生成用户权益ID"""
    return generate_uuid("ENT")
