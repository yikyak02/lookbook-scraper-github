from flask import Flask, request
from flask_restful import Resource, Api
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from PIL import Image

app = Flask(__name__)
api = Api(app)

def get_images_from_google(driver, search_query, num_images):
    driver.get("https://images.google.com/")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.submit()

    wait = WebDriverWait(driver, 1)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "s6JM6d")))
        driver.execute_script("""
            var relatedSearches = document.querySelector('.IUOThf');
            if (relatedSearches) {
                relatedSearches.style.display = 'none';
            }
        """)
        thumbnails = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "YQ4gaf")))
    except Exception as e:
        print(f"Error locating thumbnails: {e}")
        driver.save_screenshot('thumbnail_error.png')
        return []

    urls = set()
    num_collected = 0

    while num_collected < num_images:
        for i in range(len(thumbnails)):
            if num_collected >= num_images:
                break
            try:
                thumbnail = thumbnails[i]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumbnail)
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable(thumbnail))
                thumbnail.click()
                full_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.sFlh5c.pT0Scc.iPVvYb")))
                src = full_image.get_attribute("src")
                if src and "http" in src:
                    if src not in urls:
                        urls.add(src)
                        num_collected += 1
                driver.find_element(By.TAG_NAME, "body").click()
                thumbnails = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "YQ4gaf")))
            except Exception as e:
                print(f"Error clicking thumbnail: {e}")
                continue
    return list(urls)

class Scrape(Resource):
    def get(self):
        query = request.args.get('query')
        if not query:
            return {'error': 'Missing query parameter'}, 400

        driver = webdriver.Chrome()
        try:
            image_urls = get_images_from_google(driver, query, 6)
            return image_urls
        finally:
            driver.quit()

api.add_resource(Scrape, '/scrape')

if __name__ == '__main__':
    app.run(debug=True)
