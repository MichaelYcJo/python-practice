import requests, os
from django.conf import settings

# API인증으로 토큰 가져오기
def get_token():
    '''
    #settings 값을 제대로 못받아오는 오류 발생 environ으로 해야할까?
    access_data = {
        'imp_key':settings.IAMPORT_KEY,
        'imp_secret':settings.IAMPORT_SECRET
    }
    '''
    access_data = {
        'imp_key': os.environ['IAMPORT_KEY'],
        'imp_secret': os.environ['IAMPORT_SECRET_KEY']
    }

    url="https://api.iamport.kr/users/getToken"
    req = requests.post(url, data=access_data)

    #받아온 req를 json()으로 변환
    access_res = req.json()
    if access_res['code'] is 0:
        return access_res['response']['access_token']
    else:
        return None

# 어떤 order_id로 얼마만큼의 금액을 요청할것인가?
def payments_prepare(order_id, amount, *args, **kwargs):
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid':order_id,
            'amount':amount
        }
        url = "https://api.iamport.kr/payments/prepare"
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
    else:
        raise ValueError("토큰 오류")



#결제가 된 후에 요청 온 주문번호와 총량만큼 결제가 되었는지를 확인하기 위함
def find_transaction(order_id, *args, **kwargs):
    access_token = get_token()
    if access_token:
        url = "https://api.iamport.kr/payments/find/"+order_id
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url, headers=headers)
        res = req.json()
        if res['code'] == 0:
            context = {
                'imp_id':res['response']['imp_uid'],
                'merchant_order_id':res['response']['merchant_uid'],
                'amount':res['response']['amount'],
                'status':res['response']['status'],
                'type':res['response']['pay_method'],
                'receipt_url':res['response']['receipt_url']
            }
            return context
        else:
            return None
    else:
        raise ValueError("토큰 오류")