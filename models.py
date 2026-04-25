# Python 类定义示例
from typing import Any
from pydantic import BaseModel


class Dog:
    """一个简单的狗类，演示类的基本用法"""

    # 类变量，所有实例共享
    species = "犬科动物"

    def __init__(self, name, age):
        """初始化方法（构造函数）"""
        self.name = name  # 实例变量
        self.age = age

    def bark(self):
        """实例方法"""
        print(f"{self.name}：汪汪！")

    def get_info(self):
        """返回狗的信息"""
        return f"{self.name}，{self.age}岁"


# 使用类
dog1 = Dog("旺财", 3)
dog2 = Dog("小白", 5)

dog1.bark()
print(dog1.get_info())
print(f"{dog2.name} 是 {Dog.species}")




class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
