# Supermarket-Project
## Overview

After finishing university, I wanted to test my skills to their absolute limit.
Before, I was working on assignments that were scaled down and (at the time) complex, learning new technologies and methods that I was taught for the last three years. 
Now that I have finished, I wanted to apply this newly obtained knowledge and further expand on it by creating a more advanced and complex project.
I chose a supermarket application as at first it sounds simple but can become very complex depending on how much you want to implement and develop.

My overall goal is to create a fully functional supermarket application, frontend and backend.
It will contain the basics of what supermarkets need whilst also including more advanced tech.
I aim to implement various machine learning and/or AI models into the project for specific circumstances.
For example:-

- Automated moderation model for reviews created on the application.

- Recommendation system of items based off of past purchases, trends and sales.

- Demand forecasting for the different supermarkets a part of the application.

- Review analysis from customers (detect common complaints/praises).



## Technologies Used

To Be Added



## Development Plans

- Account Management (within account-service)
- - Update roles and status
- - All Account Visualisation (admin-service)
- - Frontend Development


- Global Supermarket Items (New Service product-service)
- - CRUD Items
- - Tagging system
- - - Hierarchical Bucket system for placement (e.g. chilled > dairy > butter > company name)
- - - General Tagging convention (e.g. dairy-free, vegan, imported)
- - filtering/searching (must return the most accurate results first)


- Store Service (New Service store-service (per store))
- - CRUD basic data
- - Regional Management
- - Staff data


- Admin Service (New Service admin-service)
- - Connect to all services
- - Take action depending on the service and what it provides
- - Visualise and save data
- - View each store data
- - Cache Data


- Store Inventory (New Service inventory-service (per store))
- - Items available
- - Audit Changes
- - Staff functions
- - - Stock estimating
- - - Offsaling / ordering
- - History tracking


- Online Ordering (New Service order-service)
- - Order from store
- - Order lifecycle

More To Be Added Depending On Project State
