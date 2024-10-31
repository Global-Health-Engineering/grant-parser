
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse
import argparse
from pathlib import Path
import csv
import os
import time

def sync_parse(headless_run=True):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless_run)
    # parsed_results = {}
    parsed_results = []
    url_link = "https://www.researchprofessional.com/0/rr/home"
    page = browser.new_page()
    page.goto(url_link)
    o = urlparse(url_link)
    try:
        page.locator("button:has-text('Accept all')").click()
    except:
        pass
    wait_max_seconds = 300
    stat_time = time.time()
    while wait_max_seconds>=0:
        try:
            page.get_by_role("banner").get_by_role("link", name="Funding").click(timeout=60_000) # 1 mins
        except PlaywrightTimeoutError:
            end_time=time.time()
            print(f"EXCEPTED seconds passed: {end_time-stat_time}")
            time.sleep(1)
            wait_max_seconds-=end_time-stat_time
        else:
            end_time=time.time()
            print(f"seconds passed: {end_time-stat_time}")
            break
    nav_bar = page.get_by_role("navigation")
    fields = nav_bar.get_by_role("list").get_by_role("listitem").all()[:-2]
    field_nav= {}
    for field in fields:
        field_name = field.get_by_role("link").all_inner_texts()[0]
        # parsed_results[field_name] = {}
        field_href = field.get_by_role("link").get_attribute("href")
        if "https" in field_href:
            field_link=field_href
        else:
            field_link = o.scheme + "://" + o.hostname + field_href
        # print(f"\n\n {field_link}\n\n")
        field_nav[field_name] = field_link
    for field_name, field_link in field_nav.items():
        try:
            page.goto(field_link, wait_until="domcontentloaded", timeout = 100_000) # 1 min 40 seconds
        except PlaywrightTimeoutError:
            print(f"skipping {field_link}")
            continue
        time.sleep(0.5)
        grants_in_field = page.get_by_role("listitem").filter(has_text="New Calls") \
        .get_by_role("list").get_by_role("listitem")
        print(f"{grants_in_field.count()} grants in {field_name} field found")
        grant_links = {}
        for grant in grants_in_field.all():
            # print()
            title = grant.get_by_role("heading").all_inner_texts()
            # print(title)
            title = " ".join(title)
            link_to_grant = grant.get_by_role("heading").get_by_role("link").get_attribute('href')
            if "https" not in link_to_grant: # relative link?
                link_to_grant = o.scheme + "://" + o.hostname + link_to_grant
            # print(link_to_grant)
            grant_links[title] =link_to_grant

        for title, link_to_grant in grant_links.items():
            page.goto(link_to_grant, wait_until='domcontentloaded')
            max_wait = 2# seconds to wait at most
            while max_wait:
                closing_date = page.get_by_role("paragraph").filter(has_text="Closing date").get_by_role("time").all_inner_texts()
                if len(closing_date):
                    break
                else:
                    closing_date = []
                    time.sleep(1)
                    max_wait-=0.5
            if max_wait:
                
                deadline = " ".join(closing_date)
            else:
                deadline = 'Failed to retrive'

            parsed_results.append({
                    "title": field_name + ": "+title,
                    "link": link_to_grant,
                    "deadline": deadline
                })


    print(parsed_results)
        # break

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
        output_file_name="Research_Professionals" + ".csv"

    output_file_path = output_dir.joinpath(output_file_name)
    parsed_results = sync_parse()
    save_results_to_csv(output_file_path, parsed_results)
    


if __name__=="__main__":
    main()

    