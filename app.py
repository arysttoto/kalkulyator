from flask import Flask, render_template, request, Response, jsonify, request 
from cs50 import SQL 
from datetime import datetime 
from flask_caching import Cache
import xml.etree.ElementTree as ET


# Configure application
app = Flask(__name__) 

# Configure cache
app.config['CACHE_TYPE'] = 'simple'  # In-memory caching
cache = Cache(app) 
# High-priority pages to cache for 24 hours (86400 seconds)
cache_time = 86400  # 1 day

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kalkulyator.db") 


# sitemap/robots routes
@app.route("/sitemap.xml") 
def sitemap():
    # Base domain (change this to your actual domain)
    domain = "https://www.kalkulyator.kz"

    # List of static pages (update this if you add new sections)
    urls = [
        ("/", "daily", "1.0"),
        ("/kontakty/", "monthly", "0.8"),
        ("/finansy/", "weekly", "0.9"),
        ("/finansy/kreditnyj-kalkulyator/", "weekly", "0.9"),
        ("/finansy/ipotechnyj-kalkulyator/", "weekly", "0.9"),
        ("/matematika/", "weekly", "0.9"),
        ("/matematika/kvadratnoe-uravnenie/", "weekly", "0.9"),
        ("/matematika/procenty/", "weekly", "0.9"),
        ("/matematika/ploshchad-figur/", "weekly", "0.9"),
        ("/fizika/", "weekly", "0.9"),
        ("/fizika/zakon-oma/", "weekly", "0.9"),
        ("/fizika/skorost-vremya-rasstoyanie/", "weekly", "0.9")
    ]

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Generate XML for each page
    for url, changefreq, priority in urls:
        url_element = ET.SubElement(urlset, "url")
        
        loc = ET.SubElement(url_element, "loc")
        loc.text = f"{domain}{url}"

        lastmod = ET.SubElement(url_element, "lastmod")
        lastmod.text = datetime.now().strftime("%Y-%m-%d")  # Update to today's date

        changefreq_tag = ET.SubElement(url_element, "changefreq")
        changefreq_tag.text = changefreq

        priority_tag = ET.SubElement(url_element, "priority")
        priority_tag.text = priority

    # Convert XML to string
    xml_str = ET.tostring(urlset, encoding="utf-8", method="xml")
    
    return Response(xml_str, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    return Response(
        "User-agent: *\nAllow: /\n\nSitemap: https://www.kalkulyator.kz/sitemap.xml",
        mimetype="text/plain"
    ) 
#################################################

# error handlers
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
##############################################

# basic routes section
@app.route("/")
@cache.cached(timeout=cache_time) 
def index():
    return render_template("index.html")  


@app.route("/kontakty/", methods=["GET", "POST"]) 
def contact(): 
    if request.method == "POST": 
        name = request.form.get('name')
        email = request.form.get('email')        
        message = request.form.get('message') 

        # check all values for presence, and validate them if needed 
        if not name:
            return jsonify({'error': 'Must provide name'}), 400
        if not email:
            return jsonify({'error': 'Must provide email'}), 400
        if not message:
            return jsonify({'error': 'Must provide message'}), 400
        
        # try to add inquiry to database
        try:
            date_now = datetime.now() 
            db.execute("INSERT INTO inquiries (name, email, message, date) VALUES (?, ?, ?, ?)",
                       name, email, message, date_now.strftime("%d %B %Y")) 
        except Exception:
            return jsonify({'error': 'Unknown server error'}), 500
        
        # finally, return success
        return jsonify({'status': 'success'}), 200 
    else:
        return render_template("contact.html") 
###################################################################

# finance section
@app.route("/finansy/") 
@cache.cached(timeout=cache_time) 
def finance_calculators():
    return render_template("finance.html")  


@app.route("/finansy/kreditnyj-kalkulyator/") 
@cache.cached(timeout=cache_time)
def credit_calculator():
    return render_template("/finance/credit_calculator.html")  


@app.route("/finansy/ipotechnyj-kalkulyator/") 
@cache.cached(timeout=cache_time)
def mortgage_calculator():
    return render_template("/finance/mortgage_calculator.html")  
###################################################################

# math section
@app.route("/matematika/") 
@cache.cached(timeout=cache_time) 
def math_calculators():
    return render_template("math.html") 


@app.route("/matematika/kvadratnoe-uravnenie/")
@cache.cached(timeout=cache_time) 
def quadratic_equations_calculator():
    return render_template("/math/quadratic_equations_calculator.html")


@app.route("/matematika/procenty/")
@cache.cached(timeout=cache_time)
def percent_calculator():
    return render_template("/math/percent_calculator.html") 


@app.route("/matematika/ploshchad-figur/")
@cache.cached(timeout=cache_time)
def area_calculator():
    return render_template("/math/area_calculator.html") 
###################################################################

# physics section 
@app.route("/fizika/")
@cache.cached(timeout=cache_time) 
def physics_calculator():
    return render_template("physics.html")  


@app.route("/fizika/zakon-oma/")
@cache.cached(timeout=cache_time)
def ohms_law_calculator():
    return render_template("/physics/ohms_law_calculator.html") 


@app.route("/fizika/skorost-vremya-rasstoyanie/")
@cache.cached(timeout=cache_time)
def speed_time_distance_calculator():
    return render_template("/physics/speed_time_distance_calculator.html") 
###################################################################

if __name__ == "__main__":
    app.run() 