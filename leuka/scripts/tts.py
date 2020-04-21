#!/usr/bin/env python
# -*- coding: utf-8 -*-
# apt install mpg123

import wave, sys, aanteet , aanteet2, aanteet3, time, os, rospy, pygame, time, formantit, formantit2, math #, pyaudio, phonetics
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
from std_msgs.msg import * # String, Bool
import soundfile as sf
from pygame.sndarray import make_sound
import numpy as np
from scipy import signal as sg
from scipy.io.wavfile import write


tts_settings = {
"Language" : "FI",
"Gender" : "man",
"Prosody" : None,
"Type": "concat"
}

sanottava_sana = ""

super_type = 0

aalto2 = np.array([])
ajat = []
kaynnissa = False #Turned on when tts process is requested, ends when the robot talks

def callback(data):#, args): #muodosta_aalto(teksti = " ", gender = "man", kieli = "FI" ,prosodic_information = None):   	
#tuntuu leikkaavan sanan lopusta patkan pois jos ei paata lausetta mihinkaan valimerkkiin
    global kaynnissa, sanottava_sana, super_type, aalto2, ajat
    rospy.loginfo("Tuotetaan tiedosto")
    #rospy.loginfo(data.data)
    if not kaynnissa:
        teksti = data.data #args[0], kun yritti monella stringillä
        teksti += '.'
        sanottava_sana = ""
        kaynnissa = True

        if tts_settings["Type"] == "formant":
            super_type = 0
            sampling_rate = 2**13
            #print(sampling_rate)
            aalto = np.array([])
            fs = sampling_rate
            leikkaus = 0
            lista = list(teksti.lower()+".")
            aanteet_used = formantit2
            flag = False
            ao_flag = False
        
            for markki in lista:
                if ord(markki) == 195:
                    ao_flag = True
                    merkki = ''
                elif (ao_flag):
                    if ord(markki) == 164:
                        merkki = 'ä'
                    elif ord(markki) == 165:
                        merkki = 'å'
                    elif ord(markki) == 182:
                        merkki = 'ö'
                    ao_flag = False
                else:
                    merkki = markki
                    ao_flag = False
            #print(merkki)
                if merkki in aanteet_used.formantit["vokaali"] or merkki in aanteet_used.formantit["konsonantti"]:
                    if flag:
                        if merkki == "g" and edellinen_merkki == "n":
                            aalto = np.append(aalto, for_matti("ng", "konsonantti", fs)) 
                            flag = False
                            edellinen_merkki = "666"
                            sanottava_sana += "ng"
                            ajat.append([formantit2.formantit["konsonantti"]["ng"][4], 0])
                        elif merkki in aanteet_used.formantit["vokaali"] and edellinen_merkki in aanteet_used.formantit["vokaali"]:
                            if (edellinen_merkki + merkki) in aanteet_used.formantit["diftongi"]:
                                aalto = np.append(aalto, for_matti(edellinen_merkki, "vokaali", fs))
                                aalto = np.append(aalto, for_matti(merkki, "vokaali", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["vokaali"][edellinen_merkki][4],1])
                                sanottava_sana += merkki
                                ajat.append([formantit2.formantit["vokaali"][merkki][4],1])
                            elif (edellinen_merkki + merkki) in aanteet_used.formantit["aakkoset"]:
                                aalto = np.append(aalto, for_matti(edellinen_merkki, "vokaali", fs))
                                aalto = np.append(aalto, for_matti(merkki, "vokaali", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["vokaali"][edellinen_merkki][4],1])
                                sanottava_sana += merkki
                                ajat.append([formantit2.formantit["vokaali"][merkki][4],1])
                            else:
                                aalto = np.append(aalto, for_matti(edellinen_merkki, "vokaali", fs))
                                aalto = np.append(aalto, for_matti(merkki, "vokaali", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["vokaali"][edellinen_merkki][4],1])
                                sanottava_sana += merkki
                                ajat.append([formantit2.formantit["vokaali"][merkki][4],1])
                            flag = False
                            edellinen_merkki = "666"
                        
                        elif merkki in aanteet_used.formantit["konsonantti"] and edellinen_merkki in aanteet_used.formantit["konsonantti"]:
                            if (edellinen_merkki + merkki) in aanteet_used.formantit["aakkoset"]:
                                aalto = np.append(aalto, for_matti(edellinen_merkki+merkki, "aakkoset", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["vokaali"][edellinen_merkki][4],1])
                                sanottava_sana += merkki
                                ajat.append([formantit2.formantit["vokaali"][merkki][4],1])
                            else:
                                aalto = np.append(aalto, for_matti(edellinen_merkki, "konsonantti", fs))
                                aalto = np.append(aalto, for_matti(merkki, "konsonantti", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["konsonantti"][edellinen_merkki][4],0])
                                sanottava_sana += merkki
                                ajat.append([formantit2.formantit["konsonantti"][edellinen_merkki][4],0])
                            flag = False
                            edellinen_merkki = "666"
                        
                        else:
                            if edellinen_merkki in aanteet_used.formantit["vokaali"]:
                                aalto = np.append(aalto, for_matti(edellinen_merkki, "vokaali", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["vokaali"][edellinen_merkki][4],1])
                            else:
                                aalto = np.append(aalto, for_matti(edellinen_merkki, "konsonantti", fs))
                                sanottava_sana += edellinen_merkki
                                ajat.append([formantit2.formantit["konsonantti"][edellinen_merkki][4],0])
                            flag = True
                            edellinen_merkki = merkki
                    else:
                        flag = True
                        edellinen_merkki = merkki
            aalto2 = aalto * 0.1
            rospy.loginfo(sanottava_sana)
            pub0.publish(True)
        else:
            super_type = 1
            gender = tts_settings["Gender"]
            kieli = tts_settings["Language"]
            prosodiaInfo = tts_settings["Prosody"]    

            aanteet_used = None

            if(kieli == "EN"):
               pass
            else:#elif(kieli == "FI"):
                if(gender == "man"):                #anna lauseen jalkeen argumentti kumman aanella haluat kuulla puheen
                    aanteet_used = aanteet3
                elif(gender == "woman"):
                    aanteet_used = aanteet2
            
            if(aanteet_used == None): #parametreja ei loytynyt, tehdaan defaultilla
                aanteet_used = aanteet3 
            
            #rospy.loginfo(gender)
         
            lista = list(teksti.lower())
            combined_sounds = AudioSegment.empty()
            flag = False
            edellinen_merkki = "666"
            ao_flag = False
            for markki in lista:
                if ord(markki) == 195:
                    ao_flag = True
                    merkki = ''
                elif (ao_flag):
                    if ord(markki) == 164:
                        merkki = 'ä'
                    elif ord(markki) == 165:
                        merkki = 'å'
                    elif ord(markki) == 182:
                            merkki = 'ö'
                    ao_flag = False
                else:
                    merkki = markki
                    ao_flag = False
                        

                if merkki in aanteet_used.aalto_aanne["vokaali"] or merkki in aanteet_used.aalto_aanne["konsonantti"]:
                    if flag:
                        if merkki == "g" and edellinen_merkki == "n":
                            combined_sounds += aanteet_used.aalto_aanne["konsonantti"].get("ng")
                            sanottava_sana += 'ng' 
                            flag = False
                            edellinen_merkki = "666"
                        elif merkki in aanteet_used.aalto_aanne["vokaali"] and edellinen_merkki in aanteet_used.aalto_aanne["vokaali"]:
                            if (edellinen_merkki + merkki) in aanteet_used.aalto_aanne["diftongi"]:
                                combined_sounds += aanteet_used.aalto_aanne["diftongi"].get(edellinen_merkki + merkki)
                                sanottava_sana += edellinen_merkki
                                sanottava_sana += merkki
                            elif (edellinen_merkki + merkki) in aanteet_used.aalto_aanne["aakkoset"]:
                                combined_sounds += aanteet_used.aalto_aanne["aakkoset"].get(edellinen_merkki + merkki)
                                sanottava_sana += edellinen_merkki
                                sanottava_sana += merkki
                            else:
                                combined_sounds += aanteet_used.aalto_aanne["vokaali"].get(edellinen_merkki)
                                combined_sounds += aanteet_used.aalto_aanne["vokaali"].get(merkki)
                                sanottava_sana += edellinen_merkki
                                sanottava_sana += merkki
                            flag = False
                            edellinen_merkki = "666"
                    
                        elif merkki in aanteet_used.aalto_aanne["konsonantti"] and edellinen_merkki in aanteet_used.aalto_aanne["konsonantti"]:
                            if (edellinen_merkki + merkki) in aanteet_used.aalto_aanne["aakkoset"]:
                                combined_sounds += aanteet_used.aalto_aanne["aakkoset"].get(edellinen_merkki + merkki)
                                sanottava_sana += edellinen_merkki
                                sanottava_sana += merkki
                            else:
                                combined_sounds += aanteet_used.aalto_aanne["konsonantti"].get(edellinen_merkki)
                                combined_sounds += aanteet_used.aalto_aanne["konsonantti"].get(merkki)
                                sanottava_sana += edellinen_merkki
                                sanottava_sana += merkki
                            flag = False
                            edellinen_merkki = "666"
                            
                        else:
                            if edellinen_merkki in aanteet_used.aalto_aanne["vokaali"]:
                                combined_sounds += aanteet_used.aalto_aanne["vokaali"].get(edellinen_merkki)
                                sanottava_sana += edellinen_merkki
                            else:
                                combined_sounds += aanteet_used.aalto_aanne["konsonantti"].get(edellinen_merkki)
                                sanottava_sana += edellinen_merkki
                            flag = True
                            edellinen_merkki = merkki
                    else:
                        flag = True
                        edellinen_merkki = merkki

                        
            kaks_prossaa_hitaampi = combined_sounds._spawn(combined_sounds.raw_data, overrides={
            "frame_rate": int(combined_sounds.frame_rate * 1)
            })
            if os.path.exists("sano.wav"):
                os.remove("sano.wav")

            kaks_prossaa_hitaampi.export("sano.wav", format="wav")
            tahti = rospy.Rate(1)
            tahti.sleep()
            rospy.loginfo(sanottava_sana)
            pub0.publish(True)


def puhu(data):
    global kaynnissa, super_type
    rospy.loginfo("Puhutaan")
    if data.data and kaynnissa:
        if(len(sanottava_sana) > 0):
            if super_type == 1:
                f = sf.SoundFile('sano.wav')
                sekuntia = float(len(f)) / float(f.samplerate)
                pittuus = len(sanottava_sana)
                for kiriain in sanottava_sana:
                    if ord(kiriain) == 195:
                        pittuus -= 1
                tahti = rospy.Rate(float(pittuus) / float(sekuntia))
                #playsound("sano.wav")
                pygame.mixer.init()
                pygame.mixer.music.load("sano.wav")
                pygame.mixer.music.play(1)
                ao_flag = False
                for kirjain in sanottava_sana:
                    if ord(kirjain) == 195:
                        ao_flag = True
                        continue 
                    if kirjain in aanteet.aalto_aanne["vokaali"] or (ao_flag and (ord(kirjain) ==  164 or ord(kirjain) == 182)):
                        rospy.loginfo(1)
                        pub1.publish(1)
                    else:
                        rospy.loginfo(0)
                        pub1.publish(0)
                    ao_flag = False
                    tahti.sleep()
                kaynnissa = False
            else:
                pygame.mixer.init(2**13, -16, 1) #fs kHz, 16-bit signed, mono
                sound = pygame.sndarray.make_sound(np.int16(aalto2 * 32767))
                channel = sound.play(0)
                for t in ajat:
                    pub1.publish(t[1])
                    tahti = rospy.Rate(1/t[0])
                    tahti.sleep()
                kaynnissa = False
                    
    

def onko_kaynnissa():
    global kaynnissa
    return kaynnissa


def scrap_the_talk(data):
    global kaynnissa
    if data.data:
	kaynnissa = False

def update_Language(data):
    tts_settings["Language"] = data.data

def update_Gender(data):
    tts_settings["Gender"] = data.data

def update_Prosody(data):
    tts_settings["Prosody"] = data.data
    
def update_tts_type(data):
    tts_settings["Type"] = data.data

def tts_control(): 
    rospy.init_node('tts_control', anonymous=True)
    rospy.spin()

    
def for_matti(kirjain, tyyppi, forfuckssake):
    F = np.array(formantit2.formantit[tyyppi][kirjain][0:4])  #4 ensimmäistä formanttia
    Ba = np.array([20, 30, 50, 60])                           #Bandwith formanteille
    
    dur = formantit2.formantit[tyyppi][kirjain][4]   #kesto
    fs = forfuckssake                                #näytteenottotaajuus
    nsamps = int(math.floor(dur*fs))                      #Näytteiden määrä
    R = np.exp(-np.pi*Ba/fs)                          #naparadius
    theta = (2*np.pi*F)/fs                           #napakulma
    poles = R * np.exp(1j*theta)                     #Navat
    [B,A] = sg.zpk2tf(0,poles,1)                     #Kontrolli
    h = sg.freqz(B,A,1024)
    h = h/np.max(h)
    hdb = 20*np.log10(np.abs(h)+10**-100)
    
    f0 = 105                                          #pitch
    w0T = 2*np.pi*f0/fs                              #normalisoitu
    
    nharm = int(math.floor((fs/2)/f0))
    sig = np.zeros(nsamps)
    n = np.arange(nsamps)
    
    if F[0] != 0 and F[1] != 0 and F[2] != 0 and F[3] != 0:
        for i in range(nharm):
            #sig += np.sin(i*w0T*n)
            sig += sg.sawtooth(i*w0T*n)
        
        
    sig = sig/np.max(sig)

    nfft = 1024
    fni = np.arange(0,fs-fs/nfft,fs/nfft)
    #print(len(fni))
    M = 256
    w = np.hanning(M)
    
    speech = sg.lfilter(np.array([1.0]),A,sig)        
    return speech
    
#topic Broadcast
sub0 = rospy.Subscriber("text", String, callback)
sub1 = rospy.Subscriber("language", String, update_Language)
sub2 = rospy.Subscriber("gender", String, update_Gender)
sub3 = rospy.Subscriber("prosody", String, update_Prosody)
sub4 = rospy.Subscriber("servo_ready", Bool, puhu)
sub2 = rospy.Subscriber("tts_type", String, update_tts_type)
pub0 = rospy.Publisher("tts_ready", Bool, queue_size = 1)
pub1 = rospy.Publisher("servo", UInt16, queue_size = 10)

if __name__ == "__main__":
    tts_control()
    
    
            
