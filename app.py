from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import os
import logging

logging.basicConfig(filename="producReview.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    reviews=[]
    if request.method == 'POST':
        try:

            page=1
            save_directory = "data/csv/"
            product_url = request.form['content'].replace(" ","")
            
            # create the directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
                
            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            
            # fetch the search results page
            response = requests.get(product_url)

            #verify response code
            if response.status_code != 200:
                logging.error(f"Error: unable to access productUrl:{product_url}, statusCode:{response.status_code}\n")
                return render_template('error.html', error=f"Unable to access given url Error Code:{response.status_code}")
            else:
                logging.info(f"Started: fetch review")

                soup = BeautifulSoup(response.content, "html.parser")
                product=soup.findChildren("div", class_="_2s4DIt _1CDdy2")[0].text
                
                next_page = True

                while next_page!=False:
                    
                    logging.info(f"Started: get review from page:{page}, productUrl:{product_url}")
                    
                    div_tag = soup.find_all("div", class_="col _2wzgFH K0kLPL")
                    for div in div_tag:
                        name=div.findChildren("p", class_="_2sc7ZR _2V5EHH")[0].text
                        comment_head=div.findChildren("p", class_="_2-N8zT")[0].text
                        comment=div.findChildren("div", class_="t-ZTKy")[0].text
                        rating=div.findChildren("div", class_="_3LWZlK _1BLPMq")[0].text

                        review = {"Product":product, "Name":name, "Rating":rating, "CommentHead":comment_head, "Comment":comment}
                        reviews.append(review)
                    
                    logging.info(f"End: get review from page:{page}")

                    a_next = soup.find_all("a", class_="_1LKTO3")
                    
                    if a_next[0].text != 'Next':
                        next_page = False
                    else:
                        product_url = "https://flipkart.com" + a_next[0]['href']

                        response = requests.get(product_url)
                        soup = BeautifulSoup(response.content, "html.parser")
                        page+=1

        except Exception as e:
            logging.error(f"Error: {e}")
            return 'something is wrong'
        
        return render_template('result.html', reviews=reviews, a="a")

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
