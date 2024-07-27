# Mosaic
##### a simple cms application using Flask and Htmx

### Features
- user can create blog
- user can create/edit/delete an account
- user can create/edit/delete posts in blog
- user can create/delete comments

### To-Do
- implement delete comment button
- implement front page
- implement create category page
- implement admin dashboard
- complete user profile page
- user can like posts
- user can follow other users

#### unit tests
- model tests
- blueprint tests

### How to install
##### Instructions for Windows, run the following commands using cmd in root directory
- create virtual environment: `python -m venv .venv` and activate it `.venv\Scripts\activate`
- upgrade pip: `python.exe -m pip install --upgrade pip`
- upgrade setuptools: `pip install --upgrade setuptools`
- install poetry: `pip install poetry`
- install dependencies: `poetry install`
- install front end dependencies: `cd app\static` then `npm install`
- rename `.env-example` to `.env` and edit the project's configurations
- initialize the application `flask init`
- run the application `flask run`

### Testing
- install development dependencies: `poetry install --dev`
- to run unit tests: `flask test`

#### Testing emails
- local email server `aiosmtpd -n -c aiosmtpd.handlers.Debugging -l localhost:8025`

