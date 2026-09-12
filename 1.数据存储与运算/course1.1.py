#注释
# 快速注释 crtl + /
# 从print开始
print("输出。。。")
print("hello world")
print("------")

# 等效于
print("输出。。。");print("hello world");print("------")
#
# #其他数据类型
# print(None)
# print(123)
# print(True)
# print(False)

# 标识符规范
# 1.只能包含字母、数字和下划线，不能以数字开头
# 2.不能使用Python的关键字和内置函数名
# 3.建议使用有意义的名字，使用小写字母和下划线分隔单词（snake_case）
# 4.变量名不能包含空格和特殊字符
# 5.变量名不能以数字开头
# 6.变量名不能使用Python的保留字（如if、else、for等）
# 7.变量名应该具有描述性，能够清晰地表达变量的用途和含义
# 变量命名示例
my_variable = 10
user_name = "Alice"
# 不规范的变量命名示例
#1variable = 20  # 错误：变量名不能以数字开头
#my-variable = 30  # 错误：变量名不能包含连字符

# 变量交换
a = 10
b = 20
c = a
a = b
b = c
print(a,b)

# 三变量交换练习
# a,b,c 赋给 c,a,b
a = 100
b = 200
c = 300
d = c
c = a
a = b
b = d
print(c,a,b)