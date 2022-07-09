from re import X
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from pystyle import _MakeColors
from time import sleep
import requests
import random
import json
import sys
import os

class Client:
    def __init__(self, username, password, email_phone):
        self.username = username.lower()
        self.password = password
        self.email_phone = email_phone.lower()
        self.delay = 10

        print(_MakeColors._start('53;153;253'))
        self.check_cookies()

    def check_cookies(self):
        print(f'[{self.username}] -- Search for a session...')

        session = str(os.listdir('session')).replace('.txt', '')

        if not self.username in session:
            print(f'[{self.username}] -- Session not found!')
            self.login()
        else:
            print(f'[{self.username}] -- Session found!')
            self.check_auth()

    def check_auth(self):
        print(f'[{self.username}] -- Checks authentication sessions...')

        with open(f'session/{self.username}.txt', 'r', encoding='utf-8') as file:
            file = str(file.read())

            self.csrf_token = file.split()[0]
            self.auth_token = file.split()[1]
            self.guest_token = file.split()[2]

        params = {
            'q': '#NFT',
            'tweet_search_mode': 'live',
            'count': '20',
            'query_source': 'typed_query',
        }

        response = requests.get('https://twitter.com/i/api/2/search/adaptive.json', params=params, headers=self.get_headers())

        if 'globalObjects' in response.text:
            print(f'[{self.username}] -- Authentications verified!')
        elif '"code":326' in response.text:
            print(f'[{self.username}] -- Your account has been suspended!')
            pass
        else:
            print(f'[{self.username}] -- Authentications failed!')
            os.remove(f'session/{self.username}.txt')
            self.login()
    
    def login(self):
        options = ChromeOptions()
        options.add_argument('log-level=3')
        options.add_argument('--disable-logging')
        options.add_argument('--incognito')

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        self.driver.get('https://twitter.com/i/flow/login')

        WebDriverWait(self.driver, self.delay).until(EC.visibility_of_element_located((By.CLASS_NAME, 'r-fdjqy7'))).send_keys(self.username, Keys.ENTER)
        WebDriverWait(self.driver, self.delay).until(EC.visibility_of_element_located((By.CLASS_NAME, 'r-homxoj'))).send_keys(self.password, Keys.ENTER)
    
        try:
            WebDriverWait(self.driver, self.delay).until(EC.visibility_of_element_located((By.CLASS_NAME, 'r-homxoj'))).send_keys(self.email_phone, Keys.ENTER)
        except:
            pass

        sleep(10)
        self.get_cookies_session()
        
    def get_cookies_session(self):
        print(f'[{self.username}] -- Cookie recovery...')
        cookies = str(self.driver.get_cookies())

        self.csrf_token = cookies.split("'ct0', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '")[-1]
        self.csrf_token = self.csrf_token.split("'")[0]

        self.auth_token = cookies.split("'auth_token', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '")[-1]
        self.auth_token = self.auth_token.split("'")[0]

        self.guest_token = cookies.split("'gt', 'path': '/', 'secure': True, 'value': '")[-1]
        self.guest_token = self.guest_token.split("'")[0]

        self.save_cookies_session()

    def save_cookies_session(self):
        with open(f'session/{self.username}.txt', 'w', encoding="utf-8") as file:
            file.write(self.csrf_token + '\n' + self.auth_token + '\n' + self.guest_token)

        self.driver.close()
        print(f'[{self.username}] -- Authentication key saved!')

    def scrape(self, user, cursor, amount, output_path):
        try:
            print('\n' + f'[{self.username}] -- Launching the scrape function!')
            
            # Get account id
            params = {
                'variables': '{"screen_name":"' + user + '","withSafetyModeUserFields":true,"withSuperFollowsUserFields":true}',
            }

            response = requests.get('https://twitter.com/i/api/graphql/mCbpQvZAw6zu_4PvuAUVVQ/UserByScreenName', params=params, headers=self.get_headers())

            with open('utils/response.json', 'w', encoding='utf-8') as file:
                file.write(response.text)

            with open('utils/response.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                user_id = data["data"]["user"]["result"]["rest_id"]

            # First part scrape

            first_cursor = ''
            second_cursor = ''

            params = {
                'variables': '{"userId":"' + user_id + '","count":1,"includePromotedContent":false,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true}',
                'features': '{"dont_mention_me_view_api_enabled":true,"interactive_text_enabled":true,"responsive_web_uc_gql_enabled":false,"vibe_tweet_context_enabled":false,"responsive_web_edit_tweet_api_enabled":false,"standardized_nudges_for_misinfo_nudges_enabled":false}',
            }

            response = requests.get('https://twitter.com/i/api/graphql/31HLi-uxjvX3CnJ4TYAetg/Followers', params=params, headers=self.get_headers())

            with open('utils/response.json', 'w', encoding='utf-8') as file:
                file.write(response.text)

            with open('utils/response.json', 'r', encoding='utf-8') as file:
                data = json.load(file)

                data = str(data).split()[-14]
                data = str(data).replace("'", '').replace(',', '')
                data = str(data).split('|')

                first_cursor = data[0]
                second_cursor = data[1]


            # Second part scrape

            if cursor != '':
                first_cursor = str(cursor).split('|')[0]
                second_cursor = str(cursor).split('|')[1]
                print(first_cursor)
                print(second_cursor)
                
            while True:
                params = {
                    'variables': '{"userId":"' + user_id + '","count":100,"cursor":"' + first_cursor + '|' + second_cursor + '","includePromotedContent":false,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true}',
                    'features': '{"dont_mention_me_view_api_enabled":true,"interactive_text_enabled":true,"responsive_web_uc_gql_enabled":false,"vibe_tweet_context_enabled":false,"responsive_web_edit_tweet_api_enabled":false,"standardized_nudges_for_misinfo_nudges_enabled":false}',
                }

                response = requests.get('https://twitter.com/i/api/graphql/31HLi-uxjvX3CnJ4TYAetg/Followers', params=params, headers=self.get_headers())

                with open('utils/response.json', 'w', encoding='utf-8') as file:
                    file.write(response.text)

                with open('utils/response.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    nb = len(data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"][1]["entries"]) - 2

                    for i in range(nb):
                        read = open(output_path, 'r', encoding='utf-8').read()

                        write = open(output_path, 'w', encoding='utf-8')
                        write.write(read + '@' + data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"][1]["entries"][i]["content"]["itemContent"]["user_results"]["result"]["legacy"]["screen_name"] + '\n')

                    len_users = len(open(output_path, 'r', encoding='utf-8').read().split())
                    if  len_users >= amount:
                        sys.exit(f'{self.username} -- Scrape finished!')

                with open('utils/response.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    data = data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"][1]["entries"][nb]["content"]["value"].split('|')

                    first_cursor = data[0]
                    second_cursor = data[1]

                print(f"[{self.username}] -- Scraped {len_users} users! Cursor: {first_cursor + '|' + second_cursor}")
        except Exception as e:
            print(f'[{self.username}] -- The scrape function can\'t be launch!')
            print(e)
            pass
            
    def mass_mentions(self, id, path):
        self.id = id
        random_tweet = ['You can change this message here ', 'A other message ', 'Check my sellix :) ', 'Website: https://growthhackingtools.sellix.io '] #add here you comment to the tweet
        tweet_content = random.choice(random_tweet)
        acc_del = []
        x = 0
        limit = 0
        with open(path, 'r', encoding='utf-8') as file:
            for user in file.read().split():
                if limit >= 100:
                    break
                
                user = user.replace('@', '')

                if len(str(tweet_content)) <= 255:
                    tweet_content = tweet_content + '@' + user + ' '
                    acc_del.insert(x,user) 
                    x += 1
                else:
                    json_data = {
                        'variables': {
                            'tweet_text': tweet_content,
                            'reply': {
                                'in_reply_to_tweet_id': self.id,
                            'exclude_reply_user_ids': [],
                            },
                            'media': {
                                'media_entities': [],
                                'possibly_sensitive': False,
                            },
                            'withDownvotePerspective': False,
                            'withReactionsMetadata': False,
                            'withReactionsPerspective': False,
                            'withSuperFollowsTweetFields': True,
                            'withSuperFollowsUserFields': True,
                            'semantic_annotation_ids': [],
                            'dark_request': False,
                                            },
                        'features': {
                            'dont_mention_me_view_api_enabled': True,
                            'interactive_text_enabled': True,
                            'responsive_web_uc_gql_enabled': False,
                            'responsive_web_edit_tweet_api_enabled': False,
                        },
                        'queryId': 'D3NDfbMv_TJRFhxryQZrrA',
                    }
                        
                    response = requests.post('https://twitter.com/i/api/graphql/D3NDfbMv_TJRFhxryQZrrA/CreateTweet', headers=self.get_headers(), json=json_data)

                    if not '{"data":{"create_tweet":{"tweet_results":' in str(response.text):
                        print(f'[{self.username}] -- The mass mentions function can\'t be launch!')
                        acc_del.clear()
                        break
                    else:
                        print(f'[{self.username}] -- Mentioning : {tweet_content} with success!\n')
                        i=0
                        while i < len(acc_del):
                            # Read file.txt
                            with open('utils/accounts.txt', 'r') as file:
                                text = file.read()
                                # Delete text and Write
                            with open('utils/accounts.txt', 'w') as file:
                                # Delete
                                new_text = text.replace(acc_del[i], '')
                                # Write
                                file.write(new_text)
                                i+=1
                               

                        acc_del.clear()
                        limit += 1
                        tweet_content = random.choice(random_tweet)

    def get_headers(self):
        headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-csrf-token': f'{self.csrf_token}',
            'cookie': f'auth_token={self.auth_token}; ct0={self.csrf_token};',
            'x-guest-token': f'{self.guest_token}',
        }
        return headers