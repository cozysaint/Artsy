import csv
import requests
import os
from PIL import Image

# 클라이언트 ID와 시크릿 키
client_id = ''
client_secret = ''

# Xapp 토큰을 얻기 위한 엔드포인트
token_url = 'https://api.artsy.net/api/tokens/xapp_token'

# 함수01: 토큰 가져오기
def token():

    # POST 요청을 보낼 데이터
    data = {
        'client_id': client_id,
        'client_secret': client_secret
    }

    # Xapp 토큰 요청 보내기
    response = requests.post(token_url, data=data)

    if response.status_code == 201:
        # 응답 데이터에서 토큰 추출하고 반환
        response_data = response.json()
        xapp_token = response_data['token']
        print("xapp_token: success")
        return xapp_token
    else: # 토큰을 받지 못하면 None 반환
        print("Failed to obtain xapp_token with status code:", response.status_code)
        return None

# 함수 02: 정보 요청
def req():

    # 이미지를 저장할 폴더 생성
    image_folder = 'images'
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    # CSV 파일 이름
    csv_filename = 'artworks.csv'

    # API 엔드포인트: artworks
    url = 'https://api.artsy.net/api/artworks'
    next_page_url = url
    headers = {'X-XAPP-Token': xapp_token}

    # 작품 정보 요청
    for _ in range(100): # n번 반복
        response = requests.get(next_page_url, headers=headers)

        if response.status_code == 200: 
            data = response.json() # 응답을 json으로 data에 저장
            next_page_url = data['_links']['next']['href'] if 'next' in data['_links'] else None
            # 작품 정보를 CSV 파일에 추가
            with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:  # utf-8-sig로 변경
                writer = csv.DictWriter(csvfile, fieldnames=['Title', 'Category', 'Medium', 'Date', 'Width', 'Height', 'Width_pixel', 'Height_pixel', 'Link'])
                if csvfile.tell() == 0:  # 파일이 비어 있는 경우에만 헤더 추가
                    writer.writeheader()
                for artwork in data['_embedded']['artworks']:
                    title = artwork['title']
                    category = artwork['category']
                    medium = artwork['medium']
                    date = artwork['date']
                    width = artwork['dimensions']['cm']['width']
                    height = artwork['dimensions']['cm']['height']
                    self_link = artwork['_links']['permalink']['href']
                    # 이미지 URL 가져오기, 이미지가 없다면 'none'으로 표기
                    image_url = artwork['_links']['image']['href'].format(image_version='large') if 'image' in artwork['_links'] else None  
                    if image_url:
                        # 이미지 다운로드
                        image_response = requests.get(image_url)
                        image_filename = os.path.join(image_folder, f"{title}.jpg")
                        with open(image_filename, 'wb') as image_file:
                            image_file.write(image_response.content)
                        # 이미지 정보 가져오기
                        image = Image.open(image_filename)
                        width_pixel, height_pixel = image.size
                        # 작품 정보를 CSV 파일에 추가
                        writer.writerow({'Title': title, 'Category': category, 'Medium': medium, 'Date': date, 'Link': self_link, 'Width_pixel': width_pixel, 'Height_pixel': height_pixel, 'Width': width, 'Height': height})
                    else:
                        # 이미지 URL이 없는 경우, 다음 작품으로 넘어감
                        continue
            print("Page processed:", next_page_url)
        else:
            print("Failed to get artworks with status code:", response.status_code)
            break

    print("Artworks data has been saved to", csv_filename)


# 토큰 입력
xapp_token = token()

# 메인 함수 실행
req()
