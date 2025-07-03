import csv
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

books = []
cart = []

# Helper functions

def load_books():
    global books
    with open("books.csv", "r") as file:
        reader = csv.DictReader(file)
        books = [row for row in reader]

def search_books(keyword):
    matches = []
    
    for book in books:
        if  keyword.lower() in book["Title"].lower() or \
            keyword.lower() in book["Author"].lower() or \
            keyword.lower() in book["Genre"].lower():
                matches.append(book)
        return matches
    
def add_to_cart(book_id, cart):
    for book in books:
        if int(book["id"]) == book_id:
            cart.append(book)
            return True
    return False

def checkout(cart):
    total = sum(float(book["Price"] for book in cart))
    try:
        response = requests.post("http//paymentgateway.com/process", data={"Total": total}, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.Timeout:
        print("Timeout")
    except requests.exceptions.RequestException:
        print("RequestException")

# Endpoints

@app.route("/books")
def get_books():
    return jsonify(books)

@app.route("/search")
def search():
    keyword = request.args.get("q", '')
    results = search_books(keyword)
    return jsonify(results)

@app.route("/cart", methods=["GET"])
def view_cart():
    return jsonify(cart)

@app.route("/cart", methods=["POST"])
def add_to_cart():
    book_id = request.json["id"]
    
    if add_to_cart(book_id, cart):
        return jsonify({"message": "Book added to cart."})
    else:
        return jsonify({"error": "Book not found!"})

@app.route("/checkout", methods=["POST"])
def checkout_cart():
    if cart:
        if checkout(cart):
            cart.clear()
            return jsonify({"message": "Payment processed successfully."})
        else:
            return jsonify({"error": "Payment failed, Please try again."})
    else:
        return jsonify({"error": "Your cart is empty."})

# Main
if __name__ == "__main__":
    load_books()
    app.run(host="0.0.0.0", debug=True)