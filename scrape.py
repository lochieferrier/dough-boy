from bs4 import BeautifulSoup

import requests

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

listingURLs = extractListingURLs("https://worcester.craigslist.org","/search/cta?query=volvo&sort=date&searchNearby=2&nearbyArea=59&nearbyArea=4&nearbyArea=239&nearbyArea=451&nearbyArea=281&nearbyArea=686&nearbyArea=44&nearbyArea=249&nearbyArea=250&nearbyArea=169&nearbyArea=198&nearbyArea=168&nearbyArea=3&nearbyArea=354&nearbyArea=338&nearbyArea=38&nearbyArea=378&nearbyArea=93&nearbyArea=173&min_price=100&max_price=3000")
print len(listingURLs)