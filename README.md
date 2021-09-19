# Capstone-1-Road-Trip-Log

## Developer: Peter Darinzo

1. **Goal**: The goal of this app is to provide users with a road trip assistant. Users will be able to search for services at the location of their choice, and create daily logs for the trip. User’s create text posts, and can upload images relating to the post. User’s may optionally input any expenses that day, and add notes on maintenance (oil changes, tire rotations, etc.). The app could be expanded to be a social network with other nomads, where their route is shared, along with pictures and posts. 

2. **Demographic**: This app is targeted to anyone underway on a road trip. The app will be more useful to long term RVers and “van lifers”, but is accessible to anyone on a multi day trip. 

3. **Data/API**
   - The [Yelp](https://www.yelp.com/developers/documentation/v3) will be used to show the user local services (campsites, restaurants, libraries), or at a future destination. The Yelp API accepts human readable locations, or lat/lon pairs for a location.

4. **Outline**
   - **Database Schema In Order of Priority**
   
      1. **User**
         - USer Id
         - Username
         - First name
         - Last name
         - Password
         
      2. **Posts**
         - Id
         - User Id
         - Content
         - Location
         - Date
         - Mileage
         
      3. **Locations**
         - Id
         - Location
         - Post id

      4. **Maintenance**
         - Id
         - User Id
         - Description
         - Mileage
         - Date
         - Post Id
         
      5. **Finances**
         - Id
         - User Id
         - Amount
         - Category
         - Date
         
      6. **Images**
         - Id
         - User Id
         - Post id 
         - Name
         
      7. **TODO**
         - Id
         - User Id
         - Description

   - **Potential API Issues**

   - **Sensitive information**
      - Location: A user’s location can be considered sensitive. The IP-API will be submitting the user’s IP to retrieve location data. 
      - Password

   - **Functionality**
      - Create posts/upload images.
      - View budget/mileage data.
      - View services for local and future destinations.
      - (Stretch goal) View map of route taken based on previous posts. Click on a location marker to view related posts. 

   - **User flow**
      - The user starts on the dashboard displaying location, mileage, finance data, and to do list.
      - The dashboard has a search area where users can input a location and type of service, and view results.
      - Create a text log to record days events, expenses, mileage, maintenance, and upload pictures.
      - View previous logs (also edit/delete).
      - (Stretch goal) View map of route taken based on previous posts. Click on a location marker to view related posts. 
      - (Stretch goal) search future destinations. Enter a destination city, look at routes, weather data, restaurants etc.  

   - **CRUD features**
      - Create users.
      - Create logs.

   - **Features greater than CRUD**
      - View POIs/gas/restaurants/camp sites for local and future destinations.
      - View charts of budget, mileage, etc.
      - (Stretch goal) View map of route taken based on previous posts. Click on a location marker to view related posts. 

