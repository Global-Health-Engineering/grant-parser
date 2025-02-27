# import asyncio
# from playwright.async_api import async_playwright

# async def main(grant_links = []):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto("http://playwright.dev")
#         print(await page.title())
#         await browser.close()

# asyncio.run(main())

from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import traceback

import argparse
from pathlib import Path
import csv
import os


def sync_parse(headless_run=True):

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless_run)

    page = browser.new_page()
    url_link = "https://www.volkswagenstiftung.de/en/our-funding-portfolio"
    page.goto(url_link)

    # reject cookies:
    reject_cookeis_btn = page.locator("div.cmpboxinner").get_by_text("Reject all")
    if "cmpbntnotxt" == reject_cookeis_btn.get_attribute("id"):
        reject_cookeis_btn.click()

    o = urlparse(url_link)
    parsed_results = []

    while True:
        articles = page.locator("div.content div.list-grant ul.list-grant__items").get_by_role("listitem").filter(has=page.locator("div.list-item-grant"))
        articles_count=articles.count()
        for i in range(articles_count):
            grant = articles.locator(f"nth={i}").locator("div.list-item-grant div.list-item-grant__content")

            title = grant.get_by_role("heading").all_text_contents()
            try:
                href = grant.get_by_role("link").get_attribute("href", timeout=60000)
                if "https" in href:
                    link=href
                else:
                    link = o.hostname + href
            except:
                print(traceback.format_exc)
                link = "Failed to retrive"
            deadline = grant.locator("div.list-item-grant__meta-label-wrapper").locator("nth=-1").locator("span.item-el-date").all_text_contents()
            deadline = [part.replace("  ","").replace("\n","")  for part in deadline]
            # print(f"\n\n#i: {i}, title: {title}\nlink: {link},\ndeadline: {deadline} ")
            parsed_results.append({
                    "title": " ".join(title),
                    "link": link,
                    "deadline": " ".join(deadline)
                })
        forelast_nav_button=page.locator("div.content div.list-grant").get_by_role("navigation").get_by_role("listitem").locator("nth=-2")
        if "item--next" not in forelast_nav_button.get_attribute("class"):
            break
        else:
            forelast_nav_button.get_by_role("link").click()
    # print("DONE")


    browser.close()
    playwright.stop()

    return parsed_results


def save_results_to_csv(output_file_path, results):

    # Generate CSV file name based on current timestamp
    # timestamp="latest"
    csv_file = output_file_path #f"results/parsed_results_{timestamp}.csv"
    
    # Define CSV header based on result structure
    header = ['title', 'link', 'deadline']

    # Write the results to CSV file
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Results saved to {csv_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_file_name", help=(
        "NAME of the OUTPUT CSV file in the OUTPUT_DIR "
        "directory, by default (almost) same as the script name"
        ) )
    parser.add_argument("--output_dir", help=(
        "OPTIONAL DIRECTORY RELATIVE PATH "
        "by default set to ../results directory"
        ))
    args=parser.parse_args()
    output_dir=args.output_dir
    if output_dir is None:
        output_dir=Path(os.getcwd()).joinpath("results")
    else:
        output_dir=Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file_name=args.output_file_name
    if output_file_name is None:
        output_file_name="Volkswagen" + ".csv"

    output_file_path = output_dir.joinpath(output_file_name)
    for i in range(50):
        parsed_results = sync_parse()
        if parsed_results:
            break
    save_results_to_csv(output_file_path, parsed_results)
    


if __name__=="__main__":
    main()

    