import requests, json
from urllib.request import urlretrieve
from urllib.parse import quote

from urllib.parse import quote_plus

from bs4 import BeautifulSoup


clayful_id = None
path = "./info.json"

href_data = []
src_data = []
json_data = []

for i in range(1, 57):
    url = f"https://myrobotsolution.com/store/?page={i}&"
    response = requests.get(url) 

    html = response.text 
    soup = BeautifulSoup(html, 'html.parser') 

    href_clayful_id = soup.select('.list-type2 > ul > li > .item-type1 > a')


    for i in href_clayful_id:
        href_data.append({
            "clay_ful_id" : i.get('href').split('=')[-1]
        })

    img = soup.select('.list-type2 > ul > li > .item-type1 > a > div.img > img' )


    for i in img:
        src = i.get('src').split('v1')[0]
        image_name = i.get('src').split('/')[-1]

        src_data.append({
            "image_name" : i.get('src').split('/')[-1]
        })

 
        full_src = src + 'v1/' + quote_plus(image_name)
        print('전체 URL', full_src)
        urlretrieve(full_src, './images/' + image_name)



for i, j in zip(href_data, src_data):
    json_data.append({
        "clay_ful_id" : i['clay_ful_id'],
        "image_path" : j['image_name']
    })

with open(path, 'w',  encoding='UTF-8-sig') as f:
    json.dump(json_data, f, ensure_ascii = False, indent=4)
        


'''
import re
from urllib.parse import quote_plus

# url = "https://cdn.clayful.io/stores/ACPJSG44NLXH.XB59URB7CVKC/images/3Z94YZNGG64L/v1/썸네일.png"
url = "https://cdn.clayful.io/stores/ACPJSG44NLXH.XB59URB7CVKC/images/KFMGRGD8GPZB/v1/썸네일_1.png"
hangul = re.compile('[ㄱ-ㅎ|가-힣+]')

refined_url = ""
hangul_flag = False
temp_word = ""
for word in url:
    if hangul.match(word):
        temp_word += word
        hangul_flag = True
    else:
        if hangul_flag:
            hangul_flag = False
            refined_url += quote_plus(temp_word)
            temp_word = ""
            refined_url += word
        else:
            refined_url += word

print(refined_url)
'''