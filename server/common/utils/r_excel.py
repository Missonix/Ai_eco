import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.logger import setup_logger
import os
import tempfile

logger = setup_logger('excel_utils')

class ExcelReader:
    """Excel表格读取工具类"""
    
    @staticmethod
    def process_uploaded_excel(file_content: bytes) -> List[Dict[str, Any]]:
        """
        处理上传的Excel文件内容
        
        Args:
            file_content: Excel文件的二进制内容
            
        Returns:
            List[Dict]: 处理后的订单数据列表
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # 读取Excel文件
                df = pd.read_excel(temp_file_path, engine='openpyxl')
                
                # 获取所有列名
                columns = df.columns.tolist()
                
                # 提取指定列的数据
                # 2:手机号 6:课程标题 14:三方支付单号 26:支付时间 38:退款状态
                selected_columns = [columns[1], columns[5], columns[13], columns[25], columns[37]]
                print("##########################################")
                print(selected_columns)
                print("##########################################")
                # 创建新的DataFrame只包含选定的列
                selected_df = df[selected_columns]
                
                # 重命名列
                selected_df.columns = ['手机号', '课程标题', '三方支付单号', '支付时间', '退款状态']
                
                # 删除空行
                selected_df = selected_df.dropna(how='all')
                
                # 重置索引
                selected_df = selected_df.reset_index(drop=True)
                
                # 转换为订单数据列表
                orders = []
                for _, row in selected_df.iterrows():
                    # 处理支付时间
                    purchase_time = row['支付时间']
                    if isinstance(purchase_time, str):
                        try:
                            purchase_time = datetime.strptime(purchase_time, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            # 尝试其他常见格式
                            try:
                                purchase_time = datetime.strptime(purchase_time, '%Y-%m-%d')
                            except ValueError:
                                logger.error(f"无法解析支付时间: {purchase_time}")
                                continue
                    
                    # 处理退款状态
                    is_refund = True if str(row['退款状态']).strip() == '已退款' else False
                    
                    # 处理手机号
                    phone = str(row['手机号']).strip()
                    # 处理可能的浮点数格式
                    if '.' in phone:
                        phone = phone.split('.')[0]
                    if not phone.isdigit() or len(phone) != 11:
                        logger.error(f"无效的手机号: {phone}")
                        continue
                    
                    # 处理课程名称（标准化处理）
                    course_name = str(row['课程标题']).strip()
                    # 移除所有空格
                    course_name = course_name.replace(' ', '')
                    # 标准化课程名称格式
                    if '【' in course_name and '】' in course_name:
                        # 提取课程名称和学苑名称
                        parts = course_name.split('【')
                        main_name = parts[0].strip()
                        academy = parts[1].replace('】', '').strip()
                        # 重新组合，确保格式一致
                        course_name = f"{main_name}【{academy}】"
                    
                    # 处理订单号
                    order_id = str(row['三方支付单号']).strip()
                    if not order_id:
                        logger.error("订单号为空")
                        continue
                    
                    order = {
                        'order_id': order_id,
                        'phone': phone,
                        'course_name': course_name,
                        'purchase_time': purchase_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_refund': is_refund,
                        'is_generate': False
                    }
                    orders.append(order)
                print("r_excel##########################################")
                print(orders)
                print("##########################################")
                return orders
                
            finally:
                # 删除临时文件
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.error(f"删除临时文件失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"处理Excel文件失败: {str(e)}")
            raise
