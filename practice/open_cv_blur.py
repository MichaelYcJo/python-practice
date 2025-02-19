import cv2

# 이미지 읽기
image = cv2.imread("input.jpg")

# 이미지가 정상적으로 로드되었는지 확인
if image is None:
    print("이미지를 불러오지 못했습니다.")
    exit()

# 가우시안 블러 적용
# (15, 15)는 커널 사이즈로, 숫자가 클수록 더 많이 블러처리 됩니다.
# 마지막 인자는 표준편차로, 0을 주면 커널 사이즈에 따라 자동으로 계산됩니다.
blurred = cv2.GaussianBlur(image, (15, 15), 0)

# 결과 이미지 저장
cv2.imwrite("output.jpg", blurred)

# 결과 확인을 위한 창 띄우기 (선택 사항)
cv2.imshow("Blurred Image", blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()
