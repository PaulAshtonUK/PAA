from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

# 1. Open weekly list search page (CORRECT URL)
driver.get(
    "https://pa.manchester.gov.uk/online-applications/search.do?action=weeklyList&searchType=Application"
)

# 2. Select week
week_select = wait.until(EC.presence_of_element_located((By.ID, "week")))
for option in week_select.find_elements(By.TAG_NAME, "option"):
    if option.text.strip() == "15 Dec 2025":
        option.click()
        break

# 3. Click Search
driver.find_element(By.ID, "searchButton").click()

# 4. Wait for results table
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "searchresults")))

# 5. Collect application links
links = []
for a in driver.find_elements(By.CSS_SELECTOR, "a[href*='applicationDetails.do']"):
    links.append(a.get_attribute("href"))

links = list(set(links))
print(f"[info] Found {len(links)} applications")

results = []

# 6. Visit each application
for url in links:
    driver.get(url)

    # Click "Further Information"
    wait.until(EC.element_to_be_clickable((By.ID, "subtab_details"))).click()

    # Wait for table
    table = wait.until(EC.presence_of_element_located((By.ID, "simpleDetailsTable")))

    record = {"URL": url}

    for row in table.find_elements(By.TAG_NAME, "tr"):
        key = row.find_element(By.TAG_NAME, "th").text.strip()
        value = row.find_element(By.TAG_NAME, "td").text.strip()
        record[key] = value

    results.append(record)
    print(f"[info] Scraped {record.get('Reference')}")

# 7. Save CSV
with open("manchester_planning.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

driver.quit()
