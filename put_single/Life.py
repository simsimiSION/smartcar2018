#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/7/22 1:17
# @File    : Life.py
# @Software: PyCharm

SCORE_NONE = -1


class Life(object):
    """个体类"""

    def __init__(self, aGene=None):
        self.gene = aGene
        self.score = SCORE_NONE