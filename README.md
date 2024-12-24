# CS50_final
## Duck language learning


### Duck language learning is a CS50x final project built in Flask. Users datas are stored in a SQLite database. The goal of the app is to teach French at a basic level with a mix of vocabulary and quizzes and more general lessons. 
### Before accessing lessons users are required to register using the Register link on the top right corner of the page.
### After registering users should login using their credientials to access the dashboard menu. They should then access the lesson they desire to take which contains audio sample to help with pronunciation.They should then access the quiz corresponding to the lesson by clicking the button below the lesson or directly from the dashboard. All the result of the test can be accessed in the account menu by clicking on the scoreboard button. In the same menu users can change their password and delete their account should they desire so. Deleting account is not reversible and remove all the user data from the database.

### The app is self hosted on a Debian 12 server using nginx,gunicorn and a free duckdns.org domain and can be accessed at ducklanguagelearning.duckdns.org

### The static folder contains all the audio samples used by the app as well as the images and icons. The style.css file works with the Html file to format them correcty. The media query ensure the app looks good both on computer and mobile.
### The templates folder contains all the html files of the app. All the files are extensions of the layout.html files that contains the layout of the app which all other files uses using jinja to add to this layout. Some of the content of those html files is generated with jinja from the app.py file.
### The app.py is the file that contains all the logic of the app. The python library we used are imported on this file such as Flask,Flask_session,werkzeug_security,sqlite3... Each route in the file is linked to an HTML page. The Flask session library allow to store temporary data such as the name of the user, it's current score in the quizzes.All those data can be cleared using the function session.clear.The werkzeug_security library allow to generate hashes to safely store user password in database. It's check_password_hash function allow to compare those hashes to the password the user enter while login in.

### The data.py file contains dictionnary used by the lesson to save space in the app.py file.
### Duck.db is the sqlite3 database. It contains 2 tables, One to store users usernames and hashed password, each users being associated with a unique id, two a quizz result table which store all results from quizzes.All results are associated with user id from the users table to prevent repetition as much as possible.

### The helper.py file contains functions from the Finance problem. Some of the code from this app is reused from my version of the finance problem set.




### Image generated with Microsoft Bing.
### Audio files generated with ttsmaker.com.
### CHAT GPT to assist with problem solving.
### Nav bar from Bootstrap.
### Gradient generated with CSS Gradient.
### Font Playwrite Colombia from google font.
### SSL certificate from Let's Encrypt