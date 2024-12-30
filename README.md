# Duck Language Learning  
## Learn French with Interactive Lessons and Quizzes
## Video demo: https://www.youtube.com/watch?v=5nLuII_nQfc  

Duck Language Learning is a CS50x final project built with Flask. The app helps users learn basic French through interactive lessons, quizzes, and audio exercises. User data is stored in a SQLite database.

## Introduction
 
 - **Why a french language learning app**
 French is the 5th most spoken language in the world and trade relationship between France and the United States is strong and continues to grow.
 In 2023, exchanges continued to grow, reaching €167.4 billion, including €97 billion for goods and €70.4 billion for services. (diplomatie.gouv.fr). Reciprocal investments between the two countries totaled $406 billion in 2022. The United States remains the primary destination for French investments abroad and is the leading foreign investor in France. (washington.consulfrance.org). The French-American economic partnership has created over 1.2 million jobs. Yet, a lot of those opportunities are lost because, let's be honest a lot of people in France struggle with English even if they have taken it as the primary foreign language in school. So why not create a bridge and meet each other halfway through.

 - **My experience creating this project**
 One of the first challenge I encountered was the sqlite database. I realized very quickly that the CS50 environment did a lot of work for us behind the scene and things worked differently in a real development environment. The second one was how to handle session. While we encounter sessions in the final problem set, everything is done for us and I wasn't quite sure how things worked and I'm still a bit confused to be honest. The last and probably the most challenging part was the self hosting and the automated deployment process. While I had the server set up and ready to go before starting CS50, this is the first website I actually self host. The automated process was written entirely by Chat-GPT but I had to spend a lot of time debugging to make things work properly. From a more general point of view I still struggle a bit with dictionary and list of dictionary syntax but make this project helped me quite a lot. I had a lot of fun creating it and I will keep working on it after CS50.
    

## Key Features  

- **Secure Registration and Login:**  
  Users must register via the "Register" link to access lessons. Once registered, they can log in and access the dashboard.  
- **Interactive Lessons:**  
  Each lesson includes vocabulary and audio samples to aid pronunciation.  
- **Quizzes:**  
  Users can test their knowledge through quizzes linked to each lesson, accessible from the lesson page or directly from the dashboard.  
- **Score Tracking:**  
  Quiz scores are viewable on the "Scoreboard" in the account menu.  
- **Account Management:**  
  Users can change their password or delete their account. Deleting an account is irreversible and removes all associated data from the database.  

---

## Hosting  

The app is self-hosted on a Debian 12 server with:  
- **Web Server:** Nginx  
- **Application Server:** Gunicorn  
- **Domain:** Free DuckDNS service  
- **Access:** [ducklanguagelearning.duckdns.org](http://ducklanguagelearning.duckdns.org)  

---

## Project Structure  

### Main Files and Folders  

- **`/static`**  
  Contains audio files, images, icons, and the `style.css` file. Media queries ensure a responsive design for both desktop and mobile.  
- **`/templates`**  
  Contains HTML files structured with `layout.html` as the base template, extended dynamically using Jinja2.  
- **`app.py`**  
  The main application logic, Flask routes, and session management. Key libraries include:  
  - Flask  
  - Flask-Session (for session management)  
  - Werkzeug-Security (for password hashing and verification)  
  - SQLite3 (for database operations).  
- **`data.py`**  
  Contains dictionaries used for lessons to keep `app.py` lightweight.  
- **`duck.db`**  
  SQLite database with two tables:  
  1. **Users:** Stores unique IDs, usernames, and hashed passwords.  
  2. **Quiz Results:** Stores quiz scores linked to user IDs from the Users table.  
- **`helper.py`**  
  Includes utility functions adapted from the CS50 Finance problem set.  
- **`logging_config.py`**  
  Configures logging for tracking app behavior during development and production.  
- **`requirements.txt`**  
  Lists dependencies for automated installation in production.  

---

## Automation and Tools  

- **Continuous Deployment:**  
  Updates are automatically deployed using GitHub Actions after every push to the main repository.  
- **SSL Certificate:**  
  Let's Encrypt secures the domain with HTTPS.  
- **External Resources:**  
  - Navigation Bar: Bootstrap  
  - Gradients: CSS Gradient  
  - Font: Playfair Display (Google Fonts)  
  - Audio Files: ttsmaker.com  
  - Image Generation: Microsoft Bing
  - Switch button from w3schools.com

---

## Development and Maintenance  

### Logging  

- **Development:** Logs are available in `app.log`.  
- **Production:** Gunicorn logs are available for monitoring app behavior.  

---

## Credits  

- **ChatGPT:** Assistance with problem-solving and creating the automated deployement process.  
- **CS50 Problems:** Certain functions are adapted from CS50 problem sets, particularly the Finance problem.  

---

## Contact  

Feel free to reach out if you have suggestions or would like to contribute!  
[Email me here.](mailto:ludovic.brot@gmail.com)  

---  

### Notes  

This README has been improved for clarity, structure, and formatting. Let me know if you have additional feedback or need further modifications!  
