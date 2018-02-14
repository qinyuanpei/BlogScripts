# -*- coding: utf-8 -*-

import json
import hashlib
import urllib
import random
import requests

appid = '20151113000005349'
secretKey = 'osubCEzlGjzvw8qdQc41'

class BaiduTranslate:

    def __init__(self,appid,secretKey):
        self.appid = appid
        self.secretKey = secretKey

    def translate(self,question,fromLang='zh',toLang='en'):
        salt = random.randint(32768, 65536)
        signature = self.getSignature(
            self.appid,
            question,
            salt,
            self.secretKey
        )
        
        try:
            reqURL = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
            data = {
                'q':question,
                'from':fromLang,
                'to':toLang,
                'appid':self.appid,
                'salt':str(salt),
                'sign':signature
            }
                
            resp = requests.get(reqURL,params=data)
            return json.loads(resp.text)['trans_result'][0]['dst']
        except Exception as e:
            print(str(e))
            return None

    def getSignature(self,appid,question,salt,secretKey):
        signature = appid + question + str(salt) + secretKey
        md = hashlib.md5()
        md.update(signature.encode('utf-8'))
        return md.hexdigest()
 
if(__name__ == '__main__'):
    translateClient = BaiduTranslate(appid,secretKey)
    print(translateClient.translate('在平凡中蜕变，我的2014'))
