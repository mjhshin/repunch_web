"""
Get the image urls from a google image page.
"""

import requests, re

RE_URL = re.compile(r'src="(https.*?)"')

OUTPUT_FILENAME = "docs/create_store/image_urls.txt"
IMG_QUERY = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ei=Y8PaUrK9BMjTsASz74GICg&ved=0CAcQ_AUoAQ&biw=1366&bih=653"
IMG_SEARCHES = ( "books", "meat", "bread", "babes", "houses", 
    "canned+foods", "smartphone", "groceries", "coffee", "casino",
    "toys", "cartoons", "beer", "guns", "fitness")

def get_img_urls(url):
    # return the first 20 results
    return RE_URL.findall(requests.get(url).content)[:20]

if __name__ == "__main__":
    with open(OUTPUT_FILENAME, "a+") as out:
        for i, keyword in enumerate(IMG_SEARCHES):
            urls = get_img_urls(IMG_QUERY % (keyword,)) 
            out.write("\n".join(urls))
            out.write("\n")
            
            print "Search #%d - %s: urls fetched: %d" % (i, keyword, len(urls))
            
            
            
