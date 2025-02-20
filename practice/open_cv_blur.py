import cv2


def update_blur(x):
    # 트랙바에서 가져온 값을 홀수로 보정
    ksize = cv2.getTrackbarPos("Kernel", "Blurred Image")
    if ksize % 2 == 0:
        ksize += 1
    # 블러 적용
    blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
    cv2.imshow("Blurred Image", blurred)


# 이미지 읽기 및 예외 처리
image = cv2.imread("input.jpg")
if image is None:
    print("이미지를 불러오지 못했습니다.")
    exit()

cv2.namedWindow("Blurred Image")
# 트랙바 생성: 초기값 15, 최대값 51 (원하는 범위에 따라 조절)
cv2.createTrackbar("Kernel", "Blurred Image", 15, 51, update_blur)

# 초기 블러 처리
blurred = cv2.GaussianBlur(image, (15, 15), 0)
cv2.imshow("Blurred Image", blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()
