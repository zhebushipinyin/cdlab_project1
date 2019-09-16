#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import visual, core, event, gui
import tkinter
import pandas as pd
import numpy as np
import random

# p及value Wu 1999
p = np.array([0.01, 0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99])
value = np.array([(25, 0), (50, 0), (75, 0), (100, 0), (150, 0), (200, 0), (400, 0), (800, 0),
                  (50, 25), (75, 50), (100, 50), (150, 50), (150, 100), (200, 100), (200, 150)])

# 实验刺激预处理 N = 11(p)*15(value)*2 = 330 = 2*5(block)*33(trial)
# 读取初始数据
data = pd.read_csv('data.csv')
data_np = data.values
item = [0] * len(p)
for i in range(len(p)):
    item[i] = data.loc[data['p'] == p[i]].values
    np.random.shuffle(item[i])  # 打乱每个p下的项目
# 打乱总体
np.random.shuffle(item)
block = [[0] * 33 for _ in range(5)]
# 每个block 33个trial 11（p）* 3(x1 x2)
for i in range(5):
    for j in range(11):
        block[i][3 * j] = item[j][i * 3]
        block[i][3 * j + 1] = item[j][i * 3 + 1]
        block[i][3 * j + 2] = item[j][i * 3 + 2]
    np.random.shuffle(block[i])
# 分配8个sure_reward （间隔分配）
sure_asignment = np.random.randint(0, 2, size=(5, 33))
part2 = [[0] * 33 for _ in range(5)]
part1 = [[0] * 33 for _ in range(5)]
sur = [0, 1]
for i in range(5):
    for j in range(33):
        p_value = block[i][j][0]
        v_x1 = block[i][j][1]
        v_x2 = block[i][j][2]
        sur[0] = [block[i][j][x] for x in [3, 5, 7, 9]]
        sur[1] = [block[i][j][x] for x in [4, 6, 8, 10]]
        if sure_asignment[i][j] == 0:
            part1[i][j] = {'p': p_value, 'v': (v_x1, v_x2), 'sure_reward': sur[0]}
            part2[i][j] = {'p': p_value, 'v': (v_x1, v_x2), 'sure_reward': sur[1]}
        else:
            part1[i][j] = {'p': p_value, 'v': (v_x1, v_x2), 'sure_reward': sur[1]}
            part2[i][j] = {'p': p_value, 'v': (v_x1, v_x2), 'sure_reward': sur[0]}
# 将part2逆序与part1拼接
trial_set = part1 + part2[::-1]
# 最终数据格式： 2*5(block)*33(trial)
# for each trial： dict{'p', 'v' = (x1, x2), 'sure_reward':[r1,r2,r3,r4]}


(w, h) = (1280, 720)
win = visual.Window(size=(w, h), fullscr=True, units='pix', color=[0, 0, 0])
myMouse = event.Mouse()
myMouse.setVisible(0)
clk = core.Clock()
# 时间间隔
t_trial = {'t_fix': 0.5, 't_gamble': 1.5, 't_response': 1.5, 't_int': [2, 3, 4]}
# 文本
text_gamble_1 = visual.TextStim(win, height=64*h/720, pos=(-150, 0))
text_gamble_2 = visual.TextStim(win, height=64*h/720, pos=(150, 0))
text_gamble2 = visual.TextStim(win, height=64*h/720, pos=(-240,0))
text_reward = visual.TextStim(win, height=64*h/720, pos=(240,0))
text_p = visual.TextStim(win, height=64*h/720)
txt = visual.TextStim(win, height=64*h/720)
# 注视点
fix = visual.ImageStim(win, image="dot.png", size=64)

for i in range(len(trial_set)):
    for j in range(33):
        # 数据
        p_v = trial_set[i][j]['p']
        x1, x2 = trial_set[i][j]['v']
        sure_reward = trial_set[i][j]['sure_reward']
        np.random.shuffle(sure_reward)
        # 注视点
        fix.draw()
        win.flip()
        core.wait(t_trial['t_fix'])
        # Gamble
        text_p.text = "%s%%" % int(100*p_v)
        text_p.draw()
        win.flip()
        core.wait(3)
        win.flip()
        core.wait(0.1)
        #
        text_gamble_1.text = "￥%s" % int(x1)
        text_gamble_2.text = "￥%s" % int(x2)
        text_gamble_1.draw()
        fix.draw()
        text_gamble_2.draw()
        win.flip()
        core.wait(3)
        win.flip()
        core.wait(1)
        # sure_reward & response
        for each in sure_reward:
            # text_gamble2.text = "%s%%，￥%s  %s%%，￥%s" % (int(100 * p_v), int(x1), int(100*(1 - p_v)), int(x2))
            text_gamble2.text = '奖券'
            text_reward.text = "￥%s" % int(each)
            text_gamble2.draw()
            text_reward.draw()
            win.flip()
            key = event.waitKeys(keyList=['space', 'f', 'j', 'escape'], maxWait=3)
            if not key:
                pass
            elif 'escape' in key:
                win.close()
                core.quit()
            elif 'f' in key:
                text_gamble2.color = [0, 1, 0]
            elif 'j' in key:
                text_reward.color = [0, 1, 0]
            text_gamble2.draw()
            text_reward.draw()
            win.flip()
            text_gamble2.color = [1, 1, 1]
            text_reward.color = [1, 1, 1]
            core.wait(0.1)
            event.clearEvents()
            win.flip()
            core.wait(0.1)
        # 空屏
        win.flip()
        core.wait(random.randrange(20, 41, step=1)/10.)
    if i != 4:
        # 休息 30s强制+30
        txt.text = "请休息，按【空格键】继续"
        txt.draw()
        win.flip()
        core.wait(30)
        key = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in key:
            break
# 实验结束
txt.text = "实验结束！"
win.flip()
core.wait(1)
win.close()
core.quit()