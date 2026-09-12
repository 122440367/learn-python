# 基本数据类型
# 整数（int）、浮点数(float)、字符串(str)、布尔值(boolean)、空值(NoneType)

# 使用type()函数查看数据类型
a = 1
print(type(a)) # 查看 a 变量存储的数据的类型
print(type("Hello!"))
print(type(1.1))
print(type(None))
print(type(True))

# isinstance()函数检查一个对象是否是指定类型的实例
# isinstance(数据, 类型)
print(isinstance(a, int)) # 检查 a 是否是 int 类型的实例
print(isinstance(a, float))