# -*- coding: utf-8 -*-

import uuid


def get_uuid1():
    """生成基于计算机主机ID和当前时间的UUID"""
    return uuid.uuid1()


def get_uuid4():
    """随机生成一个UUID"""
    return uuid.uuid4()


for i in range(10):
    print(get_uuid1())

print("\n")

for i in range(10):
    print(get_uuid4())
