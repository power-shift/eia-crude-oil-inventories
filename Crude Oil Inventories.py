import time
import sched
import datetime
import csv
import urllib.request
from urllib import error
import codecs
import fitz
import requests


# Report URLs
data_url = 'https://ir.eia.gov/wpsr/table4.csv'
summary_url = 'https://ir.eia.gov/wpsr/wpsrsummary.pdf'
overview_url = 'https://ir.eia.gov/wpsr/overview.pdf'

results = []

global start_time

today = datetime.datetime.today().date()


def get_report(url):
    download_successful = False

    # Keep retrying until successful response form the site; the site gets put into 500 mode right before the release
    while not download_successful:
        try:
            r = urllib.request.urlopen(url)
            start_time = time.time()
            end_time = time.ctime(time.time())
    
            print(f"Report Download Success {end_time}")

            download_successful = True

        except urllib.error.URLError as e:
            if int(e.code) != 200:
                print("ERROR DOWNLOADING DATA: {} {}".format(e.code, time.ctime(time.time())))

    csvfile = csv.reader(codecs.iterdecode(r, 'utf-8'))

    # Process and load data
    try:
        for index, line in enumerate(csvfile):
            results.append(line)
            
    except UnicodeDecodeError:
        # the last line of the file is a question mark or some character, so it always throws an error - we'll ignore it
        pass
    
    # save csv file
    with open('report_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)

    return results, start_time


def get_summary(summary_url, start_time):

    # Get PDF from the site
    response = urllib.request.urlopen(summary_url)

    # Save PDF to disk
    with open('report_summary.pdf', 'wb') as f:
        f.write(response.read())

    # Extract text from PDF
    doc = fitz.open("report_summary.pdf")
    page1 = doc.load_page(0)
    page1blocks = page1.get_text("blocks")
    summary_output = "\n\n\n"

    # Replace all line breaks and recreate paragraphs, then add blocks into a single string, separated by \n for each block
    for x in page1blocks:
        summary_output += x[4].replace('\n', '') + '\n\n'

    runtime = round(time.time() - start_time, 4)

    print(summary_output)


def create_image(overview_url):
    start_time = time.time()
    response = requests.get(overview_url)

    # Save PDF to disk
    pdf_file = 'report_overview.pdf'

    with open(pdf_file, 'wb') as f:
        f.write(response.content)
        
    doc = fitz.open(pdf_file)

    zoom = 2
    mat = fitz.Matrix(zoom, zoom)  # sets image quality
    
    page = doc.load_page(0)  # get first page
    page.set_cropbox(fitz.Rect(0.0, 0.0, 612, 225))
    
    pix = page.get_pixmap(matrix = mat)  # set with image quality

    png_image = "report_image.png"
    pix.save(png_image)
    

def do_comparison():
    # Compare previous report's data vs current
    print("\nRunning comparison...\nStart time: {}\n".format(time.ctime(time.time())))

    report_date_validated = False

    while not report_date_validated:
        results, start_time = get_report(data_url)
        
        report_date = datetime.datetime.strptime(results[0][1], '%m/%d/%y').date()  # get date from csv and convert into date object
        report_age_days = today - report_date
        report_age_days = report_age_days.days
        
        print(f"Report date: {report_date}, Age: {report_age_days}")
        
        report_age_threshold = 11  # set back to 7 after testing
    
        if report_age_days <= report_age_threshold:
            print(f"Valid Report (Less than {report_age_threshold} days old)")
            report_date_validated = True
        else:
            print(f"Report is too old (Over {report_age_threshold} days old). Retrying.")

    eia_change = float(results[2][3])  # excluding SPR
    gas_change = float(results[11][3])
    distillate_change = float(results[17][3])
    cushing_change = float(results[5][3])
    report_date = results[0][1]

    runtime_data = round(time.time() - start_time, 4)
    
    comparison_text = \
        f"\nEIA CRUDE OIL INVENTORIES REPORT \n" + \
        "• Crude Oil: {:+}M\n".format(eia_change) + \
        "• Gasoline: {:+}M\n".format(gas_change) + \
        "• Distillates: {:+}M\n".format(distillate_change) + \
        "• Cushing: {:+}M\n\n".format(cushing_change) + \
        ""

    print(comparison_text)

    get_summary(summary_url, start_time)
    create_image(overview_url)


if __name__ == "__main__":
    next_runtime = datetime.datetime(2024, 5, 27, hour=15, minute=46)  # adjust this to the next report date and time
    trigger_seconds_offset = -1.5  # adjust script to run just before the scheduled time
    trigger_time = (next_runtime - datetime.datetime.now()).total_seconds() + trigger_seconds_offset

    s = sched.scheduler(time.time, time.sleep)
    s.enter(trigger_time, 1, do_comparison)

    print(f"\nNext Runtime: {next_runtime}")

    while True:
        countdown = next_runtime - datetime.datetime.now()
        countdown_str = str(countdown).split('.')[0]  # do not display microseconds
        print('\rTime Remaining:', countdown_str, end='')

        if countdown.total_seconds() <= 2:
            s.run()
            break

        time.sleep(1)
