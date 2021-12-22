import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

ua = UserAgent()
data_ozon_items = []

headers = {
    'content-type': 'application/json; charset=UTF-8',
    'user-agent': ua.random,
    'authority': 'ozon-api.exponea.com',
    'cookie': 'xnpe_09568822-e4af-11e7-9f8d-ac1f6b02225e=e95a0152-f776-43a5-9f30-bc78498b395e'
}

def ozon_scr(count):
    for k in range(1,count+1):
        url =  f'https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=/category/proektory-15615/?page={k}&page_changed=true'
        try:
            req = requests.get(url, headers=headers)
            time.sleep(1)
            site_cont = req.json()
            with open('ozon_page.json', 'w', encoding='utf-8') as file:
                json.dump(site_cont,file, ensure_ascii=False, indent=4)
            with open('ozon_page.json', encoding='utf-8') as file:
                file_content = file.read()
            site_json = json.loads(file_content)
            print(k)
            for i in site_json['trackingPayloads'].values():
                z = json.loads(i)
                try:
                    data_ozon_items.append({
                        'name': z['title'],
                        'rang':z['index'],
                        'id': z['id'],
                        'old_price': z['price'],
                        'price': z['finalPrice'],
                        'rating': z['rating'],
                        'feedback': z['countItems'],
                        'brand': z['brand'],
                        'url': f'ozon.ru{z["link"]}'
                    })
                except Exception as ex:
                    pass
        except:
            print(f'Страница отдала пустой ответ {k}')
            time.sleep(5)
        data_info = [dict(t) for t in {tuple(d.items()) for d in data_ozon_items}]
        with open('data_Ozon.json', 'w', encoding='utf-8') as file:
            json.dump(data_info, file, ensure_ascii=False, indent=4)
    print('Закончил с названиями и т.д')


def ozon_stock(count):
    max_page = 0
    list_Items = []
    req1 = requests.get('https://www.ozon.ru/category/proektory-15615/', headers=headers)
    time.sleep(1)
    with open('ozon_page.html', 'w', encoding='utf-8') as file:
        file.write(req1.text)
    with open('ozon_page.html', 'r', encoding='utf-8') as file:
        file_content = file.read()
    soup = BeautifulSoup(file_content, 'html.parser')
    count_id = soup.find('div', id='state-searchResultsV2-252189-default-1')
    find_count = count_id.get('data-state')
    site_json = json.loads(find_count)
    with open('ozon_stock.json', 'w', encoding='utf-8') as file:
        json.dump(site_json, file)
    with open('ozon_stock.json', 'r', encoding='utf-8') as file:
        file_contetn2 = file.read()
    stock_count = json.loads(file_contetn2)
    for i in stock_count['items']:
        list_Items.append({
            'id': int(i['multiButton']['ozonButton']['addToCartButtonWithQuantity']['action'].get('id')),
            'stock': i['multiButton']['ozonButton']['addToCartButtonWithQuantity'].get('maxItems'),
            'img': i['tileImage']['images'][0]
        })
    for z in range(2,count+1):
        print(z)
        req = requests.get(f'https://www.ozon.ru/category/proektory-15615/?page={z}', headers=headers)
        time.sleep(1)
        with open('ozon_page.html', 'w', encoding='utf-8') as file:
            file.write(req.text)
        with open('ozon_page.html', 'r', encoding='utf-8') as file:
            file_content = file.read()
        soup = BeautifulSoup(file_content, 'html.parser')
        count_id = soup.find('div', id ='state-searchResultsV2-252189-default-1')
        page_number = soup.find_all('a', class_= 'b9g0')
        list_page = []
        for i in page_number[:-1]:
            if i.text != '...':
                list_page.append(int(i.text))
        if list_page != []:
            if max_page < max(list_page):
                max_page = max(list_page)
        try:
            find_count = count_id.get('data-state')
            site_json = json.loads(find_count)
            with open('ozon_stock.json', 'w', encoding='utf-8') as file:
                json.dump(site_json,file)
            with open('ozon_stock.json', 'r', encoding='utf-8') as file:
                file_contetn2 = file.read()
            stock_count = json.loads(file_contetn2)
            for i in stock_count['items']:
                list_Items.append({
                    'id': int(i['multiButton']['ozonButton']['addToCartButtonWithQuantity']['action'].get('id')),
                    'stock':i['multiButton']['ozonButton']['addToCartButtonWithQuantity'].get('maxItems'),
                    'img': i['tileImage']['images'][0]
                })
            with open('stock_Ozon.json','w', encoding='utf-8') as file:
                json.dump(list_Items, file, indent=4, ensure_ascii=False)
        except:
            print(f'Страница {z} не прогрузилась')
            time.sleep(5)
        if z == max_page:
            print('Закончил собирать остатки')
            return max_page
            break

def get_ozon():
    with open('data_Ozon.json', 'r', encoding='utf-8') as file:
        file_content = json.loads(file.read())
    with open('stock_Ozon.json', 'r') as file:
        file_content2 = json.loads(file.read())
    data_ozon = []
    for i in file_content2:
        for z in file_content:
            if i['id'] == z['id']:
                data_ozon.append(i|z)
    data_info = [dict(t) for t in {tuple(d.items()) for d in data_ozon}]
    data_ozon_end = sorted(data_info,key=lambda x:x['rang'])
    with open('ozon_data_end.json', 'w', encoding='utf-8') as file:
        json.dump(data_ozon_end,file,indent=4, ensure_ascii=False)

def main():
    count = ozon_stock(500)
    ozon_scr(count)
    get_ozon()

if __name__ == "__main__":
    main()