import json
import time

from ebay import find_offers


offers_found = set()


while True:
    with open("input.json") as file:
        books_input = json.loads(file.read())
    offers = []
    for book in books_input:
        offers += find_offers(book["isbn"], book["price"])
    offers = [offer for offer in offers if offer.url not in offers_found]
    for o in offers:
        offers_found.add(o.url)
    if offers:
        body = "\n".join("\n".join((offer.title, offer.url, str(offer.price))) for offer in offers)
        print (body)
    time.sleep(60 * 5)



