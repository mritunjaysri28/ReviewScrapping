from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import os
import csv
import logging

logging.basicConfig(filename="productReview.log" , level=logging.INFO)

app = Flask(__name__)

def get_url_response(url):
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Error: unable to access productUrl:{url}, statusCode:{response.status_code}\n")
        return render_template('error.html', error=f"Unable to access given url Error Code:{response.status_code}")
    
    logging.info(f"Navigate: {url}")
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    
    if request.method == 'POST':
        try:
            page=1
            reviews=[]
            next_page_flag=True
            url="https://flipkart.com"
            save_directory = "data/csv/"
            col_class="col _2wzgFH"
            
            product_url = request.form['content'].replace(" ","")

            if product_url.__contains__('product-reviews'):
                return render_template('error.html', error=f"Enter product page url not product review page url\n {product_url}")

            # create the directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)


            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetch the search results page
            soup = get_url_response(product_url)
            
            logging.info(f"Started: fetch review")

            #fetch product name
            product=soup.find("span", class_="B_NuCI").text

            all_reviews=soup.find("div", class_="_3UAT2v _16PBlm")
            
            if all_reviews!=None:
                soup=get_url_response(url+all_reviews.parent['href'])
                col_class="col _2wzgFH K0kLPL"
            
                
            while next_page_flag:
                logging.info(f"Started: get review from page:{page}, productUrl:{product_url}")
                div_tags = soup.find_all("div", class_=col_class)

                for div in div_tags:
                    name=div.findChildren("p", class_="_2sc7ZR _2V5EHH")[0].text
                    comment_head=div.findChildren("p", class_="_2-N8zT")[0].text
                    comment=div.findChildren("div", class_="t-ZTKy")[0].text
                    # rating=div.div.div("div", class_="_3LWZlK _1BLPMq")[0].text
                    rating=div.div.div.text
                    review = {"Product":product, "Name":name, "Rating":rating, "CommentHead":comment_head, "Comment":comment}
                    reviews.append(review)
                
                logging.info(f"Ended: get review from page:{page}, {reviews}")
                
                a_next = soup.find_all("a", class_="_1LKTO3")
                if not a_next or a_next[0].text != 'Next':
                    next_page_flag = False
                else:
                    product_url = "https://flipkart.com" + a_next[0]['href']
                    soup = get_url_response(product_url)
                    page+=1
            
            with open(f"{save_directory}/flipkartProductReview.csv", 'w', newline='') as csvfile: 
                writer = csv.DictWriter(csvfile, fieldnames = ["Product", "Name", "Rating", "CommentHead", "Comment"], delimiter=',') 
                writer.writeheader() 
                writer.writerows(reviews) 

            return render_template('result.html', reviews=reviews, a="a")
        except Exception as e:
            logging.error(f"Error: {e}")
            return render_template('error.html', error=f"some thing went wrong, Verify URL\n {e}")
        
    else:
        logging.error(f"Error: url request is not POST")
        return render_template('error.html', error=f"Its not you, URL request is not POST type")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)