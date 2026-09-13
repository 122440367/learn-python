# 运算符：算数运算符、赋值运算符、逻辑运算符、比较运算符
# 算数运算符
# + - * / // % **

# 算数运算符优先级
# **
# * / // %
# + -

# 例
x = input("请输入第一个数x：")
y = input("请输入第二个数y：")
print("x + y =",float(x) + float(y))
print("x - y =",float(x) - float(y))

# 浮点数运算可能会损失精度.
# Decimal 精确十进制计算
from decimal import Decimal
print("x + y =",Decimal(x) + Decimal(y))
print("x - y =",Decimal(x) - Decimal(y))
