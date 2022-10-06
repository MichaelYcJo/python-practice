import sys
import logging
from socket import AF_INET, SOCK_STREAM, socket

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/socket",
    responses={404: {"description": "Not found"}},
)


class RequestText(BaseModel):
    text :str



@router.post("/report")
async def tcp_client_socket(
    request_text: RequestText, server_type: Optional[str] = None
) -> str:

    print('서버타입', server_type)

    if server_type == 'stg':
        HOST = "127.0.0.1"
        PORT = 10001
    elif server_type == 'prod':
        HOST = "127.0.0.1"
        PORT = 10002
    else:
        HOST = "127.0.0.1"
        PORT = 10000

    BUF_SIZE = 1024
    ADDR = (HOST, PORT)

    print('확인확인', request_text)

    
    client_socket = socket(AF_INET, SOCK_STREAM)  # 서버에 접속하기 위한 소켓을 생성한다.


    try:
        client_socket.connect(ADDR)  # 서버에 접속을 시도한다.
        byte_num = client_socket.send(request_text.text.encode())  # 서버에 메시지 전달
        print("보낸 바이트 수 : ", byte_num)

        msg = client_socket.recv(BUF_SIZE)  # 서버로부터 응답받은 메시지 반환
        client_socket.close()

        result = msg.decode()


        return result

    except Exception as e:
        logging.error(f"[Socket] - 클라이언트 소켓 에러 :  {e}")
        sys.exit()



