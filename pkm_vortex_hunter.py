from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from requests import exceptions
from time import sleep
from hunting_info import username, password, search_map
from map_data import map_data


class VortexBot():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.search_list = map_data[f'legend_{search_map}'] + map_data[f'ultra_{search_map}'] + ['Shiny']
        self.searching = True
        self.moving_left = True

    def login(self):
        self.driver.get('https://www.pokemon-vortex.com/login/?action=logout')
        sleep(2)
        user_in = self.driver.find_element_by_xpath('//*[@id="myusername"]')
        passw_in = self.driver.find_element_by_xpath('//*[@id="mypassword"]')
        login_button = self.driver.find_element_by_xpath('//*[@id="submit"]')
        user_in.send_keys(username)
        passw_in.send_keys(password)
        login_button.click()
        self.open_map()

    def open_map(self):
        self.driver.get(f'https://www.pokemon-vortex.com/map/{search_map}')
        sleep(2)
        self.search()

###################################################################################################

    def move_left(self):
        left = self.driver.find_element_by_xpath('//*[@id="arrows"]/table/tbody/tr[2]/td[1]/img')
        if left.get_attribute('class') != 'activeArrow':
            self.moving_left = False
        else:
            left.click()

    def move_right(self):
        right_arw = self.driver.find_element_by_xpath('//*[@id="arrows"]/table/tbody/tr[2]/td[3]/img')
        if right_arw.get_attribute('class') != 'activeArrow':
            self.moving_left = True
        else:
            right_arw.click()

    def search(self):
        print('Searching... ')
        while self.searching:
            try:
                if self.moving_left:
                    self.move_left()
                else:
                    self.move_right()
                self.get_search_status()

            except ElementClickInterceptedException:
                print('Looks like the arrow keys are blocked. Trying again in 3 seconds...')
                sleep(3)

            except exceptions.ConnectionError:
                self.searching = False
                print('Connection lost. Retrying in 5 seconds...')
                sleep(5)
                self.searching = True
                self.open_map()

            except KeyboardInterrupt:
                self.searching = False
                logout = self.driver.find_element_by_xpath('//*[@id="logout"]')
                logout.click()

            except Exception:
                self.searching = False
                print('Uh oh, something went wrong')
                exp_input = input('To resume hunting, type RESUME ')
                if exp_input == 'RESUME':
                    self.searching = True
                    self.open_map()
                try:
                    logout = self.driver.find_element_by_xpath('//*[@id="logout"]')
                    logout.click()
                except NoSuchElementException:
                    pass
       
        self.driver.quit()

###################################################################################################

    def get_search_status(self): #change this orders: wild, no, research
        pkm_appeared = self.driver.find_element_by_xpath('//*[@id="pkmnappear"]').text
        if pkm_appeared.startswith('No'):  #No wild Pokémon appeared\nKeep moving around to find one.
            return
        elif pkm_appeared.startswith('Search'):    #Searching for Pokémon...\nPlease wait...
            sleep(0.4)
            self.get_search_status()
        else:
            self.check_pokemon()

    def check_pokemon(self):
        desired_pkm = False
        pkm_found = self.driver.find_element_by_xpath('//*[@id="pkmnappear"]/form/center/p').text
        pkm_found = ' '.join(pkm_found.split()[1:-1])
        if "Cell" in pkm_found: #Ignore Zygarde Cell
            return
        for search_item in self.search_list:
            if search_item in pkm_found:
                desired_pkm = True
                break
        if desired_pkm:
            check_skip = input(f'Pokemon [{pkm_found}] {self.check_duplicate()}was found, type SKIP to skip this pokemon ')
            if check_skip == 'SKIP':
                print('Searching...')
                return
            while True:
                battle_finished = input('Type CONTINUE to continue hunting ')
                if battle_finished == 'CONTINUE':
                    break
            self.open_map()
        
    def check_duplicate(self):
        try:
            self.driver.find_element_by_xpath('//*[@id="pkmnappear"]/form/center/p/img')
            return '(duplicate) '
        except NoSuchElementException:
            return ''

###################################################################################################

hunter = VortexBot()
hunter.login()