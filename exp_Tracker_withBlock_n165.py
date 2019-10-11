#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pylink import *
import pylink
from psychopy import visual, core, event, gui
import tkinter
import pandas as pd
import numpy as np
import random
import time


def end_trial():
    '''Ends recording: adds 100 msec of data to catch final events'''
    endRealTimeMode()
    pumpDelay(100)
    getEYELINK().stopRecording()
    while getEYELINK().getkey():
        pass


# p及value Wu 1999
p = np.array([0.01, 0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99])
value = np.array([(25, 0), (50, 0), (75, 0), (100, 0), (150, 0), (200, 0), (400, 0), (800, 0),
                  (50, 25), (75, 50), (100, 50), (150, 50), (150, 100), (200, 100), (200, 150)])
# 创建记录文件
result = {'id': [], 'p': [], 'x1': [], 'x2': [], 'reward': [], 'reaction_time': [], 'is_right': [], 'choose_gamble': []}
tr_result = {'id': [], 'p': [], 'x1': [], 'x2': [], 'reward': [], 'reaction_time': [], 'is_right': [], 'choose_gamble': []}
# gui
myDlg = gui.Dlg(title="实验")
myDlg.addText('被试信息')
myDlg.addField('姓名:')
myDlg.addField('性别:', choices=['male', 'female'])
myDlg.addField('年龄:', 21)
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
window = tkinter.Tk()
(w, h) = (1920, 1080)
w = window.winfo_screenwidth()
h = window.winfo_screenheight()
if not myDlg.OK:
    core.quit()
result['name'] = ok_data[0]
result['sex'] = ok_data[1]
result['age'] = ok_data[2]
tr_result['name'] = ok_data[0]
tr_result['sex'] = ok_data[1]
tr_result['age'] = ok_data[2]
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
# 不要写[[0]*33]*5，这样赋值时会出错
block = [[0] * 33 for _ in range(5)]
# 每个block 33个trial 11（p）* 3(x1 x2)
for i in range(5):
    for j in range(11):
        block[i][3 * j] = item[j][i * 3]
        block[i][3 * j + 1] = item[j][i * 3 + 1]
        block[i][3 * j + 2] = item[j][i * 3 + 2]
    np.random.shuffle(block[i])
# 练习数据
tr = [0]*11
for j in range(11):
    p_value = item[j][0][0]
    v_x1 = item[j][0][1]
    v_x2 = item[j][0][2]
    sur = [item[j][0][x] for x in [3, 4, 5, 6, 7, 8, 9, 10]]
    np.random.shuffle(sur)
    pos_gamble = np.random.randint(0, 2, size=8)
    tr[j] = {'p': p_value, 'v': (v_x1, v_x2), 'sure_reward': sur, 'gamble_pos': pos_gamble}

# 刺激位置，0gamble左, 1右
gamble_pos = np.random.randint(0, 2, size=(5, 33, 4))
trial_set = [[0] * 33 for _ in range(5)]
for i in range(5):
    for j in range(33):
        p_value = block[i][j][0]
        v_x1 = block[i][j][1]
        v_x2 = block[i][j][2]
        sur = [block[i][j][x] for x in [3, 4, 5, 6, 7, 8, 9, 10]]
        np.random.shuffle(sur)
        pos_gamble = np.concatenate((gamble_pos[i][j], 1-np.flipud(gamble_pos[i][j])))
        trial_set[i][j] = {'p': p_value, 'v': (v_x1, v_x2), 'sure_reward': sur, 'gamble_pos': pos_gamble}

# 最终数据格式： 5(block)*33(trial)
# for each trial： dict{'p', 'v' = (x1, x2), 'sure_reward':[r1,r2,r3,r4,...r8]}


RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2

# eyelinktracker = EyeLink(trackeraddress=None)
eyelinktracker = EyeLink()
# 眼动仪
pylink.openGraphics((w, h), 32)
# Opens the EDF file.
edfFileName = "%s.EDF" % result['name']
getEYELINK().openDataFile(edfFileName)
pylink.flushGetkeyQueue()
getEYELINK().setOfflineMode()
# Gets the display surface and sends a message to EDF file;
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
getEYELINK().sendCommand("pupil_size_diameter = True");
pylink.setCalibrationColors((255, 255, 255), (0, 0, 0))  # Sets the calibration target and background color
pylink.setTargetSize(int(w / 70), int(w / 300))
# select best size for calibration target
pylink.setCalibrationSounds("", "", "")
pylink.setDriftCorrectSounds("", "off", "off")

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
# psychopy 窗口
win = visual.Window(size=(w, h), fullscr=True, units='pix', color=[0, 0, 0])
# 关闭眼动仪窗口
closeGraphics()
myMouse = event.Mouse()
myMouse.setVisible(0)
# 时间间隔
t_trial = {'t_fix': 0.5, 't_gamble': 1.5, 't_response': 1.5, 't_int': [2, 3, 4]}
posx = int(250*w/1024)
# 文本
text_gamble_1 = visual.TextStim(win, height=64 * h / 720, pos=(int(-150*w/1024), 0))
text_gamble_2 = visual.TextStim(win, height=64 * h / 720, pos=(int(150*w/1024), 0))
text_gamble = visual.TextStim(win, height=64 * h / 720, pos=(-posx, 0))
text_reward = visual.TextStim(win, height=64 * h / 720, pos=(posx, 0))
text_p = visual.TextStim(win, height=64 * h / 720)
txt = visual.TextStim(win, height=64 * h / 720)
# 注视点
fix = visual.ImageStim(win, image="dot.png", size=64)
# 指导语
pic = visual.ImageStim(win, image="dot.png", size=(w, h))
# 开始屏
txt.text = '按【空格键】开始实验'
txt.draw()
win.flip()
event.waitKeys(keyList=['space'])
event.clearEvents()
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


clk = core.Clock()
myMouse.setVisible(0)
for j in range(len(tr)):
    # 数据
    p_v = tr[j]['p']
    x1, x2 = tr[j]['v']
    sure_reward = tr[j]['sure_reward']
    np.random.shuffle(sure_reward)
    # 注视点
    fix.draw()
    win.flip()
    core.wait(t_trial['t_fix'])
    # 概率
    text_p.text = "%s%%" % int(100 * p_v)
    text_p.draw()
    win.flip()
    core.wait(random.randrange(20, 41, step=1) / 10.)
    win.flip()
    core.wait(0.2)
    # 随机金额对位置
    if random.randint(0, 1):
        text_gamble_1.text = "￥%s" % int(x1)
        text_gamble_2.text = "￥%s" % int(x2)
    else:
        text_gamble_1.text = "￥%s" % int(x2)
        text_gamble_2.text = "￥%s" % int(x1)
    # 金额对
    text_gamble_1.draw()
    fix.draw()
    text_gamble_2.draw()
    win.flip()
    core.wait(3)
    win.flip()
    core.wait(0.2)
    # sure_reward & response
    for m in range(8):
        each = sure_reward[m]
        # gamble & reward 位置
        is_right = tr[j]['gamble_pos'][m]
        if is_right == 0:
            text_gamble.pos = (-posx, 0)
            text_reward.pos = (posx, 0)
        else:
            text_gamble.pos = (posx, 0)
            text_reward.pos = (-posx, 0)
        tr_result['p'].append(p_v)
        tr_result['x1'].append(x1)
        tr_result['x2'].append(x2)
        tr_result['is_right'].append(is_right)
        tr_result['reward'].append(each)

        text_gamble.text = '奖券'
        text_reward.text = "￥%s" % int(each)
        text_gamble.draw()
        text_reward.draw()
        win.flip()
        clk.reset()
        # 当前奖励
        key = event.waitKeys(keyList=['f', 'j', 'escape'], maxWait=3)
        rt = clk.getTime()
        if not key:
            tr_result['choose_gamble'].append(-1)
            tr_result['reaction_time'].append(-3)
            pass
        elif 'escape' in key:
            win.close()
            core.quit()
        elif is_right:
            tr_result['reaction_time'].append(rt)
            # 如果赌局在右
            if 'f' in key:
                text_reward.color = [0, 1, 0]
                tr_result['choose_gamble'].append(0)
            elif 'j' in key:
                text_gamble.color = [0, 1, 0]
                tr_result['choose_gamble'].append(1)
        elif not is_right:
            tr_result['reaction_time'].append(rt)
            # 如果赌局在左
            if 'f' in key:
                text_gamble.color = [0, 1, 0]
                tr_result['choose_gamble'].append(1)
            elif 'j' in key:
                text_reward.color = [0, 1, 0]
                tr_result['choose_gamble'].append(0)
        # 按键 Reward结束
        text_gamble.draw()
        text_reward.draw()
        win.flip()
        text_gamble.color = [1, 1, 1]
        text_reward.color = [1, 1, 1]
        core.wait(0.1)
        event.clearEvents()
        win.flip()
        core.wait(0.1)
    # 本次trial结束
    # 空屏
    win.flip()
    core.wait(random.randrange(20, 41, step=1) / 10.)
# 写练习数据
with open("exp_data\\TR%s.csv" % (result['name']+time.strftime("%H-%M-%S")), 'a') as exp_data:
    exp_data.write(
        'id' + ',' + 'name' + ',' + 'age' + ',' + 'sex' + ',' + 'p' + ',' + 'x1' + ',' + 'x2' + ','
        + 'reward' + ',' + 'is_right' + ',' + 'choose_gamble' + ',' + 'reaction_time' + '\n')
    for i in range(len(tr_result['id'])):
        exp_data.write(str(tr_result['id'][i]) + ',' + tr_result['name'] + ',' + str(tr_result['age']) + ',' + tr_result['sex']
                       + ',' + str(tr_result['p'][i]) + ',' + str(tr_result['x1'][i]) + ',' + str(tr_result['x2'][i])
                       + ',' + str(tr_result['reward'][i]) + ',' + str(tr_result['is_right'][i]) + ',' +
                       str(tr_result['choose_gamble'][i]) + ',' + str(tr_result['reaction_time'][i]) + '\n'
                       )

txt.text = '按【空格键】开始正式实验'
txt.draw()
win.flip()
event.waitKeys(keyList=['space'])
event.clearEvents()
clk = core.Clock()
for i in range(len(trial_set)):
    myMouse.setVisible(0)
    for j in range(33):
        # 开始记录眼动数据
        getEYELINK().startRecording(1, 1, 1, 1)
        # 如果记录的是双眼的数据则改为记录左眼；
        eye_used = getEYELINK().eyeAvailable()
        if eye_used == RIGHT_EYE:
            getEYELINK().sendMessage("EYE_USED 1 RIGHT")
        elif eye_used == LEFT_EYE or eye_used == BINOCULAR:
            getEYELINK().sendMessage("EYE_USED 0 LEFT")
            eye_used = LEFT_EYE
        core.wait(0.1)
        startTime = currentTime()
        getEYELINK().sendMessage("SYNCTIME %d" % (currentTime() - startTime))

        k = 33*i + j
        # 数据
        p_v = trial_set[i][j]['p']
        x1, x2 = trial_set[i][j]['v']
        message = "record_status_message 'Trial n%s, p:%s, x:%s, y:%s'" % (k, p_v, x1, x2)
        getEYELINK().sendCommand(message)
        msg = "TRIALID p:%s. x:%s. y:%s, n:%s" % (p_v, x1, x2, k)
        getEYELINK().sendMessage(msg)
        sure_reward = trial_set[i][j]['sure_reward']
        np.random.shuffle(sure_reward)
        # 注视点
        fix.draw()
        win.flip()
        core.wait(t_trial['t_fix'])
        # 概率
        text_p.text = "%s%%" % int(100 * p_v)
        text_p.draw()
        win.flip()
        getEYELINK().sendMessage('Probability p:%s, n:%s' % (p_v, k))
        core.wait(random.randrange(20, 41, step=1) / 10.)
        win.flip()
        core.wait(0.2)
        # 随机金额对位置
        if random.randint(0, 1):
            text_gamble_1.text = "￥%s" % int(x1)
            text_gamble_2.text = "￥%s" % int(x2)
        else:
            text_gamble_1.text = "￥%s" % int(x2)
            text_gamble_2.text = "￥%s" % int(x1)
        # 金额对
        text_gamble_1.draw()
        fix.draw()
        text_gamble_2.draw()
        win.flip()
        getEYELINK().sendMessage('Value x:%s, y:%s, n:%s'% (int(x1), int(x2), k))
        core.wait(3)
        win.flip()
        core.wait(0.2)
        # sure_reward & response
        for m in range(8):
            each = sure_reward[m]
            # gamble & reward 位置
            is_right = trial_set[i][j]['gamble_pos'][m]
            if is_right == 0:
                text_gamble.pos = (-posx, 0)
                text_reward.pos = (posx, 0)
            else:
                text_gamble.pos = (posx, 0)
                text_reward.pos = (-posx, 0)

            result['p'].append(p_v)
            result['x1'].append(x1)
            result['x2'].append(x2)
            result['id'].append(k)
            result['is_right'].append(is_right)
            result['reward'].append(each)

            text_gamble.text = '奖券'
            text_reward.text = "￥%s" % int(each)
            text_gamble.draw()
            text_reward.draw()
            win.flip()
            clk.reset()
            getEYELINK().sendMessage('Reward %s begin' % int(each))
            # 当前奖励
            key = event.waitKeys(keyList=['f', 'j', 'escape'], maxWait=3)
            rt = clk.getTime()
            if not key:
                getEYELINK().sendMessage("TRIAL ABORTED")
                result['choose_gamble'].append(-1)
                result['reaction_time'].append(-3)
                pass
            elif 'escape' in key:
                getEYELINK().sendMessage("EXPERIMENT ABORTED")
                if getEYELINK() != None:
                    # File transfer and cleanup!
                    getEYELINK().setOfflineMode()
                    msecDelay(500)
                    # Close the file and transfer it to Display PC
                    getEYELINK().closeDataFile()
                    getEYELINK().receiveDataFile(edfFileName, edfFileName)
                    getEYELINK().close()
                win.close()
                core.quit()
            elif is_right:
                result['reaction_time'].append(rt)
                # 如果赌局在右
                if 'f' in key:
                    text_reward.color = [0, 1, 0]
                    result['choose_gamble'].append(0)
                elif 'j' in key:
                    text_gamble.color = [0, 1, 0]
                    result['choose_gamble'].append(1)
            elif not is_right:
                result['reaction_time'].append(rt)
                # 如果赌局在左
                if 'f' in key:
                    text_gamble.color = [0, 1, 0]
                    result['choose_gamble'].append(1)
                elif 'j' in key:
                    text_reward.color = [0, 1, 0]
                    result['choose_gamble'].append(0)
            # 按键 Reward结束
            msg = "Reward %s end" % int(each)
            getEYELINK().sendMessage(msg)
            text_gamble.draw()
            text_reward.draw()
            win.flip()
            text_gamble.color = [1, 1, 1]
            text_reward.color = [1, 1, 1]
            core.wait(0.1)
            event.clearEvents()
            win.flip()
            core.wait(0.1)
        # 本次trial结束
        msg = "TRIALID p:%s, x:%s, y:%s, n:%s end" % (p_v, x1, x2, k)
        getEYELINK().sendMessage(msg)
        ret_value = getEYELINK().getRecordingStatus()
        # trial完成
        if ret_value == TRIAL_OK:
            getEYELINK().sendMessage("TRIAL OK")
        getEYELINK().stopRecording()
        # 空屏
        win.flip()
        core.wait(random.randrange(20, 41, step=1) / 10.)
    if i != 4:
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
    # Close the file and transfer it to Display PC
    getEYELINK().closeDataFile()
    getEYELINK().receiveDataFile(edfFileName, edfFileName)
    getEYELINK().close()

# 写数据
with open("exp_data\\%s.csv" % (result['name']+time.strftime("%H-%M-%S")), 'a') as exp_data:
    exp_data.write(
        'id' + ',' + 'name' + ',' + 'age' + ',' + 'sex' + ',' + 'p' + ',' + 'x1' + ',' + 'x2' + ','
        + 'reward' + ',' + 'is_right' + ',' + 'choose_gamble' + ',' + 'reaction_time' + '\n')
    for i in range(len(result['id'])):
        exp_data.write(str(result['id'][i]) + ',' + result['name'] + ',' + str(result['age']) + ',' + result['sex']
                       + ',' + str(result['p'][i]) + ',' + str(result['x1'][i]) + ',' + str(result['x2'][i])
                       + ',' + str(result['reward'][i]) + ',' + str(result['is_right'][i]) + ',' +
                       str(result['choose_gamble'][i]) + ',' + str(result['reaction_time'][i]) + '\n'
                       )
# 实验结束
txt.text = "实验结束！"
win.flip()
core.wait(1)
getEYELINK().close()
closeGraphics()
win.close()
core.quit()

