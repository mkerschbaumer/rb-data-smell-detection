# Development of a Software Library and Web Application for Rule-based Data Smell Detection
This is the bachelor-thesis repository of Laura Geiger and Martin Kerschbaumer.
## Setup Server
It is assumed that all the following steps are executed inside the root directory of this project.
### Setup with Docker

 1. The **Dockerfile** and **docker-compose.yml** are located in the root directory.
 2. Build the docker image with `sudo docker-compose build`.
 3. Start the web application with `sudo docker-compose up -d`.
 4. The web application can be visited at `http://127.0.0.1:5005`.

### Dockerless Server Setup
#### Setup Data Smell Detection Library
```bash

    # Virtualenv modules installation and activation (Unix based systems)
    sudo apt-get install python3-pip
    sudo pip3 install virtualenv 
    virtualenv env 
    source env/bin/activate

    # Install the requirements and the data smell detection library
    cd data_smell_detection
    pip install -r requirements-dev.in
    python3 setup.py install
     
```
#### Setup Web Application
```bash

    cd ../web_application/argon-dashboard-django/ # application root folder

    # Install modules
    pip3 install -r requirements.txt

    # Create tables
    python manage.py makemigrations
    python manage.py migrate

    # Start the application
    python manage.py runserver

    # Access the web app in browser http://127.0.0.1:8000/
      
```

