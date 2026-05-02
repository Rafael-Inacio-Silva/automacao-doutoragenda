from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def iniciar_chrome():
    options = Options()
    options.add_argument("--headless=new")  # modo invisível moderno
    options.add_argument("--start-maximized")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    driver = webdriver.Chrome(options=options)
    return driver