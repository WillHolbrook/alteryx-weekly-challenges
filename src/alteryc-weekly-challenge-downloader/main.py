from multiprocessing import Pool
from pathlib import Path
import logging

import numpy as np
import pandas as pd
import pdfkit
import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify

message_class = "MessageView lia-message-view-forum-message lia-message-view-display lia-row-standard-unread " \
                "lia-thread-topic"
attachments_class = "Attachments lia-attachments-message lia-message-attachments lia-component-attachments " \
                    "lia-component-message-view-widget-attachments-search-and-message"
media_class = "lia-attachment-row-element lia-media-document"
link_class = "lia-link-navigation"
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


def download_challenge(challenge_number: int, challenge_name: str, challenge_link: str) -> None:
    challenge_name = slugify(challenge_name)
    challenge_folder_path = Path(f"./{challenge_number}-{challenge_name}").resolve()
    challenge_folder_path.mkdir(exist_ok=True)

    page = requests.get(challenge_link)

    soup = BeautifulSoup(page.content, "html.parser")
    attachments_var = soup\
        .find("div", class_=message_class)\
        .find("div", class_=attachments_class)\
        .find_all("div", recursive=False)

    for attachment_var in attachments_var:
        relative_link_var = attachment_var.find("div", class_=media_class).find("a", class_=link_class)['href']
        link_url = f"https://community.alteryx.com{relative_link_var}"

        file_name = relative_link_var.split("/")[-1]
        print(file_name)

        r = requests.get(link_url, allow_redirects=True)
        open(f"{str(challenge_folder_path)}/{file_name}", 'wb').write(r.content)
        print(link_url)

    pdfkit.from_url(challenge_link, f"{str(challenge_folder_path)}/{challenge_name}.pdf", configuration=config)


def unpack(x):
    try:
        download_challenge(x['Challenge Number'], x['Challenge Name'], x['Challenge Link'])
    except Exception:
        logging.exception(x)


if __name__ == "__main__":

    df = pd.read_csv("../../referenceFiles/AlteryxWeeklyChallengesLink.csv")
    df = df.iloc[241:, :]
    # parallelize_dataframe(
    #     df,
    #     lambda frame: frame.apply(lambda x: download_challenge(x['Challenge Number'], x['Challenge Name'], x['Challenge Link']), axis=1))
    df.apply(unpack, axis=1)
    # print(df)
    print(df.columns)

