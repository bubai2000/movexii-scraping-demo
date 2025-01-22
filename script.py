from selenium import webdriver
from requests import get
from json import loads
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pandas import DataFrame

options = Options()
options.add_argument("--headless")  # Run in headless mode (no GUI)
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.set_capability("goog:loggingPrefs", {
    'performance': 'ALL',
}) #Required to scan APIs
driver = webdriver.Chrome(options=options)

# Inintializing export variable
export = []

#navigating to page
driver.get("https://www.movexii.com/en/p/815-split-machined-sprocketm")

#Waiting for details table to load
table = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "table_combinazioni")))

#Extracting data from table
table_body = table.find_element(By.TAG_NAME, "tbody")
rows = table_body.find_elements(By.TAG_NAME, "tr")
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    export.append([cell.text for cell in cells])

#Building JSON
df = DataFrame(export, columns=[cell.text for cell in table.find_element(
    By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")])
df.set_index("Product code", inplace=True)
df.to_json("export_data.json", orient="index")

#Finding images
image_base_url = "https://www.movexii.com/_next/image"
image_url_list = []
logs = driver.get_log('performance')
for log in logs:
    log_entry = loads(log['message'])["message"]
    if 'Network.response' in log_entry['method']:
        current_url = log_entry.get('params').get(
            'response', {}).get('url', None)
        if current_url and image_base_url in current_url:
            image_url_list.append(current_url)

#Saving images
for image_url in image_url_list:
    response = get(image_url)
    with open(response.headers['content-disposition'].split('=')[1].replace('"', ''), "wb") as f:
        f.write(response.content)

#Closing chrome
driver.quit()