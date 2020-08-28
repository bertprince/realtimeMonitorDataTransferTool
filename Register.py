# coding: utf-8
from random import random

import win32api
import pyDes
from binascii import b2a_hex, a2b_hex
import base64
import os


def getCVolumeSerialNumber():
    CVolumeSerialNumber = win32api.GetVolumeInformation("C:\\")[1]
    # print(CVolumeSerialNumber)
    if CVolumeSerialNumber:
        return str(CVolumeSerialNumber)
    else:
        return 0


def DesEncrypt(str):
    k = pyDes.des(Des_Key, pyDes.CBC, Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
    encryptStr = k.encrypt(str)
    string = base64.b64encode(encryptStr)
    # print(string)
    return string  # 转base64编码返回


def DesDecrypt(string):
    string = base64.b64decode(string)
    k = pyDes.des(Des_Key, pyDes.CBC, Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
    decryptStr = k.decrypt(string)
    # print(decryptStr)
    return decryptStr


Des_Key = "514--514"  # Key
Des_IV = "83689193"  # 自定IV向量

def CheckAuthorized():
    if os.path.isfile("./conf.ini"):
        print ("存在注册文件。")
        f = open("./conf.ini")
        # print(f.read())
        code = f.read()
        return code
    else:
        return 'Null'
        print("无注册文件，请联系管理员")
def regist():
    localCode = getCVolumeSerialNumber()
    print("是否对如下机器进行注册：%s?" % localCode)
    judge = input("[Y/N]")
    if judge == "Y" or judge == "y":
        if os.path.isfile("./conf.ini"):
            f = open("./conf.ini",'w')
            encryptCode=DesEncrypt(localCode)
            f.write(str(encryptCode))
            f.close()
        else:
            f = open("./conf.ini", 'w')
            encryptCode = DesEncrypt(localCode)
            f.write(str(encryptCode))
            f.close()
    else:
        newCode = input("请输入新机器码：")
        f = open("./conf.ini", 'w')
        encryptCode = DesEncrypt(newCode)
        f.write(str(encryptCode))
        f.close()
    print("Done")


def Register():
    if os.path.isfile('conf.bin'):
        with open('conf.bin', 'rb') as fp:
            key = a2b_hex(fp.read())
            print(key)
        serialnumber = getCVolumeSerialNumber()
        decryptstr = DesDecrypt(key).decode('utf8')
        print(decryptstr)
        if serialnumber in decryptstr:
            if 'Buy' in decryptstr:
                print('>> Buy')
                print(">> 验证完成")
                return 1
            elif 'Trial' in decryptstr:
                print('>> Trial')
                return 2
    rand = str(random.randrange(1, 1000))
    serialnumber = getCVolumeSerialNumber() + rand
    print(serialnumber)
    encryptstr = DesEncrypt(serialnumber).decode('utf8')
    print(">> 序列号:", encryptstr)
    while True:
        key = input(">> 验证码:")
        try:
            decryptstr = DesDecrypt(key.encode('utf8')).decode('utf8')
            print(decryptstr)
            if serialnumber in decryptstr:
                if 'Buy' in decryptstr:
                    print('>> Buy')
                    with open('conf.bin', 'wb') as fp:
                        fp.write(b2a_hex(key.encode('utf8')))
                        print(">> 验证完成")
                    return 1
                elif 'Trial' in decryptstr:
                    print('>> Trial')
                    return 2
        except Exception as e:
            print(e)
            print(">> 输入错误")
            continue


