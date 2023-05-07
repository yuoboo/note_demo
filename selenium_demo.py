import time
from selenium import webdriver

"""
下载webdriver
http://chromedriver.storage.googleapis.com/index.html
http://www.manongjc.com/detail/53-cstfaycwxqewtiz.html

cd /usr/local/share
wget -N http://chromedriver.storage.googleapis.com/2.26/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver
ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
ln -s /usr/local/share/chromedriver /usr/bin/chromedriver
"""
options = webdriver.ChromeOptions()
options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--screenshot')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.get("http://www.baidu.com")
driver.set_window_size(1920, 1080)
# driver.fullscreen_window()
file_name = int(time.time())
driver.get_screenshot_as_file(f"./images/{file_name}.png")

driver.close()



# phantomjs
"""
https://phantomjs.org/download.html
https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-macosx.zip

https://codeantenna.com/a/ySpQ822AUy
"""
#
# brower = webdriver.WebKitGTK(executable_path="/usr/local/bin/phantomjs")
# brower.get("http://phantomjs.org/download.html")
# brower.maximize_window()
# brower.viewportSize={'width':1024,'height':800}
# file_name = int(time.time())
# brower.save_screenshot(f"./images/ph/{file_name}.png")
# brower.quit()
# from phantomjs import Phantom
# phantom = Phantom()
# conf = {
#     'url': 'http://baidu.com/',   # Mandatory field
# }
# out = phantom.download_page(conf, load_images=True)
# print(out)
