# 单引号定义
st1 = 'Hello World!'

# 双引号定义
st2 = "Hello World!"

# 三引号定义（多行字符串）
st3 = """
Hello
World
!
"""

# 输出 It's a good day! 这句话
# 使用转义字符 \' 来表示单引号
st4 = 'It\'s a good day!'
print(st4)

# 其他转义
# \n 换行
# \t 制表符
# \" 双引号

# 字符串连接
print(st1 + " " + st4)  # 输出 Hello World! It's a good day!
# 特别注意：字符串连接时，必须确保连接的对象都是字符串类型，否则会报错

# 字符串转换 str()
# eg
num = 123
print(str(num) + "转换成为字符串") # 将整数转换为字符串并拼接

# 字符串的格式化
name = "Alice"
print("My name is %s." % name)  # 使用 %s 占位符格式化字符串
# 使用 f"内容{变量}" 进行格式化
print(f"My name is {name}.") # 使用 f-string 格式化字符串

