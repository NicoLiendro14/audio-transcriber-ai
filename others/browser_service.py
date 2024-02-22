import os
import time

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class BrowserService:
    def __init__(self):
        profile_directory = r'C:\Users\Nicolas\Desktop\UpWork Projects\interviewer_helper\data_chrome'
        os.makedirs(profile_directory, exist_ok=True)
        chrome_options = Options()
        chrome_options.add_argument(f'--user-data-dir={profile_directory}')
        self.driver = uc.Chrome(options=chrome_options)
        url = 'https://chat.openai.com/'
        self.driver.get(url)

    def send_response(self, prompt):
        # Función para verificar si el elemento existe y tiene el texto deseado
        def check_element_text(driver):
            try:
                element = driver.find_element(By.XPATH,
                                              "/html/body/div[1]/div[2]/div[2]/div/main/div[3]/form/div/div[1]/div/button")
                if element.text == "Regenerate response":
                    return True
                else:
                    return False
            except:
                return False
        input_prompt = self.driver.find_element(By.ID, 'prompt-textarea')
        input_prompt.send_keys(prompt)
        input_prompt.submit()


        # Esperar hasta que el elemento exista y tenga el texto deseado
        wait = WebDriverWait(self.driver, 50)
        wait.until(check_element_text)

        # Continuar chequeando hasta que el texto sea igual a "Regenerate response"
        while not check_element_text(self.driver):
            time.sleep(1)

        list_messages = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/main/div[2]/div/div/div")
        last_message_chatgpt = list_messages.find_elements(By.XPATH, '*')[-2].text.split("ChatGPTChatGPT1 / 1")
        return last_message_chatgpt[0]

    def quit(self):
        self.driver.quit()
