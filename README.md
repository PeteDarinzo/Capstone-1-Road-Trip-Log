# Capstone-1 Greenflash

## Developer: Peter Darinzo

### View the app: https://green-flash.herokuapp.com/

[Navigation](#navigation)  
[Installation](#installation)  
[Testing](#testing)

## About 

**Goal**

Greenflash is a road trip assistant for RVers, vanlifers, or anyone on an extended road trip. Users can use it to search for local services, as well as document the journey through log and maintenance entries which record location, mileage, and a text entry with an optional image. A log entry is used much like a personal journal, maintenance records keep track of where and when maintenance was performed on the vehicle.

A [green flash](https://en.wikipedia.org/wiki/Green_flash) is an atmospheric phenomenon in which a setting or rising sun gives off green light. The name of the app is intended to invoke the feeling of adventure felt on road trips. While I have never seen a green flash myself, I am always hopeful.


**Data** 

  The [Yelp API](https://www.yelp.com/developers/documentation/v3) is used to show the user services (campsites, restaurants, libraries) locally, or at a future destination. The Yelp API accepts a type of service to search for, human readable locations or lat/lon pairs for a location, and returns a list of matching businesses.

## Navigation

From the landing screen, anyone can use the search function by simply entering the service and a location, and viewing the results. When logged in, a user may also save places of interest, and then view them by clicking the "Places" button on the navbar.

Sign up to gain access to the log creation features of the app. Once logged in, users may still use the search function, or click on the "Posts" nav button to go to the logs page. 

The default page after clicking "Posts" is the form to submit a new log entry. The left hand column displays the most recent logs, and buttons to show all logs, and create new ones. When viewing a log, there are buttons to edit and delete the log. 

The right hand column is identical, but used to record maintenance of the vehicle. 

When logged in, clicking the username will show the user profile. There are buttons to edit and delete the profile, or change the user's password. When editing, user's may add an optional biography and change their profile image.

## Installation

### Before beginning:
Python3 and pip3 must be installed before running this app. The app also requires a Postgresql database.

## Instructions

#### 1. Get a free Yelp API key.
```
https://www.yelp.com/developers/documentation/v3/get_started
```

#### 2. (OPTIONAL FOR IMAGE SUPPORT) Create an Amazon Web Services (AWS) account, then follow the steps in this tutorial under "Navigate the Amazon S3 Dashboard" to configure S3 to store images. 

#### 3. Clone the Repo.
```
$ git clone https://github.com/PeteDarinzo/Green-Flash
```

#### 4. Create a virtual environment in the project directory.
```
$ python3 -m venv venv
```

#### 5. Start the virtual environment in the project directory.
```
$ source venv/bin/activate
```

#### 6. Install required packages.
```
$ pip3 install -r requirements.txt
```

#### 7. Create a file called .env in the root directory. =
 *Make sure to add .env to the .gitignore file in the directory so that your API and AWS credentials do not get accidentally shared.*

#### 8. Create the following variable in .env, and set it equal to your Yelp API key, with no quotations:
- API_KEY = YOUR_API_KEY_WITH_NO_QUOTATIONS

#### 9. (OPTIONAL IF USING AWS FOR IMAGES) Create the following variables in .env, and set them equal to the proper values generated in step 2:
- S3_BUCKET
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

#### 10. Start Postgresql, entering your password when prompted.
```
$ sudo service postgresql start
```

#### 12. Enter Postgresql.
```
$ psql
```

#### 13. Create a database for the app.
```
# CREATE DATABASE greenflash;
```

#### 14. Populate database tables through ipython (method 1), or the provided seed file (method 2).

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

#### 15. Run flask
```
flask run
```

#### 16. Open a web browser and run the app on the server's port.

## Testing

### Run all of the unit and integration tests with the following command:
```
$ python -m unittest
```

### To run one particular test file, modify the command as follows:
```
$ python -m unittest [test_filename].py
```
  