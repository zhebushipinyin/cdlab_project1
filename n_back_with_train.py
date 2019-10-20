#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import visual, core, event, gui
import pandas as pd
import numpy as np
import random, tkinter


rd = random.randint(1, 2)
data = pd.read_csv('nback_%s.csv' % rd)
data_tr = pd.read_csv('nback_%s.csv' % (3-rd))
data['RT'] = data['RT'].astype('float')
# gui
myDlg = gui.Dlg(title="Nback实验")
myDlg.addText('被试信息')
myDlg.addField('姓名:')
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
window = tkinter.Tk()
(w, h) = (1920, 1080)
w = window.winfo_screenwidth()
h = window.winfo_screenheight()
win = visual.Window(size=(w, h), fullscr=True, units='pix', color=[0, 0, 0])
myMouse = event.Mouse()
myMouse.setVisible(0)
M_text = visual.TextStim(win, height=80*h/720)
# 指导语
pic = visual.ImageStim(win, image="dot.png", size=(w, h))
# 指导语
while True:
    for i in range(5):
        pic.image = 'pic/Nback_%s.png'%i
        pic.draw()
        win.flip()
        event.waitKeys(keyList=['space'])
        event.clearEvents()
    M_text.text = '按【空格键】进入N-back练习'
    M_text.draw()
    win.flip()
    key = event.waitKeys(keyList=['space', 'escape'])
    if 'space' in key:
        event.clearEvents()
        break
    event.clearEvents()

ISI = core.StaticPeriod(screenHz=60)
ISI.start(1)  # start a period of 0.5s
ISI.complete()
clk = core.Clock()

for j in range(4):
    for k in range(13):
        clk.reset()
        event.clearEvents()
        index = 52*1 + 13*j + k
        M_text.color = [1, 1, 1]
        if data['trial'][index] == 1:
            M_text.text = '%s-Back' % data_tr['item'][index]
            M_text.draw()
            win.flip()
            core.wait(4)
        else:
            M_text.text = '%s' % data_tr['item'][index]
            M_text.draw()
            win.flip()
            clk.reset()
            t = clk.getTime()
            flag = 0
            while t < 2:
                t = clk.getTime()
                if t < 0.5:
                    M_text.draw()
                    win.flip()
                else:
                    win.flip()
                if flag == 0:
                    key = event.getKeys(keyList=['f', 'j', 'escape'], timeStamped=clk)
                else:
                    continue
                if not key:
                    pass
                elif 'escape' in key[-1][0]:
                    win.close()
                    core.quit()
M_text.text = '按【空格键】进入N-back实验'
M_text.draw()
win.flip()
key = event.waitKeys(keyList=['space', 'escape'])
if 'space' in key:
    event.clearEvents()
ISI = core.StaticPeriod(screenHz=60)
ISI.start(1)  # start a period of 0.5s
ISI.complete()
# 重复四次
for i in range(4):
    # 四个game block
    if i in [1, 2, 3]:
        M_text.text = '请休息，按空格键继续'
        M_text.draw()
        win.flip()
        keys = event.waitKeys(keyList=['space'])
    for j in range(4):
        for k in range(13):
            clk.reset()
            event.clearEvents()
            index = 52*i + 13*j + k
            M_text.color = [1, 1, 1]
            if data['trial'][index] == 1:
                M_text.text = '%s-Back' % data['item'][index]
                M_text.draw()
                win.flip()
                core.wait(4)
            else:
                M_text.text = '%s' % data['item'][index]
                M_text.draw()
                win.flip()
                clk.reset()
                t = clk.getTime()
                flag = 0
                while t < 2:
                    t = clk.getTime()
                    if t < 0.5:
                        M_text.draw()
                        win.flip()
                    else:
                        win.flip()
                    if flag == 0:
                        key = event.getKeys(keyList=['f', 'j', 'escape'], timeStamped=clk)
                    else:
                        continue
                    t = clk.getTime()
                    if key == []:
                        pass
                    elif 'escape' in key[-1][0]:
                        win.close()
                        core.quit()
                    elif ('f' in key[-1][0])or('j' in key[-1][0]):
                        # M_text.color = [0, 1, 0]
                        flag = 1
                        data['RT'][index] = t
                        print(t)
                        if 'f' in key[-1][0]:
                            data['response'][index] = 1
                            if data['is_same'][index] == 1:
                                data['score'][index] = 1
                        else:
                            data['response'][index] = 0
data.to_csv('exp_data/Nback_%s.csv'%ok_data[0])
