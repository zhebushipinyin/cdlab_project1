#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import tkinter
from psychopy import visual, core, event, gui, parallel
import pandas as pd
import numpy as np
from pylink import *
import pylink

# 打开端口
parallel.setPortAddress(49408)

p = np.array([0.01, 0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99])
money = np.array([(25, 0), (50, 0), (75, 0), (100, 0), (150, 0), (200, 0), (400, 0), (800, 0),
                  (50, 25), (75, 50), (100, 50), (150, 50), (150, 100), (200, 100), (200, 150)])
# 读取初始数据
data = pd.read_csv('data.csv')
data_np = data.values
item = [0] * len(p)
for i in range(len(p)):
    item[i] = data.loc[data['p'] == p[i]].values
    np.random.shuffle(item[i])  # 打乱每个p下的项目
# 打乱总体
np.random.shuffle(item)
# 不要写[[0]*33]*5，这样赋值时会出错
block = [[0] * 33 for _ in range(5)]
# 每个block 33个trial 11（p）* 3(x1 x2)
for i in range(5):
    for j in range(11):
        block[i][3 * j] = item[j][i * 3]
        block[i][3 * j + 1] = item[j][i * 3 + 1]
        block[i][3 * j + 2] = item[j][i * 3 + 2]
    np.random.shuffle(block[i])
trial_set = [[0] * 33 for _ in range(5)]
for i in range(5):
    for j in range(33):
        p_value = block[i][j][0]
        v_x1 = block[i][j][1]
        v_x2 = block[i][j][2]
        trial_set[i][j] = {'p': p_value, 'v': (v_x1, v_x2)}

# 建立存储字典result
result = {'name': 'null', 'sex': 'null', 'age': 0, 'p': [], '1-p': [], 'x': [], 'y': [], 'id': [],'RT':[],
          'first_upper': [], 'first_lower': [], 'upper': [], 'lower': []}
clk_data = {'rt': [], 'gamble': [], 'y': [], 'reward': [], 'p': [], 'x1': [], 'x2': []}

# GUI
myDlg = gui.Dlg(title=u"实验")
myDlg.addText(u'被试信息')
myDlg.addField('name:')
myDlg.addField('sex:', choices=['male', 'female'])
myDlg.addField('age:', 21)
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
window = tkinter.Tk()
w = window.winfo_screenwidth()
h = window.winfo_screenheight()
if not myDlg.OK:
    core.quit()

result['name'] = ok_data[0]
result['sex'] = ok_data[1]
result['age'] = ok_data[2]

# eyelinktracker = EyeLink(trackeraddress=None)
eyelinktracker = EyeLink()
# 眼动仪
pylink.openGraphics((w, h), 32)
edfFileName = "%s.EDF" % result['name']
getEYELINK().openDataFile(edfFileName)
pylink.flushGetkeyQueue()
getEYELINK().setOfflineMode()
getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" % (w - 1, h - 1))
getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" % (w - 1, h - 1))
if getEYELINK().getTrackerVersion() == 2:
    getEYELINK().sendCommand("select_parser_configuration 0")
else:
    getEYELINK().sendCommand("saccade_velocity_threshold = 35")
    getEYELINK().sendCommand("saccade_acceleration_threshold = 9500")
getEYELINK().setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
getEYELINK().setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
getEYELINK().setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
getEYELINK().setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
getEYELINK().sendCommand("pupil_size_diameter = YES")
pylink.setCalibrationColors((255, 255, 255), (0, 0, 0))  # Sets the calibration target and background color
pylink.setTargetSize(int(w / 70), int(w / 300))
if getEYELINK().isConnected() and not getEYELINK().breakPressed():
    print('连接成功')
    getEYELINK().doTrackerSetup()
    while True:
        try:
            error = getEYELINK().doDriftCorrect(w // 2, h // 2, 1, 1)
            if error != 27:
                break
            else:
                getEYELINK().doTrackerSetup()
        except:
            getEYELINK().doTrackerSetup()
else:
    print('NO')
    getEYELINK().close()
    closeGraphics()

win = visual.Window(size=(w, h), fullscr=True, units='pix', color=[0, 0, 0])
closeGraphics()
card_pos = [[0 for i in range(3)]for i in range(7)]
table = [[0 for i in range(3)]for i in range(7)]
value = [[0 for i in range(3)]for i in range(7)]
gou_pos = [[0 for i in range(3)]for i in range(7)]
a = w/8.
b = h/14.4
# 各表格位置
for i in range(7):
    for j in range(3):
        x1 = j*a - a
        x2 = j*a
        y1 = 4*b - i*b
        y2 = 3*b - i*b
        card_pos[i][j] = ([[x1, y1], [x1, y2], [x2, y2], [x2, y1]])
        gou_pos[i][j] = ([int((x1+x2)/2), int((y1+y2)/2)])

# 建立表格
table_jiangquan = visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2)
table_jiangquan.vertices = [[-2*a, 4*b], [-2*a, 3*b], [-a, 3*b], [-a, 4*b]]
table_p = visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2)
table_p.vertices = [[-2*a, 3*b], [-2*a, -3*b], [-a, -3*b], [-a, 3*b]]

for m in range(7):
    for n in range(3):
        table[m][n] = visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2)
        table[m][n].vertices = card_pos[m][n]
# 建立文本
# 表头
title_text = [u"抽奖券", u"选择抽奖券", u"选择固定金额", u"固定金额"]
title = [0]*4
for i in range(len(title_text)):
    title[i] = visual.TextStim(win)
    title[i].text = title_text[i]
    title[i].height = h/36
    title[i].pos = (i*a - 1.5*a, 3.5*b)

# sureReward
sure_reward = [0]*6
for i in range(6):
    sure_reward[i] = visual.TextStim(win)
    sure_reward[i].pos = (1.5 * a, 2.5 * b - i * b)

# 确认
ok = visual.TextStim(win, text=u"确认", pos=(0, -4.5*b), height=h/36)
ok_shape = visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2)
ok_shape.vertices = [[-0.5*a, -5*b], [-0.5*a, -4*b], [0.5*a, -4*b], [0.5*a, -5*b]]

# 时间间隔
t_trial = {'t_fix': 0.5, 't_gamble': 1.5, 't_response': 1.5, 't_int': [2, 3, 4]}
# 文本
text_gamble_1 = visual.TextStim(win, height=64 * h / 720, pos=(int(-150*w/1024), 0))
text_gamble_2 = visual.TextStim(win, height=64 * h / 720, pos=(int(150*w/1024), 0))
text_p = visual.TextStim(win, height=64 * h / 720)
txt = visual.TextStim(win, height=64 * h / 720)
# 注视点
fix = visual.ImageStim(win, image="dot.png", size=64 * h / 720)
# 指导语
pic = visual.ImageStim(win, image="dot.png", size=(w, h))
# 对号
dui = visual.ImageStim(win, image="gou.png", size=32 * h / 720)

# 指导语
while True:
    for i in range(3):
        pic.image = 'pic/introduction_%s'%(i+1)
        pic.draw()
        win.flip()
        event.waitKeys(keyList=['space'])
        event.clearEvents()
    txt.text = '按【空格键】进入决策实验练习'
    txt.draw()
    win.flip()
    key = event.waitKeys(keyList=['space', 'escape'])
    if 'space' in key:
        event.clearEvents()
        break
    event.clearEvents()

myMouse = event.Mouse()
myMouse.setVisible(0)
flag = 0
x1 = 0
y1 = 0
ticket = visual.TextStim(win)
ticket.text = u"奖券"
ticket.pos = (-1.5 * a, 0)
ticket.height = h / 36
for ii in range(5):
    for jj in [random.randrange(0, 33, step=1)]:
        tr = ii*33+jj
        trial = trial_set[ii][jj]
        p_v = trial['p']
        (x, y) = trial['v']
        core.wait(0.1)
        fix.draw()
        win.flip()
        core.wait(0.5)
        text_p.text = "%s%%" % int(100 * p_v)
        text_p.draw()
        win.flip()
        core.wait(random.randrange(20, 41, step=1) / 10.)
        win.flip()
        core.wait(0.2)
        if random.randint(0, 1):
            text_gamble_1.text = "￥%s" % int(x)
            text_gamble_2.text = "￥%s" % int(y)
        else:
            text_gamble_1.text = "￥%s" % int(y)
            text_gamble_2.text = "￥%s" % int(x)
        text_gamble_1.draw()
        fix.draw()
        text_gamble_2.draw()
        win.flip()
        core.wait(3)
        win.flip()
        core.wait(0.2)
        for flag in range(2):
            myMouse.setVisible(1)
            col = [0]*2
            col[0] = [x-k*(x-y)/5 for k in range(6)]
            if flag == 1:
                col[1] = [x1-k*(x1-y1)/5 for k in range(6)]
            col_p = col[flag]
            state = 'running'
            value = [[0 for i in range(3)] for i in range(7)]
            while True:
                if state == 'running':
                    for i in range(1, 7):
                        for j in range(2):
                            if table[i][j].contains(myMouse) and value[i][j] == 0:
                                pass
                            elif value[i][j] == 0:
                                pass
                            else:
                                dui.pos = gou_pos[i][j]
                                dui.draw()
                            if myMouse.isPressedIn(table[i][j]) and value[i][j] == 0:
                                value[i] = [0]*3
                                value[i][j] = 1
                                dui.pos = gou_pos[i][j]
                                dui.draw()
                            table[i][j].draw()
                    for j in range(3):
                        table[0][j].draw()
                    for i in range(7):
                        table[i][2].draw()
                    for i in range(4):
                        title[i].draw()
                    table_jiangquan.draw()
                    table_p.draw()
                    ticket.draw()
                    for i in range(6):
                        sure_reward[i].text = u"%s元"%int(col_p[i])
                        sure_reward[i].height = h/30
                        sure_reward[i].draw()
                    key = event.getKeys(["escape"])
                    if "escape" in key:
                        state = "exit"
                    check = [0]*(7-1)
                    now = [0]*(7-1)
                    point = 0
                    for i in range(1, 7):
                        point += value[i][0]+value[i][1]
                        if value[i][1] == 1:
                            now[i-1] = 1
                    j = 0
                    while j <= 5:
                        if value[j+1][1] == 1:
                            check[j] = 1
                        else:
                            break
                        j += 1
                    if check == now and point == 6 and check[5] + check[0] == 1:
                        if ok_shape.contains(myMouse):
                            ok_shape.fillColor = [-1, -1, -1]
                            ok_shape.opacity = 0.3
                        else:
                            ok_shape.fillColor = [0, 0, 0]
                            ok_shape.opacity = 1
                        ok_shape.draw()
                        ok.draw()
                    win.flip()
                    # 获得被试所选转折点
                    if check == now and myMouse.isPressedIn(ok_shape):
                        change = sum(check)
                        x1 = col_p[change-1]
                        y1 = col_p[change]
                        # 标记为第二轮
                        state = "quit"
                # 进入下一层
                if state == "quit":
                    win.flip()
                    break
                # 强行终止
                if state == "exit":
                    win.flip()
                    win.close()
                    core.quit()
            win.flip()
            if flag == 1:
                myMouse.setVisible(0)
            core.wait(0.5)
        # trial结束
        core.wait(random.randrange(20, 41, step=1) / 10. - 0.5)

# 开始屏
txt.text = '按【空格键】开始实验'
txt.draw()
win.flip()
event.waitKeys(keyList=['space'])
event.clearEvents()
parallel.setData(0)
myMouse = event.Mouse()
myMouse.setVisible(0)
# 开始
flag = 0
x1 = 0
y1 = 0
clk = core.Clock()
clk2 = core.Clock()
for ii in range(5):
    # 开始记录眼动数据
    getEYELINK().startRecording(1, 1, 1, 1)
    # 如果记录的是双眼的数据则改为记录左眼；
    eye_used = getEYELINK().eyeAvailable()
    if eye_used == 1:
        getEYELINK().sendMessage("EYE_USED 1 RIGHT")
    elif eye_used == 0 or eye_used == 2:
        getEYELINK().sendMessage("EYE_USED 0 LEFT")
        eye_used = 0
    core.wait(0.1)
    startTime = currentTime()
    getEYELINK().sendMessage("SYNCTIME %d" % (currentTime() - startTime))
    for jj in range(33):
        myMouse.setVisible(0)
        tr = ii*33+jj
        # 每个trial包含先后两次
        result['id'].append(tr)
        trial = trial_set[ii][jj]
        p_v = trial['p']
        (x, y) = trial['v']
        message = "record_status_message 'Trial n%s, p:%s, x:%s, y:%s'" % (tr, p_v, x, y)
        getEYELINK().sendCommand(message)
        msg = "TRIALID p:%s. x:%s. y:%s, n:%s" % (p_v, x, y, tr)
        getEYELINK().sendMessage(msg)
        cmd = data.loc[(data.p == p_v) & (data.x1 == x) & (data.x2 == y)].index[0] + 4
        # 发送信号
        parallel.setData(int(cmd))
        core.wait(0.1)
        parallel.setData(0)
        result['p'].append(p_v)
        result['1-p'].append(1-p_v)
        result['x'].append(x)
        result['y'].append(y)
        # 注视点
        fix.draw()
        win.flip()
        core.wait(0.5)
        # 概率
        text_p.text = "%s%%" % int(100 * p_v)
        text_p.draw()
        win.flip()
        # 发送信号-概率
        parallel.setData(1)
        getEYELINK().sendMessage('Probability p:%s, n:%s' % (p_v, tr))
        core.wait(random.randrange(60, 81, step=1) / 20.)
        parallel.setData(0)
        win.flip()
        core.wait(0.2)
        # 随机金额对位置
        if random.randint(0, 1):
            text_gamble_1.text = "￥%s" % int(x)
            text_gamble_2.text = "￥%s" % int(y)
        else:
            text_gamble_1.text = "￥%s" % int(y)
            text_gamble_2.text = "￥%s" % int(x)
        # 金额对
        text_gamble_1.draw()
        fix.draw()
        text_gamble_2.draw()
        win.flip()
        # 发送信号-金额
        parallel.setData(2)
        getEYELINK().sendMessage('Value x:%s, y:%s, n:%s' % (int(x), int(y), tr))
        core.wait(3)
        parallel.setData(0)
        win.flip()
        core.wait(0.2)
        # 选择
        for flag in range(2):
            myMouse.setVisible(1)
            # 发送信号-选择
            parallel.setData(3)
            getEYELINK().sendMessage('Reward %s begin' % flag)
            # 建立确定金额阵列
            col = [0]*2
            col[0] = [x-k*(x-y)/5 for k in range(6)]
            if flag == 1:
                col[1] = [x1-k*(x1-y1)/5 for k in range(6)]
            col_p = col[flag]
            state = 'running'
            value = [[0 for i in range(3)] for i in range(7)]
            clk.reset()
            clk2.reset()
            while True:
                if state == 'running':
                    for i in range(1, 7):
                        for j in range(2):
                            if table[i][j].contains(myMouse) and value[i][j] == 0:
                                pass
                            elif value[i][j] == 0:
                                pass
                            else:
                                dui.pos = gou_pos[i][j]
                                dui.draw()
                            if myMouse.isPressedIn(table[i][j]) and value[i][j] == 0:
                                clk_data['rt'].append(clk2.getTime())
                                clk_data['gamble'].append(i)
                                clk_data['reward'].append(col_p[i-1])
                                clk_data['y'].append(j)
                                clk_data['p'].append(p_v)
                                clk_data['x1'].append(x)
                                clk_data['x2'].append(y)
                                clk2.reset()
                                value[i] = [0]*3
                                value[i][j] = 1
                                dui.pos = gou_pos[i][j]
                                dui.draw()
                            table[i][j].draw()
                    for j in range(3):
                        table[0][j].draw()
                    for i in range(7):
                        table[i][2].draw()
                    for i in range(4):
                        title[i].draw()
                    table_jiangquan.draw()
                    table_p.draw()
                    ticket.draw()
                    for i in range(6):
                        sure_reward[i].text = u"%s元"%int(col_p[i])
                        sure_reward[i].height = h/30
                        sure_reward[i].draw()

                    key = event.getKeys(["escape"])
                    if "escape" in key:
                        state = "exit"
                    check = [0]*(7-1)
                    now = [0]*(7-1)
                    point = 0
                    for i in range(1, 7):
                        point += value[i][0]+value[i][1]
                        if value[i][1] == 1:
                            now[i-1] = 1
                    j = 0
                    while j <= 5:
                        if value[j+1][1] == 1:
                            check[j] = 1
                        else:
                            break
                        j += 1
                    if check == now and point == 6 and check[5] + check[0] == 1:
                        if ok_shape.contains(myMouse):
                            ok_shape.fillColor = [-1, -1, -1]
                            ok_shape.opacity = 0.3
                        else:
                            ok_shape.fillColor = [0, 0, 0]
                            ok_shape.opacity = 1
                        ok_shape.draw()
                        ok.draw()
                    win.flip()
                    # 获得被试所选转折点
                    if check == now and myMouse.isPressedIn(ok_shape):
                        rt = clk.getTime()
                        clk_data['rt'].append([clk2.getTime()])
                        clk_data['gamble'].append(-1)
                        clk_data['reward'].append(-1)
                        clk_data['y'].append(-1)
                        clk_data['p'].append(p_v)
                        clk_data['x1'].append(x)
                        clk_data['x2'].append(y)
                        change = sum(check)
                        x1 = col_p[change-1]
                        y1 = col_p[change]
                        if flag == 0:
                            result['first_upper'].append(x1)
                            result['first_lower'].append(y1)
                        else:
                            result['upper'].append(x1)
                            result['lower'].append(y1)
                        # 标记为第二轮
                        print(col_p)
                        print(flag, x1, y1)
                        state = "quit"
                # 进入下一层
                if state == "quit":
                    win.flip()
                    break
                # 强行终止
                if state == "exit":
                    win.flip()
                    win.close()
                    core.quit()
            win.flip()
            myMouse.setVisible(0)
            parallel.setData(0)
            getEYELINK().sendMessage("Reward %s end"%flag)
            result['RT'].append(rt)
            if flag == 1:
                myMouse.setVisible(0)
            core.wait(0.5)
        # trial结束
        parallel.setData(250)
        # 本次trial结束
        getEYELINK().sendMessage("TRIALID p:%s, x:%s, y:%s, n:%s end" % (p_v, x, y, tr))
        ret_value = getEYELINK().getRecordingStatus()
        # trial完成
        if ret_value == TRIAL_OK:
            getEYELINK().sendMessage("TRIAL OK")
        core.wait(0.1)
        core.wait(random.randrange(20, 41, step=1) / 10.- 0.6)
    getEYELINK().stopRecording()
    if ii != 4:
        # 休息 10s强制
        txt.text = "请休息，按【空格键】继续"
        txt.draw()
        win.flip()
        core.wait(10)
        key = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in key:
            break
        elif 'space' in key:
            pass

if getEYELINK() != None:
    # File transfer and cleanup!
    getEYELINK().setOfflineMode()
    msecDelay(500)
    getEYELINK().closeDataFile()
    getEYELINK().receiveDataFile(edfFileName, edfFileName)
    getEYELINK().close()

with open("exp_data\\%s.csv" % (result['name']+time.strftime("%H-%M-%S")), 'a') as exp_data:
    exp_data.write(
        'id'+','+'name'+','+'age'+','+'sex'+',' + 'p' + ',' + '1-p'+','+'x1'+',' + 'x2'+',' + 'RT'+',' + 'first_upper' +
        ',' + 'first_lower'+','+'upper'+',' + 'lower'+'\n')
    for i in range(len(result['id'])):
        exp_data.write(str(result['id'][i]) + ',' + result['name'] + ',' + str(result['age']) + ',' + result['sex']
                       + ',' + str(result['p'][i])+ ',' + str(result['1-p'][i]) + ',' + str(result['x'][i]) + ',' + str(result['y'][i])+ ',' + str(result['RT'][i])
                       + ',' + str(result['first_upper'][i]) + ',' + str(result['first_lower'][i]) + ',' +
                       str(result['upper'][i]) + ',' + str(result['lower'][i]) + '\n'
                       )

with open("exp_data\\RT%s.csv" % (result['name'] + time.strftime("%H-%M-%S")), 'a') as exp_data:
    exp_data.write(
        'name' + ',' + 'age' + ',' + 'sex' + ',' + 'p' + ',' + 'x1' + ',' + 'x2' + ',' + 'RT' + ',' +
        'gamble' + ',' + 'y' + ',' + 'reward' + '\n')
    for i in range(len(clk_data['p'])):
        exp_data.write(result['name'] + ',' + str(result['age']) + ',' + result['sex']
                       + ',' + str(clk_data['p'][i]) + ',' + str(clk_data['x1'][i]) + ',' + str(clk_data['x2'][i]) + ','
                       + str(clk_data['rt'][i]) + ',' + str(clk_data['gamble'][i]) + ',' + str(clk_data['y'][i]) + ',' +
                       str(clk_data['reward'][i]) + '\n'
                       )

# 实验结束
txt.text = "实验结束！"
win.flip()
core.wait(1)
getEYELINK().close()
closeGraphics()
win.close()
core.quit()


