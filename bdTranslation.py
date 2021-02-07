import requests
import json
import sys
import re
import hashlib

api_url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
appid = "20210201000687318"
key = "nAJvVcla92p6qx7ooNPe"
failed_strings=[]

def requests_for_dst(paragraph, filename):  
    sign = appid+paragraph+"1435660288"+key
    sign = hashlib.md5(sign.encode("utf-8")).hexdigest()
    #区别en,zh构造请求参数  
    paramas = {  
            'q':paragraph,  
            'from':'en',  # 源语言
            'to':'zh',   # 目标语言
            'appid':appid,  
            'salt':1435660288,  
            "sign":sign,
            }  #翻译请求参数
    try:
        response = requests.get(api_url,params = paramas).content  
        content = str(response,encoding = "utf-8")  
        json_reads = json.loads(content)  
        result = json_reads['trans_result']
        with open(filename, "a+") as f1:
            for r in result:
                f1.write(r["dst"]+"\n")
    except Exception as e:
        failed_strings.append(paragraph)

with open("first_56.txt", "r+", encoding='utf-8') as f:
    input = f.read()
    input = re.split("([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|1000)\u3001", input)
    for i in input:
        if (i == ""):
            continue
        requests_for_dst(i, "first_56_out.txt")