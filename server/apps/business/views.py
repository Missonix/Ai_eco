from robyn import Request, Response, status_codes
from core.response import ApiResponse
from core.middleware import error_handler, request_logger, auth_required, admin_required
from core.logger import setup_logger
from common.utils.r_excel import ExcelReader
from apps.business import crud as business_crud
from core.database import AsyncSessionLocal
import json
from datetime import datetime

logger = setup_logger('business_views')

@error_handler
@request_logger
# @auth_required
# @admin_required
async def upload_orders_excel(request: Request) -> Response:
    """
    上传Excel文件并处理订单数据
    """
    try:
        # 记录请求信息
        logger.info(f"收到文件上传请求: {request.headers}")
        
        # 获取上传的文件
        files = request.files
        logger.info(f"上传的文件列表: {files}")
        
        if not files:
            logger.error("未找到上传的文件")
            return ApiResponse.validation_error("请上传Excel文件")
            
        # 获取第一个文件对象
        file_name = next(iter(files.keys()))
        file_content = files[file_name]
        
        if not file_name or not file_content:
            logger.error("未找到上传的文件")
            return ApiResponse.validation_error("请上传Excel文件")
            
        # 记录文件信息
        logger.info(f"上传的文件信息: filename={file_name}")
            
        # 检查文件类型
        if not file_name.endswith(('.xlsx', '.xls')):
            logger.error(f"文件类型不正确: {file_name}")
            return ApiResponse.validation_error("请上传Excel格式的文件(.xlsx或.xls)")
            
        # 处理Excel文件
        try:
            # 确保文件内容是字节类型
            if not isinstance(file_content, bytes):
                file_content = file_content.encode('utf-8')
                
            orders = ExcelReader.process_uploaded_excel(file_content)
            
            if not orders:
                logger.error("Excel文件中没有有效的订单数据")
                return ApiResponse.error(
                    message="Excel文件中没有有效的订单数据",
                    status_code=400
                )
                
            # 保存订单数据
            async with AsyncSessionLocal() as db:
                success_count = 0
                error_count = 0
                error_messages = []
                
                for order in orders:
                    try:
                        order_id = order.get("order_id")
                        phone = order.get("phone")
                        course_name = order.get("course_name")
                        purchase_time = order.get("purchase_time")
                        is_refund = order.get("is_refund")
                        if is_refund is False:
                            order["is_refund"] = "无"
                            is_refund = "无"
                        if is_refund is True:
                            order["is_refund"] = "已退款"
                            is_refund = "已退款"
                        
                        if not all([order_id, phone, course_name, purchase_time, is_refund]):
                            error_message = f"订单 {order_id} 数据不完整"
                            error_messages.append(error_message)
                            error_count += 1
                            # 记录错误订单
                            await business_crud.create_upload_error_order(db, {
                                "order_id": order_id or "未知",
                                "error_message": error_message
                            })
                            continue
                            
                        # 标准化课程名称（移除多余空格）
                        course_name = ' '.join(course_name.split())
                        
                        # 转换is_refund为布尔值
                        is_refund_bool = True if is_refund == "已退款" else False
                        
                        # 转换purchase_time为datetime对象
                        try:
                            purchase_time_dt = datetime.strptime(purchase_time, "%Y-%m-%d %H:%M:%S")
                        except ValueError as e:
                            error_message = f"订单 {order_id} 购买时间格式错误"
                            error_messages.append(error_message)
                            error_count += 1
                            # 记录错误订单
                            await business_crud.create_upload_error_order(db, {
                                "order_id": order_id,
                                "error_message": error_message
                            })
                            continue
                            
                        # 根据课程名称获取课程ID
                        course = await business_crud.get_course_by_filter(db, {"course_name": course_name})
                        if not course:
                            error_message = f"订单 {order_id} 的课程 {course_name} 不存在"
                            error_messages.append(error_message)
                            error_count += 1
                            # 记录错误订单
                            await business_crud.create_upload_error_order(db, {
                                "order_id": order_id,
                                "error_message": error_message
                            })
                            continue
                        
                        # 检查订单号是否已存在
                        existing_order = await business_crud.get_order(db, order_id)
                        if existing_order:
                            error_message = f"订单 {order_id} 已存在"
                            error_messages.append(error_message)
                            error_count += 1
                            # 记录错误订单
                            await business_crud.create_upload_error_order(db, {
                                "order_id": order_id,
                                "error_message": error_message
                            })
                            continue
                        
                        # 准备订单数据
                        order_data = {
                            "order_id": order_id,
                            "phone": phone,
                            "course_id": course.course_id,
                            "purchase_time": purchase_time_dt,
                            "is_refund": is_refund_bool,
                            "is_deleted": False
                        }
                        
                        # 创建订单
                        await business_crud.create_order(db, order_data)
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"保存订单失败: {str(e)}")
                        error_message = f"订单 {order.get('order_id', '未知')} 保存失败: {str(e)}"
                        error_messages.append(error_message)
                        error_count += 1
                        # 记录错误订单
                        await business_crud.create_upload_error_order(db, {
                            "order_id": order.get('order_id', '未知'),
                            "error_message": error_message
                        })
                        
                # 返回处理结果
                return ApiResponse.success(
                    data={
                        "total": len(orders),
                        "success": success_count,
                        "error": error_count,
                        "error_messages": error_messages
                    },
                    message=f"成功导入 {success_count} 条订单数据，失败 {error_count} 条"
                )
                
        except Exception as e:
            logger.error(f"处理Excel文件失败: {str(e)}")
            return ApiResponse.error(
                message="处理Excel文件失败",
                status_code=500
            )
            
    except Exception as e:
        logger.error(f"上传订单Excel文件失败: {str(e)}")
        return ApiResponse.error(
            message="上传订单Excel文件失败",
            status_code=500
        ) 