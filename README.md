# Telegram bot for standardization of dresses

This is a Telegram bot designed for the purpose of standardizing clothing (in this case, dresses) using the AI model YOLO.  
The bot has been developed using the aiogram library. Radishes have also been integrated into the system.  

<img alt="example" src="https://github.com/user-attachments/assets/441974b3-b675-47b3-b876-d918922938aa" width=200>
<img alt="example" src="https://github.com/user-attachments/assets/e554da34-65e9-47c6-aceb-a469ace458ff" width=200>

## How to start:
First, install the latest [release](https://github.com/KelBro/ProjectTPSH/releases)  
You'll have to setup [Redis 7](https://redis.io/downloads/), or if you'll run it on Windows, you can use [Memurai](https://www.memurai.com/get-memurai)  

### For bot
First, you'll have to edit .env file, assign your Telegram Bot token, Redis server ip and Redis password  
Install requirement modules ``pip install -r  ./requirements.txt``  
When you're ready, start the _main.py_ file ``python ./main.py``  

___

### For ai
First, you'll have to edit .env file, assign your Redis server ip and Redis password  
Install [Models](https://drive.google.com/file/d/1epwmXhikBdfNGuILd3Ps3i6cvhvxvXcc/view?usp=sharing) and extract both folders to shopping-assistant-ai  
Install requirment modules ``pip install -r  ./requirements.txt``  
When you're ready, run _connect.py_ file ``python ./main.py``  

_Notes:_  
_You should use python 3.10.6_  
_The bot and ai are meant to run on different servers, but it's not necessary_  
