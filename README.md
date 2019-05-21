# pycontw_sender

議程組簡單的自動寄信腳本


## 修改 .env 檔案

.env 共有以下四個變數要更改

1. ACCOUNT= # Google 帳號
2. PASSWORD= # Google 密碼
3. SENDER= # 完整信箱帳號地址
4. CC_MAIL= # cc 的信箱，用 `,` 分隔


## 從審查系統轉出錄取者資訊 csv 檔案

請到`審查系統`匯出錄取者的訊息為 csv 檔案。小技巧: 先更新後台錄取名單再一次匯出。


## 修改信件內容

pg_sender.py 內共有以下五個變數要更改

1. years = '' # 年度
2. talk_proposal = '' # 審查系統匯出檔案
3. doodle = '' # doodle 調查網址
4. registration_date = '' # 註冊最後期限
5. question_date = '' # 提問最後期限


## Google 變更低安全性應用程式存取帳戶

Google 因為安全性問題，因此不允許應用程式去存取帳戶，因此如果要透過 Google mail server 寄信要先到[網址](https://support.google.com/accounts/answer/6010255?authuser=1&p=lsa_blocked&hl=zh-Hant&authuser=1&visit_id=636940144218553665-4017599695&rd=1)根據步驟變更。

**使用後要記得改回原本高權限**。


執行程式跳出以下錯誤，就是沒有變更權限:
```
smtplib.SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted. Learn more at\n5.7.8 http://support.google.com/mail/bin/answer.py?answer=14257 g66sm2224117qgf.37 - gsmtp')
```

簡單測試方法:
```
import smtplib

smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo()
smtpserver.login('{account}', '{password}')
```

收到以下訊息代表變更成功:
```
(235, '2.7.0 Accepted')
```

再次提醒，**使用後要記得改回原本高權限**。
