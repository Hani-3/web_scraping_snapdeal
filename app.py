from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
from pymongo.mongo_client import MongoClient

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            snapdealurl = "https://www.snapdeal.com/search?keyword=" + searchString
            uClient = requests.get(snapdealurl)
            uClient.encoding='utf-8'
            uClient = uClient.text
            snapdeal_html = bs(uClient, "html.parser")
            bigboxes = snapdeal_html.select(".product-desc-rating ")
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Product Name, original price, discounted price, total rating, filled stars(%) \n"
            fw.write(headers)
            reviews = []
            for bigbox in bigboxes:
                try:
                    product_name = bigbox.select(".product-title ")
                    product_name = product_name[0].getText()

                except:
                    logging.info("product_name")

                try:
                    original_price = bigbox.find_all("span","lfloat product-desc-price strike")
                    original_price = original_price[0].getText()

                except:
                    logging.info("original_price")

                try:
                    discounted_price = bigbox.find_all("span","lfloat product-price")
                    discounted_price = discounted_price[0].getText()

                except:
                    logging.info("discounted_price")
                try:
                    total_rating = bigbox.find_all("p","product-rating-count")
                    total_rating = total_rating[0].getText()
                except Exception as e:
                    total_rating = 0
                    logging.info(e)

                try:
                    filled_stars = bigbox.select(".filled-stars")
                    for j in filled_stars:
                        filled_star_style = j.get("style")
                        filled_star_perc = filled_star_style[6:11]
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "product_name": product_name, "original_price": original_price, "discounted_price": discounted_price,
                          "total_rating": total_rating, "filled_star_perc": filled_star_perc}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            uri = "mongodb+srv://hanypatel1603:datascience@cluster0.0dm5hfx.mongodb.net/?retryWrites=true&w=majority"

            # Create a new client and connect to the server
            client = MongoClient(uri)

            # Send a ping to confirm a successful connection
            try:
                client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                print(e)
            
            db = client['review_scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")

