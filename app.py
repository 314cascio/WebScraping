# 1. import Flask
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# 3. Define index
@app.route('/')
def index():
    # Return the template 
    mars = mongo.db.mars.find_one()
    return render_template('index.html', mars=mars)

# 3. Define scrape route
@app.route('/scrape')
def scrape_data():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape_all()
    mars.update({}, mars_data, upsert=True)
    return "Scraping Successful"

# 4.
if __name__ == "__main__":
    app.run()
