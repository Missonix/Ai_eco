import pandas as pd

# 读取Excel文件
df = pd.read_excel(
    "coursesignupReport.xlsx",
    sheet_name=0,  # 第一个sheet
    usecols=["B", "F", "N", "Z", "AL"],  # 按列字母选择
    header=1,  # 数据从第二行开始（跳过标题行）
    names=["手机号", "课程标题", "三方支付单号", "支付时间", "退款状态"]  # 自定义列名
)

# 保存结果到新Excel
df.to_excel("提取结果.xlsx", index=False)

# 打印前5行验证
print(df.head())