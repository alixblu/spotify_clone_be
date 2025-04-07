# Spotify-clone Backend Project

This repository contains the backend for a Spotify-like application, built with **Django** and **MongoDB**. The backend provides APIs for managing songs, playlists, and users. Development is done in **Visual Studio Code** using **WSL (Windows Subsystem for Linux)**.

---

## Features
- RESTful API for songs and playlists.
- Integration with MongoDB for data storage.
- Easy setup for development using WSL.

---

## Requirements
Before starting, make sure you have the following installed:
- **WSL** (Windows Subsystem for Linux) enabled and set up.
- **MongoDB** installed and running in WSL.
- **Python** (3.9 or later) installed.
- **Visual Studio Code** with the WSL extension.

---

## Installation and Setup

### Step 1: Clone the Repository
- git clone https://github.com/alixblu/spotify_clone_backend.git
- cd spotify_clone_backend
### Step 2: Create a Virtual Environment
- Set up a virtual environment to manage dependencies:
- python3 -m venv spotify_envi
source spotify_envi/bin/activate

### Step 3: Install Required Dependencies
- pip install -r requirements.txt

### Step 4: Set Up MongoDB
- sudo apt update
- sudo apt install mongodb
- sudo systemctl start mongodb

### Step 5: Configure the Database in Django
- Update the settings.py file to use MongoDB
- DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'spotify_clone_db',
    }
}

## Running the Project

### Start the Django Development Server
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver
```bash
