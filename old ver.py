from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import io
from PIL import Image

def get_images_from_google(driver, search_query, num_images):
    # Navigate to Google Images
    driver.get("https://images.google.com/")
    
    # Find the search box and input the search query
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.submit()

    # Wait for thumbnails to be loaded
    wait = WebDriverWait(driver, 20)
    try:
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
                # Re-fetch the thumbnail
                thumbnail = thumbnails[i]

                # Scroll to the element and ensure it's in the viewport
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumbnail)

                # Wait for the element to be clickable
                wait.until(EC.element_to_be_clickable(thumbnail))

                # Attempt to click the thumbnail using JavaScript
                driver.execute_script("arguments[0].click();", thumbnail)

                # Wait for the full image to load
                full_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.sFlh5c.pT0Scc.iPVvYb")))

                # Get the URL of the image
                src = full_image.get_attribute("src")
                if src and "http" in src:
                    if src not in urls:
                        urls.add(src)
                        num_collected += 1

                # Click outside to close the preview
                driver.find_element(By.TAG_NAME, "body").click()

                # Refresh thumbnails
                thumbnails = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "YQ4gaf")))

            except Exception as e:
                print(f"Error clicking thumbnail: {e}")
                continue

    return list(urls)

# Example usage:
if __name__ == "__main__":
    driver = webdriver.Chrome()
    try:
        urls = get_images_from_google(driver, "nike shirt", 5)
        for url in urls:
            print(url)
    finally:
        driver.quit()

def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = download_path + file_name

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")
            
        print("Success")
    except Exception as e:
        print('Failed -', e)