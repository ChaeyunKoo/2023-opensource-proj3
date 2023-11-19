from flask import Flask, request, render_template
import requests
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import folium

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_bus_info', methods=['POST'])
def get_bus_info():
    bus_route_id = request.form['bus_route_id']
    start_ord = request.form['start_ord']
    end_ord = request.form['end_ord']

    # 서비스 키를 URL 안전한 형태로 인코딩
    service_key = unquote('') #보안 상의 이유로 서비스 키 삭제
    url = 'http://ws.bus.go.kr/api/rest/buspos/getBusPosByRouteSt'
    params = {
        'serviceKey': service_key,
        'busRouteId': bus_route_id,
        'startOrd': start_ord,
        'endOrd': end_ord,
    }

    response = requests.get(url, params=params)

    # XML 파싱
    root = ET.fromstring(response.content)

    # 필요한 정보 추출
    bus_info = {
        'plainNo': root.find('.//plainNo').text,
        'tmX': float(root.find('.//tmX').text),
        'tmY': float(root.find('.//tmY').text),
        'routeId': root.find('.//routeId').text
    }

    # 지도에 표시
    map_center = [bus_info['tmY'], bus_info['tmX']]
    map = folium.Map(location=map_center, zoom_start=15)
    folium.Marker(location=map_center, popup=f"Bus Number: {bus_info['plainNo']}").add_to(map)

    # 지도를 HTML로 변환하여 템플릿에 전달
    map_html = map.get_root().render()

    return render_template('bus_info_with_map.html', bus_info=bus_info, map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)
