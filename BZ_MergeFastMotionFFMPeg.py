import math
import os
from gimpfu import *
from os import listdir
from os.path import isfile, join
import Image
import numpy as np
import subprocess as sp

hfolder="folder not ending with /"
hfilename="file name"
Dir4Debug="/media/bob/320d8f11-b669-4709-a17d-a1d9b1dcaa7f/Work/DebugBZGimpfu.txt"
  
def Format_Int_4D(num):
    HcountString = str(num)
    lenHstr=len(HcountString)
    if lenHstr==0:
        return "0000"
    elif lenHstr==1:
        return "000" + HcountString 
    elif lenHstr==2:
        return "00" + HcountString 
    elif lenHstr==3:
        return "0" + HcountString 
    else:
        return HcountString

def BZ_FFMpeg_FastMotion(input_str,input_str2,holdBZeffect,FramesSkipped,SpedUp): 

# FramesSkipped not really needed for most.  It is frames that are skipped between reads.  
# It can read them so fast even on my A10 AMD APU that it would average 30 frames per second.  
# It is reading the video file and merging or averaging the pixels for say 100 frames for example.  
# The more you average the better? the effect, in general?  
# HoldBZeffect is striking color distortion caused by 
# squaring (part of averaging all frames)  being done while in
# in the uint8 data type.  It needs to be copied to a float numpy array before squaring it or the 
# color is distorted. 
                                                        #    This version much faster.  Files add to the
    HoldFileNameBZ= input_str +"/"+ input_str2          #    tmp directory, one is added to same folder  

 #   f=open(Dir4Debug ,'a')
 #   f.write("XX" + HoldFileNameBZ + "XX")
 #   f.close()

    FFMPEG_BIN = "ffmpeg"
    command = [ FFMPEG_BIN,
            '-i', HoldFileNameBZ,
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-']


    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)
    TotalbeingAveraged=int(0)
    NameNewDir = "/tmp"
    mypath=input_str
    newDir=mypath + NameNewDir
    chk1=int(0)

    if not os.path.exists(newDir):
        os.makedirs(newDir)

    num2Skip=int(0)
    CounterX=int(0)
    Holdcount = int(0) 
    hsrows=2160
    if hsrows==1440:
        num_rows=hsrows
        num_cols=2560

    elif hsrows==2160:
        num_rows=hsrows
        num_cols=3840

    elif hsrows==1080:
        num_rows=hsrows
        num_cols=1920


    toContinue = 1
    while True:
        raw_image = pipe.stdout.read(num_cols*num_rows*3)
        imagehold =  np.fromstring(raw_image, dtype='uint8')
#        if imagehold.shape(0)<=10: break #warning doesn't work  
        try:  #this errors at end when raw_image is shorter than a full frame
            imagehold = imagehold.reshape((num_rows ,num_cols,3))
        except ValueError:
            break

        pipe.stdout.flush()
        if raw_image =="":
            break
        else:
            CounterX=CounterX+1 #counterx= counts video frames, sets speed up factor 
            if CounterX>20000: break
            if CounterX==1:
                bzholdfloat=np.zeros((num_rows,num_cols),dtype=(np.float,3))
            
            num2Skip=num2Skip+1          
            if num2Skip==FramesSkipped:  #frameskipped is selected on slider control num2skip counts
                num2Skip=0
                TotalbeingAveraged=TotalbeingAveraged+1
                bzhfloat=np.zeros((num_rows,num_cols),dtype=(np.float,3))
                if holdBZeffect:
                    bzhfloat=imagehold**2
                else:
                    bzhfloat= imagehold
                    np.square(bzhfloat)
  
                bzholdfloat += bzhfloat

            if CounterX>SpedUp: #sets video frames per frames made in tmp folder or speed up factor     
                CounterX=0
                bzholdfloat /= TotalbeingAveraged  #same as bzh=bzh/Total
                np.sqrt(bzholdfloat)
                im2 = Image.fromarray(bzholdfloat.astype('uint8'))
                Holdcount = Holdcount  + 1
                HoldcountString = Format_Int_4D(Holdcount)
                newFile=input_str + NameNewDir + "/" + "Merge" + HoldcountString + ".PNG"
                im2.save(newFile)
                TotalbeingAveraged=int(0)
#

register(
    "python-fu-BZ_FFMpeg_FastMotion",
    "Skip Merge speed up frames In Video, PNG files in /tmp",
    "Skip obsolete because it is faster now.  There may be cases so I left it in. Files added to tmp directory",
    "Bob Zenor", "Bob Zenor", "2017",
    "BZ_FFMpeg_FastMotion",
    "",
    [
           (PF_STRING, "input_str", "Folder s", hfolder),
           (PF_STRING, "input_str2", "File Name:", hfilename),
           (PF_TOGGLE, "holdBZeffect","Psychodelic mode:",0), 
           (PF_SLIDER, "FramesSkipped", "Frames Skipped:", 1, (1, 100, 10)),
           (PF_SLIDER, "SpedUp", "SpedUp Factor", 100, (2, 1000, 1)) 
    ],
    [],
    BZ_FFMpeg_FastMotion, menu="<Image>/Script-Fu")

main()
