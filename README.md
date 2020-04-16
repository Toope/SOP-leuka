# SOP-leuka
SOP-kurssin puhesynteesi- ja leukaryhmän repository.


# Käyttöohjeet

1. Tee oma catkin workspace
  ```
mkdir -p ~/oma_ws/src
cd oma_ws
catkin_make
source devel/setup.bash
  ```
![Vaihe 1](https://github.com/Toope/SOP-leuka/tree/master/img/vaihe1.png)

2. Kopioi kansio 'leuka' oman workspacen src kansioon (jätä src-kansion sisäinen CMakeLists.txt rauhaan) ja tee catkin_make
```
cd oma_ws
catkin_make
```
  - jos tulee ongelmia puuttuvien pakettien kanssa, asenna ne näin: sudo apt-get ros-melodic-puuttuva-paketti, esim. sudo apt-get ros-melodic-rosserial-arduino
  - jos tulee ongelmia puuttuvien python-kirjastojen kanssa, asenna ne näin: pip install kirjaston_nimi, esim. pip install pygame

3. Yhdistä arduino koneeseen (ja odota hetki että kone tunnistaa arduinon) ja aja seuraava komento, jolloin koodi uploadaa arduinolle
```
catkin_make leuka_firmware_lservo-upload
```

4. Avaa väh. kolme eri komentoriviä auki käyttöä varten
	(1) roscore
	(2) rosrun rosserial_python serial_node.py _port:=/dev/ttyACM0 _baud:=1000000
	(3) rosrun leuka tts.py   (puhesynteesin käynnistys)
	TAI rostopic pub servo std_msgs/UInt16 <tähän luku 1 tai 0> (jos haluat testata servon liikettä)
	TAI rosrun leuka talker   (jos haluat servon liikkuvan eestaas nopeasti -testi)

	Jos halutaan käyttää kokonaisuudessaan puhesynteesiä + leukaa, avataan lisäksi seuraavat komentorivit
	(4) rostopic pub text std_msgs/String "testilause."   (text-kanavalle annetaan syötteeksi haluttu lause)
	(5) rostopic pub servo_ready std_msgs/Bool True       (tämän lipun asettaminen aloittaa puheen)

	Halutessa voidaan myös muuttaa asetuksia, avaa jokaista varten oma komentorivi kun puhesynteesi on käynnistetty
	- rostopic pub gender std_msgs/String <tähän "woman" tai "man">
	- rostopic pub language std_msgs/String <kieli>  (tukee toistaiseksi vain suomen kieltä)
	- rostopic pub prosody std_msgs/String <asetus>  (ei toteutettu vielä)

Jos tulee erroria, että pakettia leuka ei löydetä, tee catkin_make ja source uudestaan. 




