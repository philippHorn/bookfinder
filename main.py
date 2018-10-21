import json
import time

from ebay import find_offers


while True:
    with open("input.json") as file:
        books_input = json.loads(file.read())
    offers = [find_offers(b["isbn"], b["price"]) for b in books_input]

    if offers:
        body = "\n".join("\n".join((offer.title, offer.url)) for offer in offers)
    time.sleep(60 * 5)



