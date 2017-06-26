import os
import requests
import sys
from lxml import html

DEBUG = False


def log(msg, is_error=False):
    if DEBUG or is_error:
        print(msg)


def replace_special_symbols(string):
    return string.replace("\\", "＼").replace("/", "／").replace(":", "：").replace("*", "＊").replace("?", "？").replace(
        "\"", "＂").replace("<", "＜").replace(">", "＞").replace("|", "｜")


def get_image_links(image_url):
    try:
        response = requests.get(image_url).content
    except Exception as e:
        log("Error occurs when getting image links", True)
        log(e, True)
        return
    image_page_html = html.fromstring(response)
    main_image = image_page_html.xpath("//div[@class='main-image']//img/@src")
    return main_image


def get_image_count_and_title(url):
    try:
        response = requests.get(url).content
    except Exception as e:
        log("Error occurs when get the image set page", True)
        log(e, True)
        return
    page_html = html.fromstring(response)
    last_page = page_html.xpath("//div[@class='pagenavi']/a[last()-1]/span")
    image_count = int(last_page[0].text)
    title = page_html.xpath("//h2[@class='main-title']")[0].text
    return image_count, title


def download_image(set_id):
    url = "http://mzitu.com/" + str(set_id)
    image_count, title = get_image_count_and_title(url)
    title = replace_special_symbols(title)
    if not os.path.exists(title):
        os.mkdir(title)
    else:
        return
    for i in range(1, image_count + 1):
        image_url = url + "/" + str(i)
        image_links = get_image_links(image_url)
        for link in image_links:
            filename = os.path.basename(link)
            log("Downloading images on Page " + str(i) + " of " + str(image_count) + " from " + title + " ...")
            log("Saving as " + filename + ".")
            if not os.path.exists(title + "/" + filename):
                with open(title + "/" + filename, "wb") as f:
                    try:
                        f.write(requests.get(link).content)
                    except Exception as e:
                        log("Error occurs when downloading file" + filename, True)
                        log(e, True)


def mzitu_dl():
    log("Hello mzitu!")
    try:
        set_id = sys.argv[1]
    except IndexError:
        set_id = input("Type the set id that you want to download: ")
    download_image(set_id)


def download_all():
    site_url = "http://www.mzitu.com/all/"
    try:
        response = requests.get(site_url).content
    except Exception as e:
        log("Error occurs when get all posts", True)
        log(e, True)
        return
    all_html = html.fromstring(html.tostring(html.fromstring(response).xpath("//div[@class='all']")[0]))
    years_str_html = all_html.xpath("//div[@class='year']")
    archives_html = all_html.xpath("//ul[@class='archives']")
    assert len(years_str_html) == len(archives_html)
    for year_count in range(0, len(years_str_html)):
        archive_html = html.fromstring(html.tostring(archives_html[year_count]))[0]
        year_str = years_str_html[year_count].text
        if not os.path.exists(year_str):
            os.mkdir(year_str)
        os.chdir(year_str)
        month_group_html = archive_html.xpath("//li")
        for group in month_group_html:
            month_html = html.fromstring(html.tostring(group))[0]
            month_str = month_html.xpath("//li/p/em")[0].text
            if not os.path.exists(month_str):
                os.mkdir(month_str)
            os.chdir(month_str)
            urls_html = month_html.xpath("//li/p[@class='url']/a")
            for url_html in urls_html:
                set_id = int(os.path.basename(url_html.xpath("@href")[0]))
                download_image(set_id)
            os.chdir("..")
        os.chdir("..")


if __name__ == '__main__':
    download_all()
