
from playwright.sync_api import sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import argparse
from pathlib import Path
import csv
import os


def sync_parse(headless_run=True):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless_run)
    url_link = "https://www.snf.ch/en/LlLsqrrZVo4EqWui/page/open-calls"
    page = browser.new_page()
    page.goto(url_link)
    o = urlparse(url_link)

    articles = page.locator("div.grid-margin section.block-overview").locator(f"nth=0").get_by_role("article")
    articles_count=articles.count()
    parsed_results = []

    for i in range(articles_count):
        topic = articles.locator("a.topic-teaser__link").locator(f"nth={i}")
        href = topic.get_attribute("href")
        if "https" in href:
            link=href
        else:
            link = o.hostname + href
        title = topic.locator("div.topic-teaser__content").get_by_role("heading").all_text_contents()
        # deadline = topic.locator("div.topic-teaser__content").get_by_role("paragraph").all_text_contents()
        deadline_element = topic.get_by_text("Submission deadline:")
        deadline_text = deadline_element.text_content()
        deadline = deadline_text.split("Submission deadline:")[1].strip()
        deadline = datetime.strptime(deadline, "%d.%m.%Y %H:%M %Z")
        deadline = deadline.replace(tzinfo=ZoneInfo("CET")).date()
        
        parsed_results.append({
            "title":" ".join(title),
            "link": link,
            "deadline": str(deadline)
        })
    print("DONE")

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
        output_file_name="SNF" + ".csv"

    output_file_path = output_dir.joinpath(output_file_name)
    for i in range(50):
        # run at most 50 times to make sure the result file is not empty
        parsed_results = sync_parse()
        if parsed_results:
            break
    save_results_to_csv(output_file_path, parsed_results)
    

if __name__=="__main__":
    main()
    