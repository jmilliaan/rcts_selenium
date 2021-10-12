import re
import requests
import json
import html
import time
import pandas as pd
from collections import defaultdict
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# important constants
account_filename = "informasilomba.xlsx"
log_filename = "newlog.xlsx"
ig_url = "https://www.instagram.com"
rcts_username = ""
rcts_password = ""
number_of_posts = 3
t_coef = 1.2

months = ["January", "February", "March",
          "April", "May", "June",
          "July", "August", "September",
          "October", "November", "December"]
header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        "AppleWebKit/537.36 (KHTML, like Gecko)"
                        "Chrome/94.0.4606.54 Safari/537.36",
          "cookie": "ig_did=EEC95D6A-0846-47F2-8B87-53F3B64A6007;"
                    "ig_nrcb=1; mid=YT7mCwALAAEdoraS5_1uT4cn27bC;"
                    "ds_user_id=49129421296;"
                    "csrftoken=jmtrjBYiSK1vA1tMSZtYpZoWK1kJfa8j;"
                    "sessionid=49129421296:IuiCKTr3UjQcGo:15;"
                    "rur='VLL\05449129421296\0541663920099:"
                    "01f72808aa326e662dbb067009bf1016c2aab88820d952e098afce519878fc54f21cecc8'"}


def detect_date(text):
    date_posted = ""
    split_text = text.split()

    for i in range(len(split_text)):
        try:
            if (split_text[i] == "on") and (split_text[i + 1] in months):
                month = split_text[i + 1]
                day = split_text[i + 2][:-1]
                year = split_text[i + 3]
                date_posted = f"{day} {month} {year}"
        except IndexError or KeyError:
            continue
    return date_posted


def get_duplicates(seq):
    tally = defaultdict(list)
    seq2 = []
    for i in range(len(seq)):
        seq2.append([i, seq[i]])
    for i, item in seq2:
        tally[item].append(i)
    return ((key, locs) for key, locs in tally.items()
            if len(locs) > 1)


def university_competition_filter(listoftext):
    keywords = ["mahasiswa",
                "universitas",
                "university",
                "undergraduate",
                "sarjana",
                "college",
                "bem",
                "ormawa",
                "hima",
                "s1"]
    for keyword in keywords:
        if keyword in listoftext:
            return True
    else:
        return False


def competition_filter(input_dict):
    keywords = ["lomba",
                "competition",
                "pertandingan",
                "kompetisi",
                "sayembara",
                "turnamen",
                "tournament",
                "perlombaan"]

    comp_filter_dict = {"url": [],
                        "username": [],
                        "post_date": [],
                        "caption": [],
                        "image_url": []}

    similar_filter_dict = {"url": [],
                           "username": [],
                           "post_date": [],
                           "caption": [],
                           "image_url": []}
    bigmat = []
    insignificant_index = []
    for caption_index in range(len(input_dict["caption"])):
        lower_caption = input_dict["caption"][caption_index].lower()
        char_only = re.findall(r"[\w']+|[.,!?;]", lower_caption)
        for keyword in keywords:

            if (keyword in char_only) and (university_competition_filter(char_only)):
                comp_filter_dict["url"].append(input_dict["url"][caption_index])
                comp_filter_dict["username"].append(input_dict["username"][caption_index])
                comp_filter_dict["post_date"].append(input_dict["post_date"][caption_index])
                comp_filter_dict["caption"].append(input_dict["caption"][caption_index])
                comp_filter_dict["image_url"].append(input_dict["image_url"][caption_index])
                break

    for similar_index in range(len(comp_filter_dict["caption"])):
        lower_similar = comp_filter_dict["caption"][similar_index].lower()
        similar_charonly = re.findall(r"[\w']+|[.,!?;]", lower_similar)
        bigmat.append("".join(similar_charonly[:4]))

    bigdup = get_duplicates(bigmat)

    for dup in bigdup:
        insignificant_index.append(dup[1][1:][0])

    for final_filter in range(len(comp_filter_dict["caption"])):
        if final_filter in insignificant_index:
            continue
        else:
            similar_filter_dict["url"].append(comp_filter_dict["url"][final_filter])
            similar_filter_dict["username"].append(comp_filter_dict["username"][final_filter])
            similar_filter_dict["post_date"].append(comp_filter_dict["post_date"][final_filter])
            similar_filter_dict["caption"].append(comp_filter_dict["caption"][final_filter])
            similar_filter_dict["image_url"].append(comp_filter_dict["image_url"][final_filter])
    return similar_filter_dict


if __name__ == '__main__':
    accounts = pd.read_excel(account_filename,
                             sheet_name="Sheet1",
                             engine="openpyxl")
    rcts_accounts = []
    for account_username in accounts["username"]:
        rcts_accounts.append(str(account_username))

    df = pd.read_excel(log_filename,
                       sheet_name="Sheet1",
                       engine="openpyxl")
    df_data = df.iloc[:, 3:7]
    chrome_options = Options()
    chrome_options.add_argument("--window-size=800,900")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(ig_url)
    time.sleep(t_coef * 2.5)

    username = driver.find_element_by_css_selector("input[name='username']")
    password = driver.find_element_by_css_selector("input[name='password']")

    username.clear()
    password.clear()

    username.send_keys(rcts_username)
    password.send_keys(rcts_password)
    print("Login")

    driver.find_element_by_css_selector("button[type='submit']").click()
    print("Clicked Login Button")
    time.sleep(t_coef * 2.5)

    driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
    print("Clicked Not Now")
    time.sleep(t_coef * 2.5)

    driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
    print("Clicked Not Now")
    c = 1
    new_dataset = {"url": [],
                   "username": [],
                   "post_date": [],
                   "caption": [],
                   "image_url": []}

    for usr in rcts_accounts:
        print(c, usr)
        c += 1
        searchbox = driver.find_element_by_css_selector(
            "input[placeholder='Search']")
        searchbox.clear()

        searchbox.send_keys(usr)
        time.sleep(t_coef * 1.5)

        searchbox.send_keys(Keys.ENTER)
        time.sleep(t_coef * 1.5)

        searchbox.send_keys(Keys.ENTER)
        time.sleep(t_coef * 2.5)

        # scroll down to acquire more posts
        driver.execute_script("window.scrollTo(0, "
                              "document.body.scrollHeight);"
                              "var lenOfPage=document.body.scrollHeight;"
                              "return lenOfPage;")

        links = driver.find_elements_by_tag_name('a')
        imglist = driver.find_elements_by_class_name("KL4Bh")
        main_posts = []
        post_count = 0

        count = 0
        for link in links:
            try:
                raw_url = link.get_attribute("href")
                # for im in img:
                #     print(im.get_attribute("src")[:-2])


            except selenium.common.exceptions.StaleElementReferenceException:
                print("> stale element reference exception")
                continue

            if "/p/" in raw_url:
                json_url = raw_url + "?__a=1"
                jsontext = requests.get(json_url, headers=header)
                htmltext = html.unescape(jsontext.text)

                head = htmltext[:9]

                if head == '{"graphql':
                    print(" ", post_count, raw_url)
                    post_count += 1
                    json_data = json.loads(htmltext)

                    try:
                        body = json_data["graphql"]["shortcode_media"]

                        username = body["owner"]["username"]
                        post_date = detect_date(str(json_data))

                        edges = body["edge_media_to_caption"]["edges"]
                        caption = edges[0]["node"]["text"].strip()

                        image_url = body["display_url"]

                    except IndexError:
                        post_date = ""
                        caption = ""
                        image_url = ""
                        pass

                    new_dataset["url"].append(raw_url)
                    new_dataset["username"].append(usr)
                    new_dataset["post_date"].append(post_date)
                    new_dataset["caption"].append(caption)
                    new_dataset["image_url"].append(image_url)
                if post_count == number_of_posts:
                    break
    print(new_dataset["url"], new_dataset["image_url"])
    driver.close()

    new_dataset = competition_filter(new_dataset)
    new_dataset_df = pd.DataFrame(new_dataset)
    new_df = pd.concat([df, new_dataset_df])

    writer = pd.ExcelWriter(log_filename)
    new_dataset_df.to_excel(writer, "New Competitions", index=False)
    new_df.to_excel(writer, "Sheet1")
    writer.save()
