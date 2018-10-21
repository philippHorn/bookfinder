from datetime import datetime, timedelta
from config import SECURITY_APPNAME
import requests


url = 'https://svcs.ebay.com/services/search/FindingService/v1'
base_params = {
    "SECURITY-APPNAME": SECURITY_APPNAME,
    'RESPONSE-DATA-FORMAT': 'JSON',
    'GLOBAL-ID': 'EBAY-DE',
    'SERVICE-VERSION': '1.0.0',
    'OPERATION-NAME': 'findItemsByProduct',
    'productId.@type': "ISBN",
    'productId': '0300188374',
    'paginationInput.pageNumber': 1,
}


class Offer:
    def __init__(self, data):
        self.price = data["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"]
        assert data["sellingStatus"]["convertedCurrentPrice"][0]["@currencyId"] == "EUR"
        self.listing_types = [info["listingType"][0] for info in data["listingInfo"]]

        # we assume all listing types have same date for now:
        end_date = data["listingInfo"][0]["endTime"][0]
        self.end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")

        self.url = data['viewItemURL']
        self.title = data["title"]

    @property
    def is_auction(self):
        return "Auction" in self.listing_types


def _collect_all_products(isbn):
    params = {"productId": isbn}
    params.update(base_params)
    response_data = requests.get(url, params).json()["findItemsByProductResponse"][0]
    results = response_data["searchResult"][0]["item"]
    while response_data["paginationOutput"][0]["pageNumber"] < response_data["paginationOutput"][0]["totalPages"]:
        params['paginationInput.pageNumber'] += 1
        response_data = requests.get(url, params).json()["findItemsByProductResponse"][0]
        results += response_data["searchResult"][0]["item"]
    return [Offer(data) for data in results]


def find_offers(isbn, price):
    offers = _collect_all_products(isbn)
    offers = [offer for offer in offers if offer.price > price]

    # if there are auctions, only include them if there is one day left till they end
    offers = [
        offer for offer in offers
        if not offer.is_auction and (offer.end_date - datetime.now()) > timedelta(days=2)
    ]
    return offers



