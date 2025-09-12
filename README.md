# FrigoFlow

Video demo: [https://youtu.be/bKxLzcad6FI](https://youtu.be/bKxLzcad6FI)

Try it out on [nickroger.pythonanywhere.com](https://nickroger.pythonanywhere.com/)

## Overview
FrigoFlow is a web application that is meant for users to help them keep track of the contents of their fridge. The main idea for this project was to reduce food waste and to make it easier to manage your groceries. It adds a simple interface for adding, editing, deleting, and seeing available recipes. The user can add a name, expiration date, and notes for each item.

This project was created as my final project for CS50. It uses many skills taught in the course, like HTML and CSS to Python and SQL. For some of the UI elements, I have used the Bootstrap framework to create modals, navigation bars, forms, and the item cards.

JavaScript was used to populate the edit modal, show notifications once a day, add the `active` class to the current page link in the navigation bar, fetch the Spoonacular API if there isn't cached data, and populate the recipe modal.

## Motivation
I wanted to build this app because I find myself not remembering the exact dates when my products expire. This way there is a way to track everything in one place and also see what foods to make using the available ingredients.

I also see this project as something I might continue to improve and use in my day-to-day life beyond CS50. It isn't just the final project of this course, but it actually solves a real problem that I encounter. It gave me a sense of what it would be like to work on a bigger-scale project, from the brainstorming to get the idea to a fully working web app that is actually useful, which I have wanted to do for a long time, and for me this was the best start to the web development scene.

## Features
- Register for an account that you can log into and log out.
- Add new items with name, expiration date, and notes.
- View all items in a simple-to-understand card layout.
- Edit or delete existing items.
- Visual indicators for items that will soon expire or are already expired.
- Sends browser notifications about the items about to expire.
- Page to see recipes that use the items that the user has added with the Spoonacular API.
- Responsive layout for mobile.
- Uses caching for the API responses, so it doesn't have to use the API for duplicate requests.

## Files and Structure
- `app.py` - The main Flask application that has the routes and connects everything together.
- `templates/` - Contains all HTML files (default directory for Flask application) that use Jinja templates for cleaner code.
- `static/` - Contains the main `styles.css` file and a directory for images.
- `helpers.py` - Has some Python functions to declutter the main `app.py` file.
- `.env.example` - Template for the environment variables for the API and Flask's secret key.
- `requirements.txt` - A list of Python dependencies needed to run the project.
- `README.md` - This file documents the project.

## Technologies Used
- **Frontend:** HTML, CSS (Bootstrap), JavaScript
- **Backend:** Python (Flask)
- **Database:** SQLite

## Design Choices
One of the main design decisions was to build the project as a mobile app or a web app. I chose the web app because after some research I found out there isn't a way to run a Flask application on mobile, so when building the web app I had in mind to make it responsive so it would look like an app. Since many users would check their fridge inventory while shopping, it was important that the site was meant for the mobile users. That made me use an app-like, bottom-style navigation for smaller screens for easier usage.

## Challanges
Some of my main challenges were
- Learning how to use SQLite on Flask without the CS50 libraries.
	I had to research the libraries to import and how they work
	
- Learning how to use an API and how to secure APIs and other private keys with environment variables.
	When learning how to use environment variables, I experimented with different approaches before choosing the `.env` file with `python-dotenv`. This made sure my API keys stayed private, but I could still access them in development.
	
- Designing a UI that feels clean and is easy to use.
	I had to look for inspiration in other designs for displaying lists of items and find one that I liked and simplify it.
	
- Adding the right styles on elements so they work better on mobile.
	This was more of a trial-and-error challenge; I had to see what worked the best and implement that change.

## Future Improvements
- [ ] Implement a barcode scanner or image upload to add items faster and easier.
- [ ] Implement AI-generated recipes for a closer match in the available items.
- [ ] Implement theme switching, from light to dark.
- [ ] Implement a feature that shows the missing ingredients in the recipe modal.

## How to Run Locally
1. Clone the repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to a `.env` file and replace the placeholders with your own values (API key and Flask secret key).
4. Initialize the database by running `sqlite3 database.db < schema.sql`.
5. Run `flask run` inside the project directory.
6. Open the app at `http://127.0.0.1:5000/`.