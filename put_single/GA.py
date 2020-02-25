#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/8/13 23:31
# @File    : GA.py
# @Software: PyCharm

import random
from put_single.Life import Life


class GA(object):
    """遗传算法类"""

    def __init__(self, aCrossRate, aMutationRate, aLifeCount, aGeneLength, aMatchFun=lambda life: 1):
        self.crossRate = aCrossRate  # 交叉概率
        self.mutationRate = aMutationRate  # 突变概率
        self.lifeCount = aLifeCount  # 种群数量，就是每次我们在多少个城市序列里筛选，这里初始化为100
        self.geneLength = aGeneLength  # 其实就是城市数量
        self.matchFun = aMatchFun  # 适配函数
        self.lives = []  # 种群
        self.best = None  # 保存这一代中最好的个体
        self.generation = 1  # 一开始的是第一代
        self.crossCount = 0  # 一开始还没交叉过，所以交叉次数是0
        self.mutationCount = 0  # 一开始还没变异过，所以变异次数是0
        self.bounds = 0.0  # 适配值之和，用于选择时计算概率

        self.initPopulation()  # 初始化种群

    def initPopulation(self):
        """初始化种群"""
        self.lives = []
        for i in range(self.lifeCount):
            gene = []
            gene_1 = list(range(int(self.geneLength/2)))
            random.shuffle(gene_1)

            gene_2 = []
            for i in range(int(self.geneLength/2)):
                gene_2.append(i+8)
            random.shuffle(gene_2)

            gene.extend(gene_1)
            gene.extend(gene_2)

            life = Life(gene)
            self.lives.append(life)


    def judge(self):
        self.bounds = 0.0
        self.best = self.lives[0]
        for life in self.lives:
            life.score = self.matchFun(life)
            self.bounds += life.score
            if self.best.score < life.score:
                self.best = life

    def cross(self, parent1, parent2):
        index = random.randint(0,1)
        index1 = index2 = index3 = index4 = 0

        index1 = random.randint(0, int(self.geneLength/2) - 1)
        index2 = random.randint(index1, int(self.geneLength/2) - 1)

        index3 = random.randint(int(self.geneLength/2), self.geneLength - 1)
        index4 = random.randint(index3, self.geneLength - 1)

        tempGene = tempGene2 = []

        if index == 0:
            tempGene = parent2.gene[index1:index2]  # 交叉的基因片段
        elif index == 1:
            tempGene2 = parent2.gene[index3:index4]

        newGene = []
        p1len = 0

        for g in parent1.gene:
            if p1len == index1:
                newGene.extend(tempGene)  # 插入基因片段
                p1len += len(tempGene)

            if p1len == index3:
                newGene.extend(tempGene2)
                p1len += len(tempGene2)

            if g not in tempGene and g not in tempGene2:
                newGene.append(g)
                p1len += 1


        self.crossCount += 1
        return newGene

    def mutation(self, gene):
        index = random.randint(0,1)
        index1 = random.randint(0, int(self.geneLength/2) - 1)
        index2 = random.randint(0, int(self.geneLength/2) - 1)

        index3 = random.randint(int(self.geneLength/2), self.geneLength - 1)
        index4 = random.randint(int(self.geneLength/2), self.geneLength - 1)
        # 把这两个位置的城市互换
        if index == 0:
            gene[index1], gene[index2] = gene[index2], gene[index1]
        elif index == 1:
            gene[index3], gene[index4] = gene[index4], gene[index3]

        # 突变次数加1
        self.mutationCount += 1
        return gene

    def getOne(self):
        """选择一个个体"""
        # 产生0到（适配值之和）之间的任何一个实数
        r = random.uniform(0, self.bounds)
        for life in self.lives:
            r -= life.score
            if r <= 0:
                return life

        raise Exception("选择错误", self.bounds)

    def newChild(self):
        """产生新后的"""
        parent1 = self.getOne()
        rate = random.random()

        # 按概率交叉
        if rate < self.crossRate:
            # 交叉
            parent2 = self.getOne()
            gene = self.cross(parent1, parent2)

        else:
            gene = parent1.gene



        # 按概率突变
        rate = random.random()
        if rate < self.mutationRate:
            gene = self.mutation(gene)

        return Life(gene)

    def next(self):
        """产生下一代"""
        self.judge()  # 评估，计算每一个个体的适配值
        newLives = []
        newLives.append(self.best)  # 把最好的个体加入下一代
        while len(newLives) < self.lifeCount:
            newLives.append(self.newChild())
        self.lives = newLives
        self.generation += 1