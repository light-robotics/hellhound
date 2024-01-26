# hellhound

HellHound: a robot-dog.
YouTube channel: https://www.youtube.com/channel/UC5iMcYcLpUnzzhuc-a_uPiQ
Email: light.robotics.2020@gmail.com

To run hellhound:

run "python3 /hellhound/hellhound_hardware/hh_dualshock.py"
run "python3 /hellhound/run/movement_processor.py"
run "sudo python3 /hellhound/run/neopixel_commands_reader.py"
Video streaming:

sudo ffmpeg -s 1024x576 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -b:v 4000k -r 30 http://{nexus_ip}:8081/12345/1024/576/
Useful:

vcgencmd measure_temp
cat /var/log/syslog.1