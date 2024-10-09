Authors: Daniel Lu, Youssuf Hichri

Purpose: To automatically book library rooms for ourselves to study in.

Files:
  1. main.py
  2. booker.py
  3. bookings.json
  4. requirements.txt

You will need to create a credentials.json file on your own, and it should look like the following:

[
  {
     "username": "CUNET\\your_username",
     "password": "your_password"
  }
]


You need Python installed, as well as pip
  1. sudo apt install python3
  2. sudo apt install python3-pip


To run this code, you need to install all the packages in the requirements.txt
  1. run the command: pip install -r requirements.txt



You will also need to have a chrome driver installed.


This script is scheduled to run every Tuesday and Thursday at midnight.
I was able to apply this by editing the **crontab** file
  1. crontab -e
  2. put the following command in the crontab file, make sure to edit the second path to match the location of the script on your device: 0 0 * * 2,4 /usr/bin/python3 /home/orangepi/Desktop/script/libooker/main.py
  3. test if you did it right: crontab -l
  4. give it the right permissions: chmod +x /home/orangepi/Desktop/script/libooker/main.py
  5. make it output to a log file: 0 0 * * 2,4 /usr/bin/python3 /home/orangepi/Desktop/script/libooker/main.py >> /home/orangepi/logs/booker.log 2>&1


////////////////////////////////////////////////WORK IN PROGRESS////////////////////////////////////////////////
Making the script run periodically requires the orange Pi to be powered on permanently or periodically.
  1. 
