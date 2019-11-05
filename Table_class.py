#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 表格对象，包含psychopy文本刺激txt，形状刺激shape，选择标记dui（对号），表格位置ver
class Table:
    def __init__(self, text, shape, choose, ver):
        self.txt = text
        self.shape = shape
        self.dui = choose
        self.shape.vertices = ver
        self.ver = ver
        self.x = (ver[0][0] + ver[1][0] + ver[2][0] + ver[3][0]) / 4
        self.y = (ver[0][1] + ver[1][1] + ver[2][1] + ver[3][1]) / 4
        self.dui.pos = (self.x, self.y)
        self.txt.pos = (self.x, self.y)

    # 镜像
    def t(self, mirror=0, inverse=0):
        if mirror:
            if not inverse:
                self.dui.pos = (-self.x, self.y)
                self.txt.pos = (-self.x, self.y)
                self.shape.vertices = ([-self.ver[0][0], self.ver[0][1]],
                                       [-self.ver[1][0], self.ver[1][1]],
                                       [-self.ver[2][0], self.ver[2][1]],
                                       [-self.ver[3][0], self.ver[3][1]]
                                       )
            else:
                self.dui.pos = (-self.x, -self.y)
                self.txt.pos = (-self.x, -self.y)
                self.shape.vertices = ([-self.ver[0][0], -self.ver[0][1]],
                                       [-self.ver[1][0], -self.ver[1][1]],
                                       [-self.ver[2][0], -self.ver[2][1]],
                                       [-self.ver[3][0], -self.ver[3][1]]
                                       )
        elif inverse:
            self.dui.pos = (self.x, -self.y)
            self.txt.pos = (self.x, -self.y)
            self.shape.vertices = ([self.ver[0][0], -self.ver[0][1]],
                                   [self.ver[1][0], -self.ver[1][1]],
                                   [self.ver[2][0], -self.ver[2][1]],
                                   [self.ver[3][0], -self.ver[3][1]]
                                   )
        else:
            self.dui.pos = (self.x, self.y)
            self.txt.pos = (self.x, self.y)
            self.shape.vertices = self.ver
