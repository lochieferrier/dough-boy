from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import dryscrape
import ast

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def extractListingURLs(baseURL,searchURL):
	nextLink = "bigpotato"
	startLink = searchURL
	count = 0
	listingURLs = []
	while nextLink != "":
		if count == 0:
			nextLink = startLink

		baseurl = baseURL
		url = baseurl+nextLink

		r  = requests.get(baseurl + nextLink)

		data = r.text

		soup = BeautifulSoup(data,"lxml")

		nextLink = ""

		for link in soup.find_all('a',text='next > '):
			# print link['href']
			# Take the next page link
			nextLink = link['href']
		result = soup.find_all('a',{'class':'result-title hdrlnk'})
		if len(result) == 0:
			nextLink = ""
		else:
			for a in result:
				listingURLs += [a['href']]
		count = count + 1
		# print listingURLs
	return listingURLs

def valueListing(listingURL):
	r = requests.get(listingURL)
	data = r.text
	soup = BeautifulSoup(data,"lxml")

	attrs = soup.find_all('p',{'class':'attrgroup'})
	if len(attrs) > 0:
		typeStr = (attrs[0].find('b').text).lower()
		splitStr = typeStr.split()
		if len(splitStr)==3:
			year = splitStr[0]
			make = splitStr[1]
			model = splitStr[2]
		
			# Now we have a car to work with, we need to figure out what type it is to plug into KBB
			# This is tricky, so we're just going to use the base vehicle.
			KBBstyles = getKBBStyles(year,make,model)
		else:
			# print 'failed to split typestr'
			year = ""
			make = ""
			model = ""
			KBBstyles = []
		# These URLs are coming out with a little bad stuff on them, such as a vehicleid, and /options/
		# which if left unremidied will make KBB ask too many questions
		# let's fix that
		if len(KBBstyles) < 1:
			# print 'triggered google search'
			# Find what the thing is meant to be named with Google
			stylesURL = getKBBURLWithGoogle(typeStr)
			stylesURL = stylesURL.split('/')
			# print stylesURL
			if len(stylesURL) == 7:

				make = stylesURL[3]
				model = stylesURL[4]
				year = stylesURL[5]
				KBBstyles = getKBBStyles(year,make,model)
				# print 'rigged with google results'
				# print KBBstyles
			else:
				# print 'failed to get KBB from URL'
				KBBstyles = []
		if len(KBBstyles) > 0:
			# Also, we take the first body style (cheapest option)
			finalURL = 'https://www.kbb.com/'+make+'/'+model+'/'+year+'/'+KBBstyles[0]+'/?intent=buy-used&pricetype=private-party&condition=good&persistedcondition=good'
			price = getKBBPrice(finalURL)
			asking = soup.find('span',{'class':'price'})
			asking = asking.text.replace('$','')
			asking = int(asking)
			rego = 135 + asking*0.0625
			inspection = 35
			upside = price - asking - rego - inspection
			return upside
		else:
			print 'failed on KBB styles check ' + year + make + model
			return -99
	else:
		return -99
def getKBBURLWithGoogle(typeStr):
	r = requests.get("https://www.google.com/search?ei=0HUKWv7dD4WBmQHQgLbgCg&q="+ typeStr+ "+kbb&oq="+typeStr+"+kbb&gs_l=psy-ab.3...748.1248.0.1384.4.4.0.0.0.0.0.0..0.0....0...1.1.64.psy-ab..4.0.0....0.i4xIQXc_4l8")
	data = r.text
	soup = BeautifulSoup(data,"html.parser")
	c = soup.find('cite')
	return c.text
def getKBBPrice(vehicleURL):
	# time.sleep(5)
	# # myDynamicElement = driver.find_element_by_id("RangeBox")
	# # print myDynamicElement
	r = requests.get(vehicleURL)
	html = r.text
	soup = BeautifulSoup(html, 'html.parser')
	g = soup.find_all('div',{'id':'priceAdvisor'})
	if len(g) < 1:
		return 999999
	else:
		data = g[0]['data-config']
		dataDict = ast.literal_eval(data)
		priceURL = 'https://www.kbb.com' + dataDict['urls']['private-party']
		URLarr = priceURL.split('&')
		vehicleID = URLarr[4].split('=')[1]
		mileage = URLarr[6].split('=')[1]
		priceURL = "https://www.kbb.com/Api/3.8.13.0/62764/vehicle/upa/PriceAdvisor/meter.svg?action=Get&intent=buy-used&pricetype=Private%20Party&zipcode=02215&vehicleid="+vehicleID+"&condition=good&mileage="+mileage
		# r = webdri`ver.PhantomJS('phantomjs',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
		r = requests.get(priceURL)
		html = r.text
		soup = BeautifulSoup(html,'html.parser')
		price = soup.find('text',{'data-reactid':'58'})
		# print html
		p = price.text.split(' ')[0]
		p = p.replace(',','')
		p = p.replace('$','')
		p = int(p)
		return p
def getKBBStyles(year,make,model):
	# print 'gettingstyle'
	# print` year + make + model
	url = 'https://www.kbb.com/'+make+'/'+model+'/'+year+'/styles/'
	# print url
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data,"lxml")
	styleElems = soup.find_all('a',{'class':'right btn-main-cta'})
	styles = []
	# Maybe we got one of the weird ones where it autoredirects, in this case we want to pull the style from the URL

	for style in styleElems:
		KBBURL = style['href']
		styles += [KBBURL.split('/')[4]]

	if len(styleElems) == 0:
		styleElems = soup.find_all('meta',{'property':'og:url'})
		styles = [styleElems[0]['content'].split('/')[6]]
	return styles

listingURLs = extractListingURLs("https://worcester.craigslist.org","/search/cta?query=volvo&sort=date&searchNearby=2&nearbyArea=59&nearbyArea=4&nearbyArea=239&nearbyArea=451&nearbyArea=281&nearbyArea=686&nearbyArea=44&nearbyArea=249&nearbyArea=250&nearbyArea=169&nearbyArea=198&nearbyArea=168&nearbyArea=3&nearbyArea=354&nearbyArea=338&nearbyArea=38&nearbyArea=378&nearbyArea=93&nearbyArea=173&min_price=100&max_price=3000")
# print len(listingURLs)
print str(len(listingURLs)) + " vehicles loaded"
# listingURLs = ['https://westernmass.craigslist.org/cto/d/2000-volvo-v40-90k-999-bo/6383398328.html']
for listingURL in listingURLs:
	upside = valueListing(listingURL)
	print [upside,listingURL]