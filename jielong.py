from pypinyin import lazy_pinyin
import xlrd
import pymongo
import re
import random
from bs4 import BeautifulSoup  #引入爬虫库
import requests

clinet=pymongo.MongoClient("localhost",27017)
geographydb=clinet["geography"]
cities=geographydb["cities"]

#爬取百度百科地级市名称数据
def getcities(url,headers):
    page = requests.get(url, headers=headers)
    page.encoding = "utf-8"
    soup = BeautifulSoup(page.text, "lxml")
    tables = soup.select("table")
    cities_temp = []
    for i in range(0, 26):
        cities_temp += str(tables[i].get_text()).replace("、", "").replace(" ", "").replace("自治州","自治州市").replace("\n","").replace("省直辖县级行政单位","").replace("地区","地区市").split("市")[1:-1]
    exist_cities = [item["city"] for item in cities.find()]
    x = set(cities_temp)
    y = set(exist_cities)
    rest_of_cities = x-y
    return rest_of_cities

#创建mongodb数据库
def createdb():
    if cities.find():pass
    else:
        fname = "chengshi.xls"
        bk = xlrd.open_workbook(fname)
        sh = bk.sheet_by_name("name")
        for i in range(1, sh.nrows):
            data={
                "city":sh.cell_value(i,1),
                "pinyin":lazy_pinyin(sh.cell_value(i,1))[0]
            }
            cities.insert_one(data)

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
            "cookie": "BAIDUID=82D4DBE08CDD16CAA359C49AE975F7E1:FG=1; PSTM=1469097798; BIDUPSID=ABDEF9387BBD616245A6731FD6FF36BC; __cfduid=d326a2bcf008e239039e3be4a957ea6d71494856285; MCITY=-%3A; BDUSS=5oU0RySGs4bH5vOUxTamNWckpuSDZPV3VIMGVOeW9NUU5xbUlLTE9lT1R2N2hhQVFBQUFBJCQAAAAAAAAAAAEAAACfwwoOsKZfztLI3dLXwvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJMykVqTMpFaWU; pgv_pvi=3912264704; pgv_si=s9246819328; BDRCVFR[qST5E-G8bOc]=mk3SLVN4HKm; PSINO=6; H_PS_PSSID=1432_21106_22160; BDORZ=FFFB88E999055A3F8A630C64834BD6D0"
        }
        url = "https://baike.baidu.com/item/县级市"
        for item in getcities(url,headers):
            if item:
                data={
                    "city":item,
                    "pinyin":lazy_pinyin(item)[0]
                }
                cities.insert_one(data)
            else:pass

#搜索结果
def selectresult(str):
    str_pinyin=lazy_pinyin(str[-1])[0]
    if cities.find({"city":re.compile('^'+str[-1])},{"city":1}).count():
        result=cities.find({"city":re.compile('^'+str[-1])},{"city":1,"_id":0})
        row_num=random.randint(0,result.count()-1)
        print("搜索结果：",result[row_num]["city"])
    elif cities.find({"pinyin":str_pinyin},{"city":1,"_id":0}).count():
        result=cities.find({"pinyin":str_pinyin},{"city":1,"_id":0})
        row_num = random.randint(0, result.count() - 1)
        print("搜索结果：",result[row_num]["city"])
    else:
        print("查不到结果")
    validinput()

#数据有效性判断，开始程序
def validinput():
    str = input("请输入一个城市名：")
    if cities.find({"city":str}, {"city": 1}).count():
        selectresult(str)
    else:
        print("输入错误，请重新输入！")
        validinput()

createdb()
validinput()



