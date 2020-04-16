#!/usr/bin/env python
# -*- coding: utf-8 -*-
# apt install mpg123
import wave, sys, aanteet , aanteet2, aanteet3, time, os, rospy, pygame #, pyaudio, phonetics
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
from std_msgs.msg import * # String, Bool
import soundfile as sf

tts_settings = {
"Language" : "FI",
"Gender" : "man",
"Prosody" : None
}

sanottava_sana = ""

kaynnissa = False #Turned on when tts process is requested, ends when the robot talks

def callback(data):#, args): #muodosta_aalto(teksti = " ", gender = "man", kieli = "FI" ,prosodic_information = None):   	
#tuntuu leikkaavan sanan lopusta patkan pois jos ei paata lausetta mihinkaan valimerkkiin
    global kaynnissa, sanottava_sana
    rospy.loginfo("Tuotetaan tiedosto")
    #rospy.loginfo(data.data)
    if not kaynnissa:
	    kaynnissa = True
	    teksti = data.data #args[0], kun yritti monella stringillä
            teksti += '.'
            sanottava_sana = ""
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
                #rospy.loginfo(ord(markki))
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
                            #if merkki == "n" or merkki in aanteet_used.aalto_aanne["vokaali"]:
                            flag = True
                            edellinen_merkki = merkki
                            #else:
                                #combined_sounds += aanteet_used.aalto_aanne["konsonantti"].get(merkki)
                             #   flag = True
                              #  edellinen_merkki = merkki
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
    global kaynnissa
    rospy.loginfo("Puhutaan")
    if data.data and kaynnissa:
        if(len(sanottava_sana) > 0):
	    f = sf.SoundFile('sano.wav')
	    sekuntia = float(len(f)) / float(f.samplerate)
            pittuus = len(sanottava_sana)
            for kiriain in sanottava_sana:
                if ord(kiriain) == 195:
                    pittuus -= 1
	    #rospy.loginfo(float(sekuntia))
	    #rospy.loginfo(len(sanottava_sana))
	    #rospy.loginfo(float(sekuntia) / float(len(sanottava_sana)))
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

def tts_control(): 
    rospy.init_node('tts_control', anonymous=True)
    rospy.spin()

#topic Broadcast

sub0 = rospy.Subscriber("text", String, callback)
sub1 = rospy.Subscriber("language", String, update_Language)
sub2 = rospy.Subscriber("gender", String, update_Gender)
sub3 = rospy.Subscriber("prosody", String, update_Prosody)
sub4 = rospy.Subscriber("servo_ready", Bool, puhu)
pub0 = rospy.Publisher("tts_ready", Bool, queue_size = 1)
pub1 = rospy.Publisher("servo", UInt16, queue_size = 10)

if __name__ == "__main__":
    tts_control()
    
    
            
