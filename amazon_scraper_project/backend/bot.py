# bot.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def amazon_main(
    pincodes,
    asin_list,
    host_url,
    output_filename,
    city_map,
    getCompetitorFlag,
    getProductTitleFlag,
    includePrice=True,
    includeSellerCount=True
):
    """
    Main scraping function for Amazon data.
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for pincode in pincodes:
            city = city_map.get(pincode, "Unknown")
            for asin in asin_list:
                try:
                    url = f"{host_url}{asin}"
                    driver.get(url)
                    time.sleep(3)

                    try:
                        pin_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
                        pin_input.clear()
                        pin_input.send_keys(pincode)
                        driver.find_element(By.CSS_SELECTOR, "#GLUXZipUpdate .a-button-input").click()
                        time.sleep(3)
                    except Exception:
                        pass

                    try:
                        buy_box_flag = driver.find_element(By.ID, "priceblock_ourprice").text
                    except:
                        buy_box_flag = "N/A"

                    try:
                        seller = driver.find_element(By.ID, "merchant-info").text
                    except:
                        seller = "N/A"

                    if includePrice:
                        try:
                            price = driver.find_element(By.ID, "priceblock_dealprice").text
                        except:
                            price = "N/A"
                    else:
                        price = None

                    try:
                        coupon_text = driver.find_element(By.CSS_SELECTOR, ".couponBadge").text
                    except:
                        coupon_text = "N/A"

                    free_delivery = "Yes"  # Placeholder
                    fastest_delivery = "2 days"  # Placeholder

                    if includeSellerCount:
                        seller_count = "N/A"  # Placeholder
                    else:
                        seller_count = None

                    minimum_price = price if price else "N/A"

                    product_title = ""
                    if getProductTitleFlag:
                        try:
                            product_title = driver.find_element(By.ID, "productTitle").text.strip()
                        except:
                            product_title = "N/A"

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                    # Build row dynamically based on flags
                    row = [asin, buy_box_flag, timestamp, pincode, city, seller]
                    if includePrice:
                        row.append(price)
                    row.append(coupon_text)
                    row.append(free_delivery)
                    row.append(fastest_delivery)
                    if includeSellerCount:
                        row.append(seller_count)
                    row.append(minimum_price)
                    if getProductTitleFlag:
                        row.append(product_title)

                    writer.writerow(row)

                    print(f"Scraped ASIN {asin} for pincode {pincode}")

                except Exception as e:
                    print(f"Error scraping ASIN {asin} for pincode {pincode}: {e}")

    driver.quit()

