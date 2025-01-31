import requests
from bs4 import BeautifulSoup
import json

def get_latest_courses_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    courses_urls = []
    for link in soup.find_all('a'):
        if 'Courses in English' in link.text:
            courses_urls.append(link.get('href'))
    if courses_urls:
        return max(courses_urls, key=lambda x: int(''.join(filter(str.isdigit, x))))
    else:
        return None

def get_course_numbers(html):
    soup = BeautifulSoup(html, 'html.parser')
    main_div = soup.find('div', id='main')
    if main_div:
        tables = main_div.find_all('table')
        for table in tables:
            course_numbers = []
            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')
                for column in columns:
                    if 'column-2' in column.get('class', []):
                        course_number = column.text.strip()
                        course_numbers.append(course_number)
            if course_numbers:
                return course_numbers
    return None

def get_malagim(html):
    soup = BeautifulSoup(html, 'html.parser')
    main_div = soup.find('div', id='main')
    if main_div:
        tables = main_div.find_all('table')
        for table in tables:
            malagim_numbers = []
            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')
                if len(columns) > 0:
                    malagim_number = columns[0].text.strip()
                    malagim_numbers.append(malagim_number)
            if malagim_numbers:
                return malagim_numbers
    return None

def fetch_data():
    try:
        url = 'https://ugportal.technion.ac.il/הוראה-ובחינות/'
        print(f"Sending GET request to {url}...")
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")

        course_numbers = []
        malagim_numbers = []

        if response.status_code == 200:
            latest_courses_url = get_latest_courses_url(response.text)
            if latest_courses_url:
                print(f"Fetching course numbers from {latest_courses_url}...")
                response = requests.get(latest_courses_url)
                course_numbers = get_course_numbers(response.text)
                if not course_numbers:
                    print('Failed to find course numbers!')
            else:
                print('Failed to find latest English courses URL! Maybe the page was changed.')
        else:
            print(f'Failed to fetch {url}. Status code: {response.status_code}')

        # Fetch malagim data
        malagim_url = "https://ugportal.technion.ac.il/הוראה-ובחינות/לימודי-העשרה/"
        print(f"Sending GET request to {malagim_url}...")
        response = requests.get(malagim_url)
        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            malagim_numbers = get_malagim(response.text)
            if not malagim_numbers:
                print('Failed to fetch malagim numbers!')
        else:
            print(f'Failed to fetch malagim URL. Status code: {response.status_code}')

    except Exception as e:
        print(f'An error occurred: {e}')
        return {'courses': [], 'malagim': []}

    return {'courses': course_numbers, 'malagim': malagim_numbers}

def read_from_file(filename='output.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'courses': [], 'malagim': []}

def write_to_file(data, filename='output.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data written to {filename}")

def main():
    previous_data = read_from_file()
    new_data = fetch_data()

    if not new_data['courses']:
        new_data['courses'] = previous_data['courses']
        print("No new courses data found. Using previous data.")
    else:
        print("Updated courses data.")

    if not new_data['malagim']:
        new_data['malagim'] = previous_data['malagim']
        print("No new malagim data found. Using previous data.")
    else:
        print("Updated malagim data.")

    write_to_file(new_data)

if __name__ == '__main__':
    main()
