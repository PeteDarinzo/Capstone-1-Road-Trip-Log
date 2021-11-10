# Capstone-1 Greenflash

## Developer: Peter Darinzo

[Navigation](#navigation)  
[Installation](#installation)  
[Testing](#testing)

## About 

**Goal**

Greenflash is a road trip assistant for RVers, vanlifers, or anyone on extended road trips. Users can use it to search for local services such as RV parks, restaurants, and libraries. Users can also create log and maintenance entries which record their location, and mileage. A log entry is used much like a personal journal, maintenance records keep track of where and when maintenance was performed on the vehicle.

A [green flash](https://en.wikipedia.org/wiki/Green_flash) is an atmospheric phenomenon in which a setting or rising sun gives off green light. The name of the app is intended to spark the feeling of adventure felt on road trips. While I have never seen a green flash myself, I am always hopeful.


**Data** 

  The [Yelp API](https://www.yelp.com/developers/documentation/v3) is used to show the user services (campsites, restaurants, libraries) locally, or at a future destination. The Yelp API accepts a type of service to search for, human readable locations or lat/lon pairs for a location, and returns a list of matching businesses.

## Navigation

From the landing screen, anyone can use the search function, simply enter the service and a location. When logged out, a user may only view the results. When logged in, a user may save places of interest for later reference, and then view them by clicking the "Places" button on the navbar.

Signup to gain access to the log creation features of the app. Once logged in, user's may still use the search function, or click on the "posts" nav button to go to the logs page. 

The default page is the form to submit a new log entry. The left hand column displays the most recently written logs, and buttons to show all logs, and create new ones. When viewing a log, there are buttons two edit and delete the log. 

The right hand column is identical, but used to record maintenance to the vehicle. When logged in, clicking the username will show the user profile.

A biography and optional profile image may be added. There are buttons to edit and delete the profile, or change the user's password.

## Installation

### Before beginning:
Python3 and pip3 must be installed before running this app. The app also requires a Postgresql database.

## Instructions

#### 1. Get a free Yelp API key.
```
https://www.yelp.com/developers/documentation/v3/get_started
```

#### 2. Clone the Repo.
```
$ git clone https://github.com/PeteDarinzo/Green-Flash
```

#### 3. Create a virtual environment in the project directory.
```
$ python3 -m venv venv
```

#### 4. Start the virtual environment in the project directory.
```
$ source venv/bin/activate
```

#### 5. Install required packages.
```
$ pip3 install -r requirements.txt
```

#### 6. Create a python file called key.py and add the API key. **Make sure to add key.py to the .gitignore file in the directory so that your API key doesn't get accidentally shared.**<br/>
#### 7. Create a variable in key.py called API_KEY, set it equal to your Yelp API key.<br/>
#### 8. Start Postgresql, entering your password when prompeted.
```
$ sudo service postgresql start
```

#### 9. Enter Postgresql.
```
$ psql
```

#### 10. Create a databse for the app.
```
# CREATE DATABASE greenflash;
```

#### 11. Populate database tables through ipython (method 1), or the provided seed file (method 2).

 - #### Method 1
   ```
   $ ipython
   In [1]: $run app.py
   In [2]: db.create_all()
   ```

- #### Method 2
   The seed file create the database tables, and populates them with data.
   ```
   $ python seed.py
   ```

#### 12. Run flask
```
flask run
```

#### 13. Open a web browser and run the app on the server's port.

## Testing

### Run all of the unit and integration tests with the following command:
```
$ python -m unittest
```

### To run one particular test file, modify the command as follows:
```
$ python -m unittest [test_filename].py
```
  