import requests
from urllib.request import urlretrieve
from urllib.parse import quote

from urllib.parse import quote_plus

from bs4 import BeautifulSoup



for i in range(1, 52):
    url = f"https://myrobotsolution.com/store/?page={i}&"
    response = requests.get(url) 

    print(response.status_code)

    html = response.text 
    soup = BeautifulSoup(html, 'html.parser') 



    img = soup.select('.item-type1 > a > div.img > img' )

    for i in img:
        src = i.get('src').split('v1')[0]
        src_qutoe = i.get('src').split('/')[-1]
        print(src)
        print(src_qutoe)

        full_src = src + 'v1/' + quote_plus(src_qutoe)
        print('전체 URL', full_src)
        urlretrieve(full_src, './imags/' + src_qutoe)



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