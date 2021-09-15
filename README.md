# Capstone-1-Road-Trip-Log
Springboard Capstone 1 - Road Trip Log

1. **Goal**: The goal of this app is to provide users with a way to create daily logs for road trips. User’s create text posts, and can upload images relating to the post. User’s may optionally input any expenses that day, and add notes on maintenance (oil changes, tire rotations, etc.). The app could be expanded to be a social network with other nomads, where their route is shared, along with pictures and posts. 

2. **Demographic**: This app is targeted to anyone underway on a road trip. The app will be more useful to long term RVers and “van lifers”, but is accessible to anyone on a multi day trip. 

3. **Data/API**
   - The [IP-API](https://ip-api.com/docs/api:json) can be used to obtain a user’s geographic location from their IP address.
   - The [Image Charts](https://documentation.image-charts.com/) API can be used to generate charts of user expenses, daily mileage, etc.
   - The [Observable](https://github.com/d3/d3/blob/main/API.md) API could be used to create interactive maps plotting the trip based on post locations  (stretch goal).

4. Drop the salmon into the egg-milk bowl.

   Here are some techniques on salmon-dropping:
   * Make sure no trout or children are present
   * Use both hands
   * Always have a towel nearby in case of messes

4. **Outline**
   - Database Schema
   -
      1. User:
         - Username
         - First name
         - Last name
         - Password
         
      2. Posts
         - Id
         - Content
         - Location
         - Date
         - Mileage
         
      3. Locations
         - Location
         - Post id
         
      4. Images
         - Id
         - Post id 
         - Name
         
      5. Finances
         - Id
         - Amount
         - Category
         - Date
         
      6. Maintenance 
         - Id
         - Description
         - Mileage
         - Date
         - Post Id
         
      7. TODO
         - Id
         - Description

   3. Potential API Issues

   4. Sensitive information
      - Location: A user’s location can be considered sensitive. The IP-API will be submitting the user’s IP to retrieve location data. 
      - Password

   5.Functionality
Create posts/upload images.
View budget/mileage data.
(Stretch goal) View map of route taken based on previous posts. Click on a location marker to view related posts. 
(Stretch goal) view data on future destinations.

User flow
The user starts on the dashboard displaying location, mileage, finance data, and to do list.
Create a text log to record days events, expenses, mileage, maintenance, and upload pictures.
View previous logs (also edit/delete).
(Stretch goal) search future destinations. Enter a destination city, look at routes, weather data, restaurants etc.  

CRUD features
Create users.
Create logs.

Features greater than CRUD?
View charts of budget, mileage, etc.
(Stretch goal) View map of route taken based on previous posts. Click on a location marker to view related posts. 
(Stretch goal) View POIs/gas/restaurants/weather for future destinations.

