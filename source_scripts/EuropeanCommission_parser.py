import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Playwright
import tqdm
import traceback
from urllib.parse import urlparse
import argparse
from pathlib import Path
import csv
import os


async def async_parse(headless_run=True):#playwright: Playwright):
    async def handle_popup(*args, **kwargs):
        print("handle_popup triggered")
        if len(args):
            print(f"args: {args}")
        else:
            print("no args")

        if len(kwargs):
            print(f"kwargs: {kwargs}")
        else:
            print("no kwargs")
        print("popup window registered!")
        await page.get_by_role("dialog").get_by_role("checkbox").click()
        await asyncio.sleep(3)
        await page.get_by_role("dialog").get_by_role("button").click()
        print("popup handled my Lord")


    async def handle_dialog(*args, **kwargs):
        print("handle_dialog triggered")
        if len(args):
            print(f"args: {args}")
        else:
            print("no args")

        if len(kwargs):
            print(f"kwargs: {kwargs}")
        else:
            print("no kwargs")
        print("Dialog window registered!")
        await page.get_by_role("dialog").get_by_role("checkbox").click()
        await asyncio.sleep(3)
        await page.get_by_role("dialog").get_by_role("button").click()
        print("dialog handled my Lord")

    async def handle_block_window():
        print("handle_block_window triggered")

        try:
            if await page.get_by_label("Please do not show again").count(timeout = 1000):
                await page.get_by_label("Please do not show again").check()
                await page.get_by_label("Welcome to the EU Funding &").get_by_role("button", name="eUI Icon").click()
            else:
                await page.locator("eui-dialog-container").get_by_role("document").get_by_role("checkbox").click(timeout=1000)
                await page.locator("eui-dialog-container").get_by_role("document").get_by_role("button").filter(has=page.locator("span.eui-button__container")).click(timeout=1000)
        except PlaywrightTimeoutError as err:
            return False
        else:
            return True
    
    
    
    url_link = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search"
    parsed_results = []
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless_run)
    page = await browser.new_page()
    page.set_default_timeout(50000)
    page.on("dialog", handle_dialog)
    page.on("popup", handle_popup)

    o = urlparse(url_link)

    await page.goto(url_link)
    # reject cookies:
    await page.get_by_role("link").filter(has=page.get_by_text("Accept only essential cookies")).click()
    
    await asyncio.sleep(1)

    nav_bar = page.get_by_role("navigation")
    funding_tab=nav_bar.get_by_role("listitem").filter(has=page.get_by_title("Funding"))
    await funding_tab.hover()
    await asyncio.sleep(1)
    await funding_tab.get_by_text("Calls for proposals").click()
    await asyncio.sleep(1)

    # try to set view to 100 grants per page (so that there are less reroutes):
    try:
        # await page.locator("eui-paginator eui-dropdown").get_by_role("button").click(timeout=1000)
        # await page.locator("eui-dropdown-content").get_by_role("button").filter(has_text="100").click(timeout=1000)
        await page.get_by_role("button", name="Select Items per page").click()
        await page.get_by_role("menuitem", name="100").click()
        await asyncio.sleep(1)
    except:
        pass
    await asyncio.sleep(1)
    # Parsing loop that also handles any blocking popups
    loop_running = True
    while loop_running: 
        try:
            grants = await page.locator("sedia-result-card-calls-for-proposals").all()
            grants_count_on_page = len(grants)
            # print(f"There are {grants_count_on_page} grants here")
            for grant in grants:
                title = await grant.locator("eui-card-header-title").get_by_role("link").all_text_contents()
                href = await grant.locator("eui-card-header-title").get_by_role("link").get_attribute("href")
                if "https" in href:
                    link=href
                else:
                    link = o.hostname + href
                
                deadline = await grant.locator("eui-card-header-subtitle sedia-result-card-type").locator("nth=1")\
                                        .locator("strong.ng-star-inserted").locator("nth=1").all_text_contents()
                # print(f"\n\ntitle: {title}\nlink: {link},\ndeadline: {deadline} ")
                parsed_results.append({
                    "title":" ".join(title),
                    "link":link,
                    "deadline":" ".join(deadline)
                })


            next_page_btn = page.locator("eui-paginator div.eui-paginator__page-navigation-item")\
                .locator("nth=-2").get_by_role("button")
            next_page_btn_disabled = await next_page_btn.get_attribute("disabled", timeout=500)
            if next_page_btn_disabled == "disabled":
                loop_running = False
                break
            else:
                await next_page_btn.click(timeout = 10000)
                await asyncio.sleep(1)

        except PlaywrightTimeoutError as err:
            handled = await handle_block_window()
            if not handled:
                print("Error could not be handled")
                loop_running = False
                return
    

    await browser.close()
    await playwright.stop()

    print("DONE")

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
    

async def main():

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
        output_file_name="European_Comission" + ".csv"

    output_file_path = output_dir.joinpath(output_file_name)

    # async with async_playwright() as playwright:
        # await async_parse(playwright)
    parsed_results = await async_parse()
    save_results_to_csv(output_file_path, parsed_results)


if __name__ == "__main__":
    try:
        # Use asyncio.run only if the event loop is not already running
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Handle the closed loop scenario by creating and running a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
