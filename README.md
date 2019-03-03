Personal Macshop Tracker
====
Macshop Tracker is a script that notice you following the newest post in ptt-macshop every hour.

## dependencies
    python==3.6
    apscheduler==3.5.3
    line-bot-sdk==1.8.0
    beautifulsoup4==4.7.1
    
## Installation
 [Docker](https://www.docker.com)
 
## Getting Started
    git clone https://github.com/yylin48/macshop-tracker.git
    cd macshop-tracker
    cp env.py.sample env.py 
    
Filled in your channel token, secret, your line user id in env.py

	channel_token = 'CHANNEL_TOKEN'
	secret = 'SECRET'
	your_id = 'YOUR_USER_ID'
	
the file you need
	
	app.py
	env.py
	Dockerfile
	docker-compose.yml
	requirements.txt
	
## Usage

build and run in background

    docker-compose build
    docker-compose up -d


![image](https://github.com/yylin48/macshop-tracker/blob/master/png/macshop-tracker-example.png)      

### other method

you can also use Procfile & Pipfile to deploy on Heroku

	
