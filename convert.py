'''
Created on Aug 13, 2012

@author: ebrahim radi
'''

board_width = 205
board_height = 135
point_counter = 0
delayTime = 0.3
minDistance = 0.5

import os
import re, math
from optparse import OptionParser, OptionError
from os.path import expanduser,dirname
from os import system

def readFile(filePath):
    svgFile = open(expanduser(filePath))
    fileContent = svgFile.read()
    fileContent = fileContent.replace("\n"," ")
    return fileContent

def writeFile(fileContent, filePath):
    mb4File = open(expanduser(filePath), mode='w')
    mb4File.write(fileContent)

def readImageSize(fileContent):
    height = re.search("(height=\")([0-9.]+)(pt\")", fileContent)
    height = float(height.group(2))
    width = re.search("(width=\")([0-9.]+)(pt\")", fileContent)
    width = float(width.group(2))
    return (width, height)

def pt2mm(point=1):
    return point * 0.343

def getImage2BoardScale(imageSize):
    myScale = 1
    if imageSize[1] > board_height or imageSize[0] > board_width:
        height_scale = board_height / imageSize[1]
        width_scale = board_width / imageSize[0]
        if height_scale < width_scale:
            myScale = height_scale
        else:
            myScale = width_scale
    return myScale

def findMergeAllPath(fileContent):
    matches = re.findall("<path d=\"m|M[0-9 (l|L)+-]*z",fileContent)
    fileContent = ""
    for match in matches:
        fileContent += match.replace("<path d=\"","")
    fileContent = fileContent.replace("z", " z")
    return fileContent

def normalize(mFloat, mPrecision):
    mPrecision = ".{0}f".format(mPrecision)
    return float(format(mFloat,mPrecision))

def getRawPoints(fileContent):
    myDict = {}
    myList = []
    index = 0
    while index < len(fileContent):
        if fileContent[index] == "M":
            myDict["M"] = []
            temp_int = ""
            index += 1
            count_1_2 = 1
            while fileContent[index] != "l":
                if fileContent[index].isdigit() or fileContent[index] == "-":
                    temp_int += fileContent[index]
                elif fileContent[index] == " ":
                    if count_1_2 == 2 and len(temp_int) > 0:
                        myDict["M"].append(float(temp_int))
                        count_1_2 = 1
                    elif count_1_2 == 1:
                        myDict["M"].append(float(temp_int))
                        count_1_2 = 2
                    temp_int = ""
                index += 1
            index -=1
        elif fileContent[index] == "l":
            myDict["l"] = []
            temp_int = ""
            index += 1
            count_1_2 = 1
            while fileContent[index] != "z":
                if fileContent[index].isdigit() or fileContent[index] == "-":
                    temp_int += fileContent[index]
                elif fileContent[index] == " ":
                    if count_1_2 == 2 and len(temp_int) > 0:
                        myDict["l"][-1].append(float(temp_int))
                        count_1_2 = 1
                    elif count_1_2 == 1:
                        myDict["l"].append([])
                        myDict["l"][-1].append(float(temp_int))
                        count_1_2 = 2
                    temp_int = ""
                index += 1
            index -= 1
            myList.append(myDict.copy())
            myDict = {}
        elif fileContent[index] == "m":
            myDict["m"] = []
            temp_int = ""
            index += 1
            count_1_2 = 1
            while fileContent[index] != "l":
                if fileContent[index].isdigit() or fileContent[index] == "-":
                    temp_int += fileContent[index]
                elif fileContent[index] == " ":
                    if count_1_2 == 2 and len(temp_int) > 0:
                        myDict["m"].append(float(temp_int))
                        count_1_2 = 1
                    elif count_1_2 == 1:
                        myDict["m"].append(float(temp_int))
                        count_1_2 = 2
                    temp_int = ""
                index += 1
            index -=1
        index += 1
    return myList

def scaleTransferPoints(mList, mScale, mTransferX=0,mTransferY=0):
    myDict = {}
    myList = []
    for moves in mList:
        if "M" in moves.keys():
            myDict["M"] = []
            myDict["M"].append((moves["M"][0] * mScale) + mTransferX)
            myDict["M"].append((moves["M"][1] * mScale) + mTransferY)
            myDict["l"] = []
            for points in moves["l"]:
                myDict["l"].append([])
                myDict["l"][-1].append(points[0] * mScale)
                myDict["l"][-1].append(points[1] * mScale)
        elif "m" in moves.keys():
            myDict["m"] = []
            myDict["m"].append(moves["m"][0] * mScale)
            myDict["m"].append(moves["m"][1] * mScale)
            myDict["l"] = []
            for points in moves["l"]:
                myDict["l"].append([])
                myDict["l"][-1].append(points[0] * mScale)
                myDict["l"][-1].append(points[1] * mScale)
        myList.append(myDict.copy())
    return myList

def potraceScalePoints(mList, mScale=0.1):
    return scaleTransferPoints(mList, mScale)

def pt2mmPoints(mList, mScale=0.343):
    return scaleTransferPoints(mList, mScale)

def image2BoardScale(mList, mScale):
    return scaleTransferPoints(mList, mScale)

def image2BoardTransfer(mList, mTransferX=-95, mTransferY=255):
    return scaleTransferPoints(mList, 1, mTransferX, mTransferY)

def pointCodeMaker(mX, mY):
    global point_counter
    point_counter += 1
    default_point = ",237.60,179.280,-0.120,-180.000,0.000,0.000)(7,0)\n"
    return "p{0}=({1:.3f},{2:.3f}{3}".format(point_counter, mX, mY, default_point)

def instructionCodeMaker(params):
    myString = ""
    for p in params:
        try:
            if p == "up":
                myString += "p{0}.z=p{0}.z+10\n".format(point_counter)
            elif p == "down":
                myString += "p{0}.z=p{0}.z-10\n".format(point_counter)
            elif p == "delay":
                myString += ("dly " + str(delayTime) + "\n")
            elif p == "mvs":
                myString += "mvs p{0}\n".format(point_counter)
            elif p == "mov":
                myString += "mov p{0}\n".format(point_counter)
            else:
                raise Exception("Bad parameter \'{0}\'".format(p))
        except:
            exit()
    return myString

def getDistance(x1, x2, y1, y2):
    return math.sqrt(((x1 - x2)*(x1 - x2)) + ((y1 - y2)*(y1 - y2)))

#@todo: Q:Dose it need to make normalize in tracePath(mList)?
#       A:No. Because of minDistance comparison. 

def tracePath(mList):
    last_x = 0
    last_y = 0
    robot_points = ""
    robot_code = ""
    uniqueFlag = True
    for moves in myList:
        if "M" in moves.keys():
            uniqueFlag = True
            last_x = moves["M"][0]
            last_y = moves["M"][1]
            tmp_x = last_x
            tmp_y = last_y
            for points in moves["l"]:
                last_x = points[0]+last_x
                last_y = points[1]+last_y
                if getDistance(tmp_x, last_x, tmp_y, last_y) > minDistance:
                    if uniqueFlag:
                        robot_points += pointCodeMaker(tmp_y, tmp_x)
                        robot_code += instructionCodeMaker(["up", "mov", "delay", "down", "mov"])
                        uniqueFlag = False
                    tmp_x = last_x
                    tmp_y = last_y
                    robot_points += pointCodeMaker(tmp_y, tmp_x)
                    robot_code += instructionCodeMaker(["mvs"])
            if not uniqueFlag:
                robot_code += instructionCodeMaker(["up", "delay", "mov", "delay"])
        elif "m" in moves.keys():
            last_x = moves["m"][0]+last_x
            last_y = moves["m"][1]+last_y
            tmp_x = last_x
            tmp_y = last_y
            for points in moves["l"]:
                last_x = points[0]+last_x
                last_y = points[1]+last_y
                if getDistance(tmp_x, last_x, tmp_y, last_y) > minDistance:
                    if uniqueFlag:
                        robot_points += pointCodeMaker(tmp_y, tmp_x)
                        robot_code += instructionCodeMaker(["up", "mov", "delay", "down", "mov"])
                    tmp_x = last_x
                    tmp_y = last_y
                    robot_points += pointCodeMaker(tmp_y, tmp_x)
                    robot_code += instructionCodeMaker(["mvs"])
            if not uniqueFlag:
                robot_code += instructionCodeMaker(["up", "delay", "mov", "delay"])
    return (robot_points, robot_code)

def setStats(mDistance, dTime=None, pCounter=None):
    global delayTime
    global minDistance
    global point_counter
    if dTime is not None:
        delayTime = dTime
    if mDistance is not None:
        minDistance = normalize(mDistance, 1)
    if pCounter is not None:
        point_counter = pCounter
    return

if __name__ == '__main__':    
    usage = "Usage: python3 convert.py [options] ..."
    optParser = OptionParser(usage=usage)
    optParser.add_option("-i","--input",action='store',type='string',dest='input_file',
                         help='Get path of an input file. \"SVG\"')
    optParser.add_option("-o","--output",action='store',type='string',dest='output_file',
                         help='Get path of an output file. \"MB4\"')
    optParser.add_option("-d","--delay",action='store',type='float',dest='delay_time',
                         help='Get delay time for up and down.\n\
                         Default value is \"0.3\".')
    optParser.add_option("-m","--min-distance",action='store',type='float',dest='min_distance',
                         help='Get minimum distance.\n\n\
                         Default value is \"0.5\".')
    optParser.add_option("-v","--verbose",action='store_true',dest='verbose',default=False,
                         help='Print some useful information.\n\
                         By default it\'s false.')
    optParser.add_option("-q","--quiet",action='store_false',dest='verbose',default=False,
                         help='Don\'t print any information.\n\
                         By default it\'s true.')
    (options, args) = optParser.parse_args()
    if len(args) != 0 or options.input_file is None or options.output_file is None:
        raise OptionError("Please use -h or --help")

    system("echo " + options.input_file + " " + options.output_file[:-4] + "2.bmp | " + os.path.join(dirname(__file__), "convertcv.exe"))
    system("potrace -a -100 --svg " + options.output_file[:-4] + "2.bmp")
    
    setStats(options.min_distance, options.delay_time)
    fileContent = readFile(options.output_file[:-4] + "2.svg")
    (width, height) = readImageSize(fileContent)
    myScale = getImage2BoardScale((pt2mm(width), pt2mm(height)))
    fileContent = findMergeAllPath(fileContent)
    myList = getRawPoints(fileContent)
    myList = potraceScalePoints(myList)
    myList = pt2mmPoints(myList)
    myList = image2BoardScale(myList, myScale)
    myList = image2BoardTransfer(myList)
    setStats(minDistance - 0.1)
    while True:
        setStats(minDistance + 0.1,pCounter=0)
        fileContent = ""
        (codePoint, codeInstruction) = tracePath(myList)
        if options.verbose:
            print("Minimum distance: \'",minDistance,"\' Point count: \'",\
                  codePoint.count("\n"),"\'")
        if codePoint.count("\n") + 1 > 500:
            continue
        fileContent += "p0=(327.945,7.245,266.700,179.280,-0.120,-180.000,0.000,0.000)(7,0)\n"
        fileContent += "servo on\nhclose 1\noadl on\n"
        fileContent += "mov p0\ndly 2\n"
        fileContent += codeInstruction
        fileContent += "mov p0\ndly 1\n"
        fileContent += "oadl off\nservo off\nend"
        if options.verbose:
            print("Minimum distance: \'",minDistance,\
                  "\' Instruction count: \'",fileContent.count("\n") + 1, "\'")
        if fileContent.count("\n") + 1 > 5000:
            continue
        break
    writeFile(codePoint + fileContent, options.output_file)


import tempfile
import shutil
import os
import subprocess

def convert_main(input_bmp: str, output_mb4: str, convert_exe: str):
    # مسیر کوتاه موقت
    with tempfile.TemporaryDirectory() as tmpdir:
        bmp_tmp = os.path.join(tmpdir, "input.bmp")
        bmp2_tmp = os.path.join(tmpdir, "output2.bmp")
        shutil.copy(input_bmp, bmp_tmp)

        # اجرای convertcv.exe روی مسیر کوتاه
        try:
            subprocess.run([convert_exe, bmp_tmp, bmp2_tmp], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"خطا در اجرای convertcv.exe: {e}")

        # اجرای potrace
        svg_tmp = os.path.join(tmpdir, "output2.svg")
        try:
            subprocess.run(["potrace", "-a", "-100", "--svg", bmp2_tmp], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"خطا در اجرای potrace: {e}")

        # خواندن SVG و ادامه الگوریتم قدیمی
        with open(svg_tmp, "r", encoding="utf-8") as f:
            file_content = f.read()

        # اینجا کد tracePath و تولید MB4 با الگوریتم قدیمی
        # جایگزین با همان منطق اصلی
        with open(output_mb4, "w", encoding="utf-8") as f:
            f.write(file_content)  # نمونه، جایگزین با خروجی MB4 واقعی

