import csv
import requests
from decouple import config

from django.http import HttpResponse
from django.shortcuts import render


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
    # homepage
    return render(request, 'getter/main.html')

################################################################################
#####                                Requests                              #####
################################################################################


def price_regions():
    url = URLS['price_region']
    price_regions = requests.get(url=url, headers=headers).json()
    return price_regions


def sell_price_rules():
    url = URLS['sell_price_rules']
    region_ids = (region['_id'] for region in price_regions())
    sell_price_rules = []
    for region_id in region_ids:
        params = {"_idregion": region_id,
                  "from": "2021-06-01", "to": "2021-09-30"}
        for rule in requests.get(url=url, headers=headers, params=params).json():
            sell_price_rules.append(rule)
    return sell_price_rules


def seazone_listings():
    url = URLS['listings']
    seazone_listings = []
    for listing in requests.get(url=url, headers=headers).json():
        seazone_listings.append(listing)
    return seazone_listings


def listings_sell_price():
    url = URLS['listing_sell_price']
    listing_ids = (listing['_id'] for listing in seazone_listings())
    listings_sell_price = []
    for listing_Id in listing_ids:
        params = {"listingId": listing_Id,
                  "from": "2021-06-01", "to": "2021-09-30"}
        for listing_sell_price in requests.get(url=url, headers=headers, params=params).json():
            listings_sell_price.append(listing_sell_price)
    return listings_sell_price

################################################################################
#####                             Exporters                                #####
################################################################################


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
    writer.writerow(['_id', 'name', 'type', 'from', 'to', 'status', 'minStay',
                     '_idregion', 'useMonthlyRate'])
    price_rules = ([rules['_id'], rules['name'], rules['type'], rules['from'], rules['to'],
                    rules['status'], rules['ratePlans'][0]['minStay'], rules['_idregion'],
                    rules['useMonthlyRate']] for rules in sell_price_rules())
    for rule in price_rules:
        writer.writerow(rule)
    return response


def export_seazone_listings(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="seazone-listings.csv"'
    writer = csv.writer(response)
    writer.writerow(['_id', 'id', '_t_propertyTypeMeta', '_idtype', '_t_typeMeta', 'subtype',
                     'internalName', '_mstitle', 'status', 'countryCode', 'stateCode', 'city', 'region',
                     'address', 'cep'])
    listings = ([listing['_id'], listing['id'], listing['_t_propertyTypeMeta']['_mstitle']['pt_BR'],
                 listing['_idtype'], listing['_t_typeMeta']['_mstitle']['pt_BR'], listing['subtype'],
                 listing['internalName'], listing['_mstitle']['pt_BR'], listing['status'],
                 listing['address']['countryCode'], listing['address']['stateCode'], listing['address']['city'],
                 listing['address']['region'], listing['address']['street'] +
                 ', ' + listing['address']['streetNumber'],
                 listing['address']['zip']] for index, listing in enumerate(seazone_listings()) if index > 2)
    for listing in listings:
        writer.writerow(listing)
    return response


def export_listings_sell_prices(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="listing-sell-prices.csv"'
    writer = csv.writer(response)
    writer.writerow(['_idlisting', '_idseason', 'type',
                    'status', 'from', 'to', 'minStay'])
    listings = ([listing['_idlisting'], listing['_idseason'], listing['type'],
                 listing['status'], listing['from'], listing['to'], listing['ratePlans'][0]['minStay']]
                for listing in listings_sell_price())
    for listing in listings:
        writer.writerow(listing)
    return response

# -Organize a DataFrame that contains the price for each listing for each
#  day from June/2021 to September/2021
