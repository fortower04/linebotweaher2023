

#ncuever



# 載入需要的模組
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage
import requests


app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('IwKEndDponiPD0/c94LMHhJyPyo+AlApKL/t3olCXu9EZ7znDi23+8q+4hZkCO+IUigUP36yBk139ReOvUgSuuYxHOPL28t2EkRTEWPMaCGQo2iDk+K8L2GZOQeUzAwOjBalOzdGltQy33Iq/ig9kwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a939e605879fd1df6cba21d17ea0a23b')

# 接收 LINE 的資訊
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 報天氣
@handler.add(MessageEvent, message=TextMessage)
def replytouser(event):
    if event.message.text == "今天彰師大天氣如何":
        replyMessage1 = weather()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=replyMessage1))

    if event.message.text == "今天空氣品質如何":
        replyMessage2 = aqidata()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=replyMessage2))

    if event.message.text == "問題與回饋":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='你說我在聽!\n會盡快回覆您的(๑•̀ㅂ•́)و✧'))

    if event.message.text == "想知道最近6小時的天氣預報":
        replyMessage3 = forecast()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=replyMessage3))
    if event.message.text == "想看全台最新的雷達回波圖":
        radar_img=radar()
        replyMessage5 = ImageSendMessage(
            original_content_url=radar_img,
            preview_image_url=radar_img )
        line_bot_api.reply_message(event.reply_token, replyMessage5)
   

#氣象觀測
def weather():
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWB-32B029F3-FC1B-421E-B23E-85AEA770BF4D&locationName=%E5%BD%B0%E5%B8%AB%E5%A4%A7"
    response = requests.get(url)
    allData = response.json()
    time=allData['records']['location'][0]['time']['obsTime']
    weatherElement= allData['records']['location'][0]['weatherElement']
    temp=weatherElement[3]['elementValue']
    htemp=weatherElement[14]['elementValue']
    rainfall=weatherElement[6]['elementValue']


    if temp=='-99':
        temp='無資料'
    else:
        temp=int(round((float(temp)),0))
    if htemp=='-99':
        htemp='無資料'
    else:
        htemp=int(round((float(htemp)),0))
    if rainfall=='-99':
        rainfall='無資料'
    else:
        rainfall=float(rainfall)

    weathertext='觀測時間:'+'\n'+time+"\n"+'\n'+'現在氣溫:'+str(temp)+'\n'+"今日最高溫:"+str(htemp)+'\n'+"今日累積雨量:"+str(rainfall)+'mm\n'+"現在天氣狀況:"+weatherElement[20]['elementValue']

    if temp =='無資料' or htemp =='無資料'  or rainfall =='無資料' : 
        sug1='\n✧柴語錄:\n測站資料有問題導致資訊不完整 \n請稍後查詢(ಥ﹏ಥ)'
    elif temp  >= 30 and rainfall ==0 :
        sug1='\n✧柴語錄:\n夏日炎炎!記得防曬、補充水分\n柴在家吹電扇避暑(๑•́ ₃ •̀๑)'
    elif 20<=temp  < 30 and rainfall  == 0 :
        sug1='\n✧柴語錄:\n適合戶外活動的舒適天氣\n柴在公園開心玩耍ヽ(✿ﾟ▽ﾟ)ノ'
    elif temp  < 20 and rainfall <= 0:
        sug1='\n✧柴語錄:\n涼意襲來!多加保暖，別冷著囉\n柴躲在溫暖的窩裡ლ(╹◡╹ლ)'
    elif rainfall > 0 :
        sug1='\n✧柴語錄:\n今天有下雨哦~請攜帶雨具\n注意行車安全!\n柴趴著看窗外的雨(｡◕∀◕｡)'
    else:
        sug1='✧柴關心您✧'
 
    
   

    weather=weathertext+"\n"+sug1
    return(weather)

#空氣品質觀測
def aqidata():
    url = "https://data.epa.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON"
    response = requests.get(url)
    allData = response.json()

    aqi= allData['records'][32]
    
    aqitext="觀測時間:"+'\n'+aqi["publishtime"]+'\n'+"\n"+"AQI空氣品質指標:"+aqi['aqi']+"\n"+"狀態:"+aqi['status']+"\n"+"PM10 懸浮微粒:"+aqi["pm10"] +"\n"+"PM2.5 細懸浮微粒:"+aqi["pm2.5"]+"\n"+"二氧化硫濃度:"+aqi["so2"]+"\n"+"二氧化氮濃度:"+aqi["no2"]
    
    sug=" "

    if '良好' not in aqi['status']:
        sug='\n✧柴語錄:\n空氣灰灰~戴好口罩才有乾淨空氣喔!\n柴不出門 在家躲空汙(๑•́ ₃ •̀๑)'
    else:
        sug='\n✧柴語錄:\n今天空氣不錯唷\n可以出外走走呼吸新鮮空氣\n柴大口吸氣吐氣ヽ(✿ﾟ▽ﾟ)ノ'

    aqidata=aqitext+"\n"+sug
    return(aqidata)

#天氣預報
def forecast():
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-017?Authorization=CWB-32B029F3-FC1B-421E-B23E-85AEA770BF4D&locationName=%E5%BD%B0%E5%8C%96%E5%B8%82"
    response = requests.get(url)
    allData = response.json()
    weatherElement= allData['records']['locations'][0]['location'][0]['weatherElement']
    
    time='預報時間區間:'+weatherElement[6]['time'][0]['startTime']+"-"+weatherElement[6]['time'][1]['endTime'][11:19]

    if float (weatherElement[3]['time'][0]['elementValue'][0]['value']) <= float(weatherElement[3]['time'][2]['elementValue'][0]['value']):

        temp='溫度:'+weatherElement[3]['time'][0]['elementValue'][0]['value']+" ~ "+weatherElement[3]['time'][2]['elementValue'][0]['value']+' °C'
    else:
        temp='溫度:'+weatherElement[3]['time'][2]['elementValue'][0]['value']+" ~ "+weatherElement[3]['time'][0]['elementValue'][0]['value']+' °C'

    if float (weatherElement[2]['time'][0]['elementValue'][0]['value']) <= float(weatherElement[2]['time'][2]['elementValue'][0]['value']):

        atemp='體感溫度:'+weatherElement[2]['time'][0]['elementValue'][0]['value']+" ~ "+weatherElement[2]['time'][2]['elementValue'][0]['value']+' °C'
    else:
        atemp='體感溫度:'+weatherElement[2]['time'][2]['elementValue'][0]['value']+" ~ "+weatherElement[2]['time'][0]['elementValue'][0]['value']+' °C'

    pop6='降雨機率:'+weatherElement[7]['time'][0]['elementValue'][0]['value']+" %"
    situation="天氣狀況:"+weatherElement[1]['time'][0]['elementValue'][0]['value']

    other=weatherElement[6]['time'][0]['elementValue'][0]['value']
    otherst=other.split("。")
    otherst[4]=otherst[4].replace("(","\n(")
    detail="✧或許你還想知道:"+"\n舒適度 "+otherst[3]+"\n"+otherst[4]+"\n"+otherst[5]


    
    forecast=time+"\n"+"\n"+temp+"\n"+atemp+"\n"+pop6+"\n"+situation+"\n\n"+detail
    return(forecast)
#雷達回波圖
def radar():
    url='https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/O-A0058-003?Authorization=rdec-key-123-45678-011121314&format=JSON'
    response = requests.get(url)
    allData = response.json()
    radar=allData['cwbopendata']['dataset']['resource']['uri']
    
   
    return(radar)


        

if __name__ == "__main__":
    app.run()






