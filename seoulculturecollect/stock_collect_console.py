import os
import click
from seoulculturecollect import Console
import requests
from bs4 import BeautifulSoup

class StockConsoleCollect(Console):
    def main(self, code):
        # S&P500
        s_p_500 = self.get_bs_obj(code="S&P500")

        # NASDAQ
        nasdaq = self.get_bs_obj(code="NASDAQ")

        # DOW
        dow = self.get_bs_obj(code="DOW")

        import redis

        r = redis.Redis(host='localhost', port=6379, db=0)

        r.hset('stock:S&P500', 'today_info', str(s_p_500['today_info']))
        r.hset('stock:S&P500', 'exday_info', str(s_p_500['exday_info']))
        r.hset('stock:S&P500', 'time_info', str(s_p_500['time_info']))

        r.hset('stock:NASDAQ', 'today_info', str(nasdaq['today_info']))
        r.hset('stock:NASDAQ', 'exday_info', str(nasdaq['exday_info']))
        r.hset('stock:NASDAQ', 'time_info', str(nasdaq['time_info']))

        r.hset('stock:DOW', 'today_info', str(dow['today_info']))
        r.hset('stock:DOW', 'exday_info', str(dow['exday_info']))
        r.hset('stock:DOW', 'time_info', str(dow['time_info']))


    def get_bs_obj(self, code):
        code_symbol_dict = {
            "S&P500": "SPI@SPX",
            "NASDAQ": "NAS@IXIC",
            "DOW": "DJI@DJI"
        }
        symbol = code_symbol_dict[code]
        url = "https://finance.naver.com/world/sise.naver?symbol=" + symbol
        result = requests.get(url)
        bs_obj = BeautifulSoup(result.content, "html.parser")

        return {
            "today_info": bs_obj.find("p", {"class":"no_today"}),
            "exday_info": bs_obj.find("p", {"class":"no_exday"}),
            "time_info": bs_obj.find("div", {"class":"group_h"}),
        }


@click.command()
@click.option("--code", help="code")
def cli(code):
    console = StockConsoleCollect()
    console.main(code=code)


if __name__ == '__main__':
    cli()