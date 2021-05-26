from pyquery import PyQuery
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 銘柄名
def get_company_name(sc):

    url = 'https://kabutan.jp/stock/?code=' + str(sc)
    q = PyQuery(url)
    name = q.find('div.company_block > h3').text()

    return name

# マーケット名
def get_market_name(sc):

    url = 'https://kabutan.jp/stock/?code=' + str(sc)
    q = PyQuery(url)
    name = q.find('span.market').text()

    return name

# 株価情報
def get_stock_info(sc):

    options = Options()
    options.add_argument('--headless')

    url = 'https://jp.kabumap.com/servlets/kabumap/Action?SRC=basic/top/base&codetext=' + str(sc)
    driver_path = "C:/Users/es/webdriver/chrome/chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)
    
    oprice = driver.find_element_by_css_selector('#oprice').text
    high = driver.find_element_by_css_selector('#high').text
    low = driver.find_element_by_css_selector('#low').text
    yearHigh = driver.find_element_by_css_selector('#yearHigh').text
    yearLow = driver.find_element_by_css_selector('#yearLow').text
    volume = driver.find_element_by_css_selector('#volume').text
    minUnit = driver.find_element_by_css_selector('#minUnit').text
    avgTrade = driver.find_element_by_css_selector('#avgTrade').text
    mcap = driver.find_element_by_css_selector('#mcap').text
    per = driver.find_element_by_css_selector('#per').text
    pbr = driver.find_element_by_css_selector('#pbr').text
    yeld = driver.find_element_by_css_selector('#yield').text
    
    return oprice, high,low,yearHigh,yearLow,volume,minUnit,avgTrade,mcap,per,pbr,yeld 
    
