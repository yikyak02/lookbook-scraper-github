from flask import Flask, request
from flask_restful import Resource, Api
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os



app = Flask(__name__)
api = Api(app)

def get_images_from_google(search_query, num_images):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_driver_path = './chromedriver/chromedriver'
    
    
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

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
    driver.quit()
    return list(urls)


class Scrape(Resource):
    def get(self):
        query = request.args.get('query')
        if not query:
            return {'error': 'Missing query parameter'}, 400

        try:
            image_urls = get_images_from_google(query, 2)
            return image_urls
        except Exception as e:
            print(f"Error: {e}")
            return {'error': 'Internal Server Error'}, 500

api.add_resource(Scrape, '/scrape')

if __name__ == '__main__':
    app.run(debug=True)
