#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Import the following modules
import requests
import cv2
import os
from requests import exceptions

# Set your subscription key and search endpoint
SUBSCRIPTION_KEY = "" # YOUR_API_KEY_GOES_HERE
SEARCH_URL = "https://api.bing.microsoft.com/v7.0/images/search"

# Set the maximum number of results for a given search and the group size for results (maximum of 50 per request)
MAX_RESULTS = 250
GROUP_SIZE = 50


# In[ ]:


# Build the list of exceptions that can be thrown when attempting to download images
EXCEPTIONS = set([IOError, FileNotFoundError,
	exceptions.RequestException, exceptions.HTTPError,
	exceptions.ConnectionError, exceptions.Timeout])


# In[ ]:


# Set your search query
SEARCH_TERM = "Blade Runner 1982 Roy Batty"

# Set your headers and search parameters
HEADERS = {"Ocp-Apim-Subscription-Key" : SUBSCRIPTION_KEY}
PARAMS = {"q": SEARCH_TERM, "mkt": "en-US", "offset": 0, "count": GROUP_SIZE}


# In[ ]:


# Perform the search
print(f"[INFO] Searching Bing API for '{SEARCH_TERM}'")
search = requests.get(SEARCH_URL, headers=HEADERS, params=PARAMS)
search.raise_for_status()

# Grab the results from the search, including the total number of estimated results returned by the Bing API
results = search.json()
estimatedNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)
print(f"[INFO] {estimatedNumResults} total results for '{SEARCH_TERM}'")


# In[ ]:


# Keep a counter of the images downloaded
total = 0

# Loop over the estimated number of results in `GROUP_SIZE` groups
for offset in range(0, estimatedNumResults, GROUP_SIZE):
	# Update the search parameters using the current offset
	print(f"[INFO] Making request for group {offset}-{offset + GROUP_SIZE} of {estimatedNumResults}...")
	PARAMS["offset"] = offset
    
	# Make the request to fetch the results
	search = requests.get(SEARCH_URL, headers=HEADERS, params=PARAMS)
	search.raise_for_status()
	results = search.json()
	print(f"[INFO] Saving images for group {offset}-{offset + GROUP_SIZE} of {estimatedNumResults}...")
    
    # Loop over the results
	for v in results["value"]:
		# Try to download the image
		try:
			# Make a request to download the image
			print(f"[INFO] Fetching: {v['contentUrl']}")
			r = requests.get(v["contentUrl"], timeout=30)
			
            # Build the path to the output image
			ext = v["contentUrl"][v["contentUrl"].rfind("."):]
			path = os.path.sep.join(["C:/Users/fatih.gokmenoglu/Downloads/replicant-or-not/Roy Batty/", f"{str(total).zfill(8)}{ext}"])
            
			# Write the image to disk
			f = open(path, "wb")
			f.write(r.content)
			f.close()
		# Catch any errors that would not unable us to download the image
		except Exception as e:
			# Check to see if our exception is in our list of exceptions to check for
			if type(e) in EXCEPTIONS:
				print(f"[INFO] Skipping: {v['contentUrl']}")
				continue
                
        # Try to load the image from disk
		image = cv2.imread(path)
        
		# If the image is `None` then we could not properly load the image from disk (so it should be ignored)
		if image is None:
			print(f"[INFO] Deleting: {path}")
			os.remove(path)
			continue
            
		# Update the counter
		total += 1

