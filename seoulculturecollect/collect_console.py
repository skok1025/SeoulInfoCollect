import json
import os
import click
from datetime import datetime

import requests
import xmltodict

from seoulculturecollect import Console

class ConsoleCollect(Console):
    def main(self, input_area_code):
        if input_area_code:
            area_code_list = [input_area_code]
        else:
            area_code_dict = json.load(open('resource/area_code.json', 'r', encoding='utf-8'))
            area_code_list = area_code_dict.keys()

        all_event_list = []

        for area_code in area_code_list:
            print(area_code + '에 대한 데이터 수집 시작')
            call_url = f'http://openapi.seoul.go.kr:8088/{os.environ["SEOUL_API_KEY"]}/xml/citydata/1/5/{area_code}'
            response = requests.get(call_url)

            if response.status_code != 200:
                print(f'{area_code}에 대한 데이터 수집 실패')
                continue

            response_dict = xmltodict.parse(response.text)

            try:
                EVENT_STTS = response_dict.get('SeoulRtd.citydata', {}).get('CITYDATA', {}).get('EVENT_STTS', {}).get('EVENT_STTS', None)
            except AttributeError:
                EVENT_STTS = None

            if type(EVENT_STTS) == dict:
                EVENT_STTS['EVENT_AREA_CODE'] = area_code
                EVENT_STTS['EVENT_START_DATE'], EVENT_STTS['EVENT_END_DATE'] = EVENT_STTS['EVENT_PERIOD'].split('~')
                all_event_list.append(EVENT_STTS)
            elif type(EVENT_STTS) == list:
                for event in EVENT_STTS:
                    event['EVENT_AREA_CODE'] = area_code
                    event['EVENT_START_DATE'], event['EVENT_END_DATE'] = event['EVENT_PERIOD'].split('~')
                    all_event_list.append(event)

        result = {
            'collect_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(all_event_list),
            'all_event_list': all_event_list
        }

        collect_file_name = f'/shkim30/resources/{input_area_code}_event_list.json' if input_area_code else '/shkim30/resources/event_list.json'

        # 파일이 이미 존재하면 삭제
        if os.path.exists(collect_file_name):
            try:
                os.remove(collect_file_name)
                print(f'{collect_file_name} 파일을 삭제하고 새로운 데이터로 덮어씌웁니다.')
            except OSError as e:
                print(f'Error: {collect_file_name} : {e.strerror}')

        with open(collect_file_name, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

@click.command()
@click.option("--area_code", help="지역코드")
def cli(area_code):
    console = ConsoleCollect()
    console.main(input_area_code=area_code)

if __name__ == '__main__':
    cli()
