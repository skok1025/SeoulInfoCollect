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

            # xml to dict
            response_dict = xmltodict.parse(response.text)

            try:
                EVENT_STTS = response_dict.get('SeoulRtd.citydata', {}).get('CITYDATA', {}).get('EVENT_STTS', {}).get('EVENT_STTS', None)
            except AttributeError:
                EVENT_STTS = None  # 또는 다른 적절한 기본값 할당

            if type(EVENT_STTS) == dict:
                EVENT_STTS['EVENT_AREA_CODE'] = area_code
                EVENT_STTS['EVENT_START_DATE'], EVENT_STTS['EVENT_END_DATE'] = EVENT_STTS['EVENT_PERIOD'].split('~')

                all_event_list.append(EVENT_STTS)
            elif type(EVENT_STTS) == list:
                for event in EVENT_STTS:
                    event['EVENT_AREA_CODE'] = area_code
                    event['EVENT_START_DATE'], event['EVENT_END_DATE'] = event['EVENT_PERIOD'].split('~')

                    all_event_list.append(event)
            else:
                pass


        result = {
            'collect_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(all_event_list),
            'all_event_list': all_event_list
        }

        # 3항연산자
        collect_file_name = f'resource/{input_area_code}_event_list.json' if input_area_code else 'resource/event_list.json'

        # json 파일로 저장 (* 이미 파일이 있으면 덮어쓰기
        with open(collect_file_name, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)


@click.command()
@click.option("--area_code", help="지역코드")
def cli(area_code):
    console = ConsoleCollect()
    console.main(input_area_code=area_code)


if __name__ == '__main__':
    cli()


