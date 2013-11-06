"""
Get the image urls from a google image page.
"""

import requests, re

RE_URL = re.compile(r'src="(https.*?)"')

OUTPUT_FILENAME = "docs/create_store/image_urls.txt"
IMG_SEARCHES = (
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=products&tbm=isch",
    "https://www.google.com/search?q=cars&source=lnms&tbm=isch&sa=X&ei=MWZ6UsbpLuLJsQT8-IC4Bg&ved=0CAcQ_AUoAQ&biw=1366&bih=679",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=guns&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=fitness&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=electronics&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=toys&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=foods&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=games&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=books&tbm=isch",
    "https://www.google.com/search?q=fruits&biw=1366&bih=679&source=lnms&tbm=isch&sa=X&ei=aWl6UofbC5DKsQS644HoAg&ved=0CAcQ_AUoAQ#q=sports&tbm=isch",
)

def get_img_urls(url):
    r = requests.get(url)
    return "\n".join(RE_URL.findall(r.content))

if __name__ == "__main__":
    with open(OUTPUT_FILENAME, "a+") as out:
        for url in IMG_SEARCHES:
            out.write(get_img_urls(url))
            out.write("\n")
