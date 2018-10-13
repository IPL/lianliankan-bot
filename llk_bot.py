# -*- coding: utf-8 -*-
import time
import serial
from PIL import Image

from common import config, screenshot, plan, log_util
from common.auto_adb import auto_adb

game_config = config.open_accordant_config()

x = game_config['top_left_point']['x']
y = game_config['top_left_point']['y']
width = game_config['block_size']['width']
height = game_config['block_size']['height']
interval = game_config['block_size']['interval']

boardWidth = game_config['board_size']['boardWidth']
boardHeight = game_config['board_size']['boardHeight']

sampleRate = game_config['sample_rate']

# 通过adb发送点击事件，或者是串口通讯驱动电机和滑台
control_by_adb = game_config['control_by_adb']

# 电机、丝杆、滑台、屏幕的物理参数
pixelToMM = 0.05935
pulseCount = 1600
loopMM = 4
dirRow = -1
dirCol = -1

# 串口通讯的参数
port_name = 'COM3'
baud_rate = 115200
timeout_conf = 2000

dict = {}

if (control_by_adb == False):
    ser = serial.Serial(port_name, baud_rate, timeout=timeout_conf)

def colorEqual(tuple1, tuple2):
    if ((tuple1[0] - tuple2[0]) * (tuple1[0] - tuple2[0]) + (tuple1[1] - tuple2[1]) * (tuple1[1] - tuple2[1]) + (tuple1[2] - tuple2[2]) * (tuple1[2] - tuple2[2]) < 60):
        return True
    else:
        return False

def getColor(indexI, indexJ):
    key = str(indexI) + "_" + str(indexJ)
    return dict.get(key)

def agvColor(img, img_curr_x_left_top, img_curr_y_left_top, width, height, indexI, indexJ):
    key = str(indexI) + "_" + str(indexJ)
    if (key in dict):
        tupleRGB = dict.get(key)
    else:
        totalCount = width * height / (sampleRate * sampleRate)
        count = 0;
        r = 0;
        b = 0;
        g = 0;
        for i in range(0, width // sampleRate):
            for j in range(0, height // sampleRate):
                tuple = img.getpixel((img_curr_x_left_top + i * sampleRate, img_curr_y_left_top + j * sampleRate))
                if ((tuple[1] >= 10 and tuple[1] <= 20) and (tuple[2] >= 60 and tuple[2] <= 70) and (tuple[3] >= 110 and tuple[3] <= 120)):
                    count = count + 1
                else:
                    r += tuple[1]
                    b += tuple[2]
                    g += tuple[3]
        tupleRGB = (r / (totalCount - count), g / (totalCount - count), b / (totalCount - count))
        dict[key] = tupleRGB
        print("AVG RGB %d, %d, %d, %d, %d" % (indexI, indexJ, tupleRGB[0], tupleRGB[1], tupleRGB[2]))
    return tupleRGB

def myTouch(adb, row, col):
    if (control_by_adb):
        posX = x + col * (width + interval) + width / 2
        posY = y + row * (height + interval) + height /2
        cmd = 'shell input tap {x} {y}'.format(
            x=posX,
            y=posY
        )
        adb.run(cmd)
        print("%s: %s: %s: %s" % (row, col, posX, posY))

def commandContent(from_row, from_col, to_row, to_col):
    if (control_by_adb == False):
        pulseRow = (to_row - from_row) * (width + interval) * pixelToMM / loopMM * pulseCount * dirRow
        pulseCol = (to_col - from_col) * (height + interval) * pixelToMM / loopMM * pulseCount * dirCol
        s = "M01 %d %d 0 0 \r\n" % (pulseCol, pulseRow)
        ser.write(s.encode('utf-8'))
        s = "M01 0 0 %d 0 \r\n" % (1200)
        ser.write(s.encode('utf-8'))
        s = "M01 0 0 %d 0 \r\n" % (-1200)
        ser.write(s.encode('utf-8'))

def oneRound(adb, dict):

    dict.clear()

    log_util.print_log("开始截屏")
    img = screenshot.pull_screenshot()
    log_util.print_log("完成截屏")

    for i in range(0, boardWidth):
        for j in range(0, boardHeight):
            img_curr_x_left_top = x + i * (width + interval)
            img_curr_y_left_top = y + j * (height + interval)
            img_curr_x_mid      = img_curr_x_left_top + width / 2
            img_curr_y_mid      = img_curr_y_left_top + height / 2
            agvColor(img, img_curr_x_left_top, img_curr_y_left_top, width, height, i, j)

    log_util.print_log("完成颜色值计算")

    maxCategory = 1
    id_matrix = [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]
    id_matrix[0][0] = maxCategory

    for i in range(0, boardWidth):
        for j in range(0, boardHeight):
            if (id_matrix[i][j] == 0):
                maxCategory = maxCategory + 1
                id_matrix[i][j] = maxCategory
            for m in range(0, boardWidth):
                for n in range(0, boardHeight):
                    if (m != i or n != j):
                        if (id_matrix[m][n] == 0 and id_matrix[i][j] != 0 and colorEqual(getColor(i, j), getColor(m,n))):
                            id_matrix[m][n] = id_matrix[i][j] 

    log_util.print_log("完成识别")

    previous_row = 0
    previous_col = 0

    while True:

        print('---one step---')
        plan.print_matrix(id_matrix)

        # find one step solution
        one_step = plan.solve_matrix_one_step(id_matrix)
        if not one_step:
            commandContent(previousRow, previousCol, 0, 0)
            print('solved')
            return None

        from_col, from_row, to_col, to_row = one_step
        id_matrix[from_col][from_row] = 0
        id_matrix[to_col][to_row] = 0

        myTouch(adb, from_row, from_col)
        myTouch(adb, to_row, to_col)
        
        print("%s, %s -> %s, %s" % (from_row, from_col, to_row, to_col))
        commandContent(previous_row, previous_col, from_row, from_col)
        commandContent(from_row, from_col, to_row, to_col)

        previous_row = to_row
        previous_col = to_col

def main():
    while True:
        raw_input_A = input("Again: ")
        print(raw_input_A)
        oneRound(adb, dict)

if __name__ == '__main__':
    adb = auto_adb()
    adb.test_device()
    try:
        # yes_or_no()
        main()
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('谢谢使用')
        exit(0)
