import time
import numpy as np
import uuid
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Set Headers and Context Options
headers = {'Accept-Encoding': 'gzip, deflate, sdch',
           'Accept-Language': 'en-US,en;q=0.8',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive'}

# Create Scrapper object
class TokpedScrapper:
    def __init__(self, data_id:uuid):
        self.logger = logging.getLogger(__name__)
        self.data_id = data_id
    
    def create_firefox_session(self):
        """
        Create new firefox instance using Selenium
        """
        self.logger.info('Create new firefox session')

        # Define firefox setting
        firefox_options = Options()
        for key, value in headers.items():
            firefox_options.set_preference("network.http.header.override." + key, value)
        # Add headless option
        firefox_options.add_argument("--headless")

        # Define driver
        self.driver = webdriver.Firefox(options = firefox_options)

        # Maximize window
        self.driver.maximize_window()
    
    def scroll_page(self, max_scroll:int=5):
        self.logger.info(f'Scroll page {max_scroll} times')

        # You can set your own pause time. My laptop is a bit slow so I use 1 sec
        scroll_pause_time = 1
        screen_height = self.driver.execute_script("return window.screen.height;")   # get the screen height of the web
        i = 1.0

        # See maximum limit scrolling to 5
        while True:
            # scroll one screen height each time
            executed = False
            while executed == False:
                try:
                    self.driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
                    i += 1.0
                    time.sleep(scroll_pause_time)
                    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
                    scroll_height = self.driver.execute_script("return document.body.scrollHeight;")  
                    executed = True
                except:
                    time.sleep(0.5)
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            if (screen_height) * i > scroll_height or i > max_scroll:
                break
    
    def get_post_link(self, url:str):
        """
        Get all post link from given official account URL
        """
        self.logger.info(f'Get video post link from {url}')

        # Go to the url
        self.driver.get(url)

        # Add time sleep, to let the web refresh
        time.sleep(2)

        # Scroll page
        self.scroll_page(10)

        # Get video post
        video_post_links = self.driver.find_elements(by = By.XPATH, value = "/html/body/div[1]/div/div[2]/div[2]/div[4]/div/div[2]/div[1]/div/div/div/div/div/div/div[1]/a")

        # Do preprocessing
        video_post_links = [html.get_attribute('href') for html in video_post_links]

        # Return video_post_links
        return video_post_links

    def get_data_metadata(self, post_url:str):
        self.logger.info(f'Get data metadata from {post_url}')

        # Get URL
        self.driver.get(post_url)

        # Add sleep time to refresh web
        time.sleep(3)

        # Scroll web
        self.scroll_page(10)

        # Get Item Name
        item_name = self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div[4]/div/h1').text
        sold_count = self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div[4]/div/div[1]/div/p[1]').text
        rating = self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div[4]/div/div[1]/div/p[2]/span[1]/span[2]').text

        # Scroll web
        description = ''
        try:
            button_readmore = self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/div/button')
            button_readmore.click()
            description += self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/ul').get_attribute('innerText') + '\n\nDETAIL:\n'
            description += self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/div/span/span/div').get_attribute('innerText')
        except:
            description += self.driver.find_element(by = By.XPATH, value = '//*[@id="pdp_comp-product_detail"]/div[2]/div[2]').get_attribute('innerText')
            description += self.driver.find_element(by = By.XPATH, value = '//*[@id="pdp_comp-product_detail"]/div[2]/div[2]/div/span/span/div').get_attribute('innerText')

        self.driver.execute_script("window.scrollTo(0, 200);")
        specification = ''
        try:
            more_info_button = self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div/button[3]')
            more_info_button.click()
            specification_list = self.driver.find_elements(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/ul/li/button')
            if len(specification_list) > 0:
                for button in specification_list:
                    button.click()
                    time.sleep(2)
                    specification += self.driver.find_element(by = By.XPATH, value = '//*[@id="tab-note-panel"]').get_attribute('innerText') + '\n'
                    specification += self.driver.find_element(by = By.XPATH, value = '/html/body/div/div[2]/article/div/div/div/div[2]/div[2]').get_attribute('innerText')
                    close_button = self.driver.find_element(by = By.XPATH, value = '/html/body/div/div[2]/article/header/button')
                    close_button.click()
                    time.sleep(2)
        except Exception as e:
            print(e)

        # Get total stocks
        total_stocks = self.driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div[2]/div[2]/div[3]/div/div/div[1]/p').get_attribute('innerText')
        self.post_id = str(uuid.uuid4())

        data_metadata = {
            'pid': self.post_id,
            'URL': post_url,
            'Item Name': item_name,
            'Description': description,
            'Specification': specification,
            'Total Stock': total_stocks,
            'Quantity Sold': sold_count,
            'Rating': rating
        }

        return data_metadata

    def get_qna_metadata(self, max_qna_page:int=3):
        self.logger.info(f'Get QnA metadata for {max_qna_page} pages')

        # Create empty list to store the values for each item
        item_id_list = []
        qna_id_list = []
        question_list = []
        user_q_list = []
        answer_list = []
        user_a_list = []

        for i in range(max_qna_page):
            # Get QnA box
            qna_box = self.driver.find_element(by = By.XPATH, value = '//*[@id="pdp_comp-discussion_faq"]/div')

            # Get questions
            article_list = qna_box.find_elements(by = By.XPATH, value = 'div/section/article')

            # Find expand buttons
            button_lists = qna_box.find_elements(by = By.XPATH, value = 'div/section/article/div[2]/div/ul/button')
            for button in button_lists:
                try:
                    button.click()
                except Exception as e:
                    continue
            for i, article in enumerate(article_list):
                qna_id = str(uuid.uuid4())
                question = article.find_element(by = By.XPATH, value = 'div[1]/div/div[1]/div/p').text
                user_q = article.find_element(by = By.XPATH, value = 'div[1]/div/div[1]/div/div/a').text
                try:
                    reply_box = article.find_element(by = By.XPATH, value = 'div[2]/div/ul/li[1]/div/div[1]/div')
                    if article.find_element(by = By.XPATH, value = 'div[2]/div/ul/li[1]/div/div[1]/div/div/div').text == 'Penjual':
                        answer = reply_box.find_element(by = By.XPATH, value = 'p/span').text
                        user_a = reply_box.find_element(by = By.XPATH, value = 'div/a').text
                except Exception as e:
                    continue
                item_id_list.append(self.post_id)
                qna_id_list.append(qna_id)
                question_list.append(question)
                user_q_list.append(user_q)
                answer_list.append(answer)
                user_a_list.append(user_a)
            
            # Click next button
            # /html/body/div[1]/div/div[2]/div[2]/div[15]/div/div/section/div/nav/ul/li[10]/button
            try:
                self.driver.find_elements(by = By.XPATH, value = "/html/body/div[1]/div/div[2]/div[2]/div[15]/div/div/section/div/nav/ul/li/button")[-1].click()

                # Add sleep time to refresh page
                time.sleep(2)
            except:
                break
        
        # Create dict_qna
        qna_metadata = {
            'ID': qna_id_list,
            'Item ID': item_id_list,
            'User Question': user_q_list,
            'Question': question_list,
            'User Answer': user_a_list,
            'Answer': answer_list
        }
        
        return qna_metadata
    
    def quit_session(self):
        self.logger.info("Quit Firefox session")
        self.driver.quit()