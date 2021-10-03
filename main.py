from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import datetime
import re
import time
import requests
import html
import json
import pandas as pd
import sys


class UsernameFile:
    def __init__(self, location):
        self.location = location
        self.df = pd.read_excel(self.location,
                                sheet_name="Sheet1",
                                engine="openpyxl")
        self.url_list = self.df_to_list()
        self.size = len(self.url_list)

    def df_to_list(self):
        urllist = []
        for i in self.df['username']:
            urllist.append(i)
        return urllist


class URLList(UsernameFile):
    def __init__(self, account_url_location, number_of_posts, timing_coefficient, do_filter_keywords):
        super(URLList, self).__init__(account_url_location)

        self.mainlog = EventLog()

        chrome_options = Options()
        chrome_options.add_argument("--window-size=800,900")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        self.ig_url = "https://www.instagram.com/"

        # im not putting my instagram credentials in github
        self.ig_username = "test_jm_rcts"
        self.ig_password = "testingeksternal"

        self.number_of_posts = number_of_posts
        self.do_filter_keywords = do_filter_keywords

        if timing_coefficient is None:
            self.timing_coefficient = 1
        else:
            self.timing_coefficient = timing_coefficient

        self.driver.get(self.ig_url)
        time.sleep(self.timing_coefficient * 3)
        username = self.driver.find_element_by_css_selector("input[name='username']")
        password = self.driver.find_element_by_css_selector("input[name='password']")
        username.clear()
        password.clear()
        username.send_keys(self.ig_username)
        password.send_keys(self.ig_password)
        print("Login")
        self.driver.find_element_by_css_selector("button[type='submit']").click()
        time.sleep(self.timing_coefficient * 2.7)
        print("Clicked Login Button")
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
        time.sleep(self.timing_coefficient * 2.7)
        print("Clicked Not Now")
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
        print("Clicked Not Now")

        self.account_list = UsernameFile(account_url_location)
        self.posts_url = self.get_post_url_list()

        time.sleep(0.2 * self.timing_coefficient)
        self.driver.close()

    def get_account_posts(self, current_username):
        main_posts = []
        if self.number_of_posts > 10:
            print("Number of posts must not exceed 10!")
            self.number_of_posts = int(input("Number of posts: "))
        searchbox = self.driver.find_element_by_css_selector("input[placeholder='Search']")
        searchbox.clear()

        searchbox.send_keys(current_username)
        time.sleep(self.timing_coefficient * 2)

        searchbox.send_keys(Keys.ENTER)
        time.sleep(self.timing_coefficient * 2)

        searchbox.send_keys(Keys.ENTER)
        time.sleep(self.timing_coefficient * 3)

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                                   "var lenOfPage=document.body.scrollHeight;"
                                   "return lenOfPage;")

        links = self.driver.find_elements_by_tag_name('a')
        post_count = 0
        print(current_username)
        for link in links:
            post_url_raw = link.get_attribute('href')
            if '/p/' in post_url_raw:
                main_posts.append(post_url_raw)
                json_url = post_url_raw + "?__a=1"
                post_count += 1
                print(f"{post_count}. {post_url_raw}")
                current_post = InstagramData(json_url)
                self.mainlog.add_event(new_url=current_post.output_url,
                                       new_username=current_post.output_username,
                                       new_postdate=current_post.output_post_date,
                                       new_caption=current_post.output_caption)

                if post_count == self.number_of_posts:
                    break

        time.sleep(self.timing_coefficient * 1)
        return main_posts

    def get_post_url_list(self):
        sum_posts = []
        for account_username in self.account_list.url_list:
            current_acquisition = self.get_account_posts(account_username)
            for post_url in current_acquisition:
                sum_posts.append(post_url)
        if self.do_filter_keywords:
            self.mainlog.to_excel(self.do_filter_keywords)
        else:
            self.mainlog.to_excel(self.do_filter_keywords)
        return sum_posts


class InstagramData:
    def __init__(self, url):
        self.added_text = "?__a=1"
        self.months = ["January", "February", "March",
                       "April", "May", "June",
                       "July", "August", "September",
                       "October", "November", "December"]

        self.post_url = url

        self.header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                     "AppleWebKit/537.36 (KHTML, like Gecko)"
                                     "Chrome/94.0.4606.54 Safari/537.36",
                       "cookie": "ig_did=EEC95D6A-0846-47F2-8B87-53F3B64A6007;"
                                 "ig_nrcb=1; mid=YT7mCwALAAEdoraS5_1uT4cn27bC;"
                                 "ds_user_id=49129421296;"
                                 "csrftoken=jmtrjBYiSK1vA1tMSZtYpZoWK1kJfa8j;"
                                 "sessionid=49129421296:IuiCKTr3UjQcGo:15;"
                                 "rur='VLL\05449129421296\0541663920099:"
                                 "01f72808aa326e662dbb067009bf1016c2aab88820d952e098afce519878fc54f21cecc8'"}

        self.request_text = requests.get(self.post_url, headers=self.header)
        self.statuscode = self.request_text.status_code
        self.current_header = self.request_text.headers

        self.html_data = html.unescape(self.request_text.text)
        self.output_url = self.post_url
        self.raw_data = self.get_data()

        self.output_username = self.raw_data[0]
        self.output_post_date = self.raw_data[1]
        self.output_caption = self.raw_data[2]

    def get_data(self):
        data_head = self.html_data[:9]

        username = "failed to acquire"
        caption = "failed to acquire"
        post_date = "(date not found)"

        if data_head == '{"graphql':
            json_data = json.loads(self.html_data)
            body = json_data["graphql"]["shortcode_media"]
            username = body["owner"]["username"]
            post_date = self.detect_date(str(json_data))
            caption = body["edge_media_to_caption"]["edges"][0]["node"]["text"].strip()

        return username, post_date, caption

    def detect_date(self, text):
        date_posted = ""
        split_text = text.split()

        for i in range(len(split_text)):
            try:
                if (split_text[i] == "on") and (split_text[i + 1] in self.months):
                    month = split_text[i + 1]
                    day = split_text[i + 2][:-1]
                    year = split_text[i + 3]
                    date_posted = f"{day} {month} {year}"
            except IndexError or KeyError:
                continue
        return date_posted

    def __repr__(self):
        return self.html_data


class EventLog:
    def __init__(self):
        self.keywords = ["lomba",
                         "competition",
                         "pertandingan",
                         "kompetisi",
                         "sayembara",
                         "turnamen",
                         "tournament"]
        self.url = []
        self.username = []
        self.post_date = []
        self.caption = []
        date = str(datetime.date.today())
        self.outputfilename = f"rcts_{date}.xlsx"

    def add_event(self, new_url, new_username, new_postdate, new_caption):
        self.url.append(new_url)
        self.username.append(new_username)
        self.post_date.append(new_postdate)
        self.caption.append(new_caption)

    def delete_at_index(self, input_dict, index):
        input_dict["url"].pop(index)
        input_dict["username"].pop(index)
        input_dict["post_date"].pop(index)
        input_dict["caption"].pop(index)

    def filter_lomba(self, input_dict):
        new_dict = {"url": [],
                    "username": [],
                    "post_date": [],
                    "caption": []}
        for caption_index in range(len(input_dict["caption"])):
            lower_caption = input_dict["caption"][caption_index].lower()
            char_only = re.findall(r"[\w']+|[.,!?;]", lower_caption)
            for keyword in self.keywords:
                if keyword in char_only:
                    new_dict["url"].append(input_dict["url"][caption_index][:-6])
                    new_dict["username"].append(input_dict["username"][caption_index])
                    new_dict["post_date"].append(input_dict["post_date"][caption_index])
                    new_dict["caption"].append(input_dict["caption"][caption_index])
                    break

        return new_dict

    def to_excel(self, do_filter):
        dict_out = {"url": self.url,
                    "username": self.username,
                    "post_date": self.post_date,
                    "caption": self.caption}
        if do_filter:
            filtered_dict = self.filter_lomba(dict_out)
            df = pd.DataFrame(filtered_dict)
        else:
            df = pd.DataFrame(dict_out)
        df.to_excel(self.outputfilename)


if __name__ == '__main__':
    print("REAL TIME COMPETITION TRACKING SYSTEM")
    print("DIVISI EKSTERNAL BEM CIT 2021/2022\n")
    print("Selalu gunakan format file .xlsx")

    system_input = sys.argv

    usernamefile = str(system_input[1])
    n_posts = int(system_input[2])
    timing_coef = float(system_input[3])
    do_filter_keywords = bool(system_input[4])

    rcts_url = URLList(usernamefile, n_posts, timing_coef, do_filter_keywords)

    print("Finished")
    time.sleep(0.5)
    print("Exiting...")
    time.sleep(0.5)
