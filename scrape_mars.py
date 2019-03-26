#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Dependencies
import requests
from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import datetime as dt


def mars_news(browser):
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Get first list item and wait half a second
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=0.5)

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    soup = bs(html, 'html.parser')

    try:
        # get titles
        slide_element = soup.select_one('ul.item_list li.slide')
        slide_element.find('div', class_ = 'content_title')

        # get title text
        title = slide_element.find('div', class_ = 'content_title').get_text()
    
        # get paragraph text
        paragraph = slide_element.find('div', class_ = 'article_teaser_body').get_text()

    except AttributeError:
        return None, None    
    return title, paragraph
    
def mars_images(browser):
    # Visit URL on JPL site
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url2)

    # Splinter hits button of full_image class
    full_image_button = browser.find_by_id('full_image')
    full_image_button.click()

    # Find the 'more info" button' and click
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_element = browser.find_link_by_partial_text('more info')
    more_info_element.click()

    # Parse results html with soup
    html = browser.html
    image_soup = bs(html, 'html.parser')

    img = image_soup.select_one('figure.lede a img')
    # Get image URL
    img_url = image_soup.select_one('figure.lede a img')

    try:
        img_url = img.get('src')
    except AttributeError:
        return None

    # Use base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url}'
    return img_url



def twitter_weather(browser):
    # URL of page to be scraped
    url3 = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url3)

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    soup2 = bs(html, 'html.parser')

    mars_weather_tweet = soup2.find('div', attrs={'class': 'tweet', 'data-name': 'Mars Weather'})

    # Search w/in the tweet for p tag containnig the tweet text
    mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
    return mars_weather


def hemispheres(browser):
    # URL of page to be scraped
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    hemisphere_image_urls = []

    # First get a list of hemispheres
    links = browser.find_by_css('a.product-item h3')
    for item in range(len(links)):
        hemisphere = {}
        
        # Find the element on each loop
        browser.find_by_css('a.product-item h3')[item].click()
        
        # Find the sample image anchor tag and extraxt the href
        sample_element = browser.find_link_by_text('Sample').first
        hemisphere['img_url'] = sample_element['href']
        
        # Get hemisphere title
        hemisphere['title'] = browser.find_by_css('h2.title').text
        
        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere)
        
        # Navigate back
        browser.back()
    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    hemisphere_soup = bs(html_text, 'html.parser')

    try:
        title_element = hemisphere_soup.find('h2', class_="title").get_text()
        sample_element = hemisphere_soup.find('a', text="Sample").get('href')
    except AttributeError:
        title_element = None
        sample_element = None
    hemisphere = {
        "title" : title_element,
        "sample" : sample_element
    }
    return hemisphere


def mars_facts():
    try:
        df = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None

    df.columns = ['Obervation Type', 'Recorded Measure']
    df.set_index('Obervation Type', inplace=True)

    return df.to_html(classes="table tabe-striped")


# create function
def scrape_all():

    # Use splinter to scrape
    executable_path = {'executable_path': './chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    title, paragraph = mars_news(browser)
    img_url = mars_images(browser)
    mars_weather = twitter_weather(browser)
    hemisphere_image_urls = hemispheres(browser)
    facts = mars_facts()
    timestamp = dt.datetime.now()

    data = {
        "title": title,
        "paragraph": paragraph,
        "featured image": img_url,
        "weather": mars_weather,
        "hemispheres": hemisphere_image_urls,
        "facts": facts,
        "last_modified": timestamp
    }

    browser.quit()
    return data

if __name__ == "__main__":
    print(scrape_all())

