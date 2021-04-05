import csv
import requests
from decouple import config

from django.http import HttpResponse
from django.shortcuts import render
# from django.http import StreamingHttpResponse


URLS = {
    # Price Regions in the system
    'price_region': 'https://ssl.stays.com.br/external/v1/parr/price-regions',
    # Sell Price Rules for each region
    'sell_price_rules': 'https://ssl.stays.com.br/external/v1/parr/seasons-sell',
    # Acquire Seazone's listings
    'listings': 'https://ssl.stays.com.br/external/v1/content/listings',
    # Retrieve all Listings Sell Prices
    'listing_sell_price': 'https://ssl.stays.com.br/external/v1/parr/listing-rates-sell'
}

headers = {"Authorization": config('AUTHORIZATION'),
           "Content-Type": "application/json"}


def main(request):
    return render(request, 'getter/main.html')


def price_regions():
    url = URLS['price_region']
    try:
        request = requests.get(url=url, headers=headers)
    except:
        raise ValueError(
            f"Error {requests.get(url=url, headers=headers).status_code}\n")
    return request.json()


def sell_price_rules():
    url = URLS['sell_price_rules']
    region_ids = (region['_id'] for region in price_regions())
    sell_price_rules = []
    for region_id in region_ids:
        for rule in requests.get(url, headers=headers, params={"_idregion": region_id}).json():
            sell_price_rules.append(rule.values())
    return sell_price_rules


def seazone_listings():
    url = URLS['listings']
    listings_details = []
    for listing in requests.get(url=url, headers=headers).json():
        listings_details.append(listing.values())
    return listings_details


def export_price_regions(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="price-regions.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'name'])

    regions = ([region['_id'], region['name']] for region in price_regions())
    for region in regions:
        writer.writerow(region)
    return response


def export_sell_price_rules(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sell-prices-rules.csv"'
    writer = csv.writer(response)
    writer.writerow(requests.get(URLS['sell_price_rules'], headers=headers, params={
                    "_idregion": price_regions()[0]["_id"]}).json()[0].keys())
    price_rules = (rules for rules in sell_price_rules())
    for rule in price_rules:
        writer.writerow(rule)
    return response


def export_seazone_listings(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="seazone-listings.csv"'
    writer = csv.writer(response)
    writer.writerow(requests.get(
        URLS['listings'], headers=headers).json()[0].keys())
    listings = (listing for listing in seazone_listings())
    for listin in listings:
        writer.writerow(listin)
    return response


# -Organize a DataFrame that contains the price for each listing for each
#  day from June/2021 to September/2021
