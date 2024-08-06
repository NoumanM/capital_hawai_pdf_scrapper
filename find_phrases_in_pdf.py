import datetime
from glob import glob
from PyPDF2 import PdfReader
import os
import csv

date_today = datetime.datetime.now().strftime("%d-%m-%Y")
print('Today: ', date_today)
base_url = 'https://www.capitol.hawaii.gov/sessions/session2024/Testimony/'
# list_of_phrases = ["grassroot institute", "tax foundation", "hawaii appleseed", "hawaii chamber", "grassrootinstitute",
#                    "taxfoundation", "hawaiiappleseed", "hawaiichamber",
#                    'appleseed', 'hawaii alliance for progressive action', 'hawaiiallianceforprogressiveaction',
#                    'hawaiialliance', 'progressiveaction', 'hawaii chamber of commerce', 'hawaiichamberofcommerce',
#                    'chamberofcommerce', 'UHERO', 'uhero'
#                    ]
# list_of_phrases = [
#     "League of Women","Kris Coffield","Commerce Hawaii",
#     "Association of REALTORS","Sierra Club","UNITE HERE Local 5","Lahaina Strong",
#     "Alliance for Progressive","hawaiiyimby","DEMOCRATIC PARTY OF", "hawaiisfuture",
#     'hcan', 'leagueofwomen', 'kriscoffield', 'hihac', 'commercehawaii', 'associationofrealtors', 'sierraclub',
#     'uniteherelocal5', 'lahainastrong', 'ilwu', 'allianceforprogressive',  'democraticpartyof',
# ]
list_of_phrases = [
    "HCAN", "League of Women", "Kris Coffield", "HiHAC", "Commerce Hawaii", "Association of REALTORS", "Sierra Club",
    "UNITE HERE Local 5", "Lahaina Strong", "ILWU", "Alliance for Progressive", "hawaiiyimby",
    "DEMOCRATIC PARTY OF", "hawaiisfuture"
]

working_dir = os.getcwd()
download_dir = os.path.join(working_dir, 'downloaded_pdfs')
output_file_name = os.path.join(working_dir, f'output-{date_today}.csv')
pdf_files = glob(os.path.join(download_dir, '*.pdf'))
done_files_csv_path = os.path.join(working_dir, f'done_files-{date_today}.csv')


def write_data_in_csv_file(data_list, file_name):
    csv_file_name = os.path.join(working_dir, f'{file_name}-{date_today}.csv')
    exist = False
    if os.path.exists(csv_file_name):
        exist = True
    with open(csv_file_name, 'a+', newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        for d in data_list:
            if not exist:
                writer.writerow(d.keys())
            writer.writerow(d.values())


def find_phrase_count():
    done_files = []
    if os.path.exists(done_files_csv_path):
        with open(done_files_csv_path, 'r', encoding='utf-16') as infile:
            reader = csv.reader(infile)
            for row in reader:
                done_files.append(row[0])
    for pdf_file in pdf_files:
        try:
            if pdf_file in done_files:
                continue
            pdf_name = pdf_file.split('\\')[-1]
            pdf_url = base_url + pdf_name
            print('PDF URL: ', pdf_url)
            reader = PdfReader(pdf_file)
            number_of_pages = len(reader.pages)
            print('NUMBER OF PAGES: ', number_of_pages)
            pdf_main_dict = {'url': pdf_url}
            for phrase in list_of_phrases:
                pdf_main_dict[phrase] = 0
            for page_number in range(number_of_pages):
                page = reader.pages[page_number]
                text = page.extract_text()
                phrase_count = {phrase: pdf_main_dict[phrase] + text.count(phrase) for phrase in list_of_phrases}
                pdf_main_dict.update(phrase_count)

            pdf_main_dict['numOfPages'] = number_of_pages
            exists = False
            if os.path.exists(output_file_name):
                exists = True
            with open(output_file_name, 'a+', newline='') as output_file:
                csv_writer = csv.writer(output_file)
                if not exists:
                    csv_writer.writerow(list(pdf_main_dict.keys()))
                csv_writer.writerow(list(pdf_main_dict.values()))

            write_data_in_csv_file([{'pdf_path': pdf_file}], 'done_files')

        except Exception as e:
            write_data_in_csv_file([{'message': str(e)}], 'find_phrases_errors')


if __name__ == '__main__':
    find_phrase_count()
