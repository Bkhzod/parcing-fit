import requests
from bs4 import BeautifulSoup
import json
import csv

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'

# Show the site that we are not a bot

headers = {
    'Accept': '*/*',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.124 YaBrowser/22.9.4.863 Yowser/2.5 Safari/537.36'
}
req =requests.get(url, headers=headers)
src = req.text

# Save the site code to avoid repeated access to the original

with open('index.html', 'w') as file:
    file.write(src)

with open('index.html') as file:
    src= file.read()

#Collect all categories with links to them and write them to a file
soup = BeautifulSoup(src,'lxml')
all_products_href = soup.find_all(class_='mzr-tc-group-item-href')
al_categories_dict={}

for i in all_products_href:
    item_text= i.text
    item_href = 'https://health-diet.ru' + i.get('href')
    al_categories_dict[item_text]=item_href

with open('all_categories_dict.json', encoding='utf8') as file:
    all_categories = json.load(file)

# We go to each category link and collect data about products

count=0
iteration_count = int(len(all_categories)) - 1
print(f'Iterations:{iteration_count}')

for category_name, category_href in all_categories.items():
    # Replace unnecessary symbols
    rep=[',', '-', ' ']
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, '_')

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f'Data/{count}_{category_name}.html', 'w', encoding='utf8') as file:
        file.write(src)

    with open(f'Data/{count}_{category_name}.html', encoding='utf8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    #if page is not empty
    alert_er = soup.find(class_='uk-alert-danger')
    if alert_er is not None:
        continue

    #Get table heads
    table_head = soup.find(class_='mzr-tc-group-table').find('tr').find_all('th')

    product= table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(f'Data/{count}_{category_name}.csv', 'w', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product,
                calories,
                proteins,
                fats,
                carbohydrates
            )
        )
# Get product data
    products_data = soup.find(class_='mzr-tc-group-table').find('tbody').find_all('tr')

    product_info = []
    for item in products_data:
        products_tds = item.find_all('td')

        title = products_tds[0].find('a').text
        calories = products_tds[1].text
        proteins = products_tds[2].text
        fats = products_tds[3].text
        carbohydrates = products_tds[4].text

        product_info.append(
            {
                'Title':title,
                'Calories': calories,
                'Proteins': proteins,
                'Fats':fats,
                'Carbohydrates':carbohydrates
            }
        )
        with open(f'Data/{count}_{category_name}.csv', 'a', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )
    with open(f'Data/{count}_{category_name}.json', 'a', encoding='utf-8-sig') as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)


    print(f'# Itteration: {count}, {category_name} Is written...')
    iteration_count = iteration_count-1
    if iteration_count == 0:
        print('wor is done')
        break
    print(f'Itteration remain {iteration_count}')
    count += 1