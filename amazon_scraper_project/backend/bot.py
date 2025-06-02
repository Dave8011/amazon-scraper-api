# bot.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def amazon_main(pincodes, asin_list, host_url, output_filename, city_map, getCompetitorFlag, getProductTitleFlag):
    """
    Main scraping function for Amazon data.

    Args:
        pincodes (list): List of pincodes to scrape data for.
        asin_list (list): List of ASINs (Amazon product IDs).
        host_url (str): Base URL for Amazon product pages.
        output_filename (str): File path to write the scraped CSV.
        city_map (dict): Mapping from pincodes to city names.
        getCompetitorFlag (bool): Whether to get competitor data.
        getProductTitleFlag (bool): Whether to get product title.
    """

    # Setup Chrome options for headless scraping
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Iterate over pincodes and ASINs
        for pincode in pincodes:
            city = city_map.get(pincode, "Unknown")
            for asin in asin_list:
                try:
                    url = f"{host_url}{asin}"
                    driver.get(url)
                    time.sleep(3)  # wait for page to load

                    # Example: Set delivery pincode on Amazon page (if required)
                    # You might need to adjust selectors here based on Amazon's page changes
                    try:
                        pin_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
                        pin_input.clear()
                        pin_input.send_keys(pincode)
                        driver.find_element(By.CSS_SELECTOR, "#GLUXZipUpdate .a-button-input").click()
                        time.sleep(3)
                    except Exception:
                        pass  # If pincode input not found, ignore

                    # Scrape the Buy Box flag (example)
                    try:
                        buy_box_flag = driver.find_element(By.ID, "priceblock_ourprice").text
                    except:
                        buy_box_flag = "N/A"

                    # Scrape seller info
                    try:
                        seller = driver.find_element(By.ID, "merchant-info").text
                    except:
                        seller = "N/A"

                    # Scrape price
                    try:
                        price = driver.find_element(By.ID, "priceblock_dealprice").text
                    except:
                        price = "N/A"

                    # Scrape coupon text (example)
                    try:
                        coupon_text = driver.find_element(By.CSS_SELECTOR, ".couponBadge").text
                    except:
                        coupon_text = "N/A"

                    # Free delivery info - Example placeholder
                    free_delivery = "Yes"  # you can parse actual info here

                    # Fastest delivery info - Example placeholder
                    fastest_delivery = "2 days"

                    # Seller count - Example placeholder
                    seller_count = "N/A"  # needs actual logic to scrape

                    # Minimum price - Example placeholder
                    minimum_price = price

                    # Product title (if requested)
                    product_title = ""
                    if getProductTitleFlag:
                        try:
                            product_title = driver.find_element(By.ID, "productTitle").text.strip()
                        except:
                            product_title = "N/A"

                    # Timestamp
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                    # Write the row based on flag
                    if getProductTitleFlag:
                        writer.writerow([asin, buy_box_flag, timestamp, pincode, city, seller, price, coupon_text, free_delivery, fastest_delivery, seller_count, minimum_price, product_title])
                    else:
                        writer.writerow([asin, buy_box_flag, timestamp, pincode, city, seller, price, coupon_text, free_delivery, fastest_delivery, seller_count, minimum_price])

                    print(f"Scraped ASIN {asin} for pincode {pincode}")

                except Exception as e:
                    print(f"Error scraping ASIN {asin} for pincode {pincode}: {e}")

    driver.quit()
