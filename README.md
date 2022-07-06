# IT2555 Application Security Project

![Japanese French Toast](https://user-images.githubusercontent.com/65378401/169692179-96d98787-600f-40b6-9917-d773e11ccb44.jpg)

> Providing quality services since 2022, better than Coffee & Waffles Co.

## Group Details

### Japanese French Toast

**PEM Group:** SF2102  
**Group Name:** Japanese French Toast  
**Why the name:** I dunno?  
**Where did you get the image:** I found them [here](https://iamafoodblog.com/extra-fluffy-super-soft-and-custard-y-japanese-style-tamagoyaki-french-toast/) and made some edits.

**Team members:**
- [211973E]  Jabriel Seah **(Leader)**
- [210162M]  Clarence Koh
- [214242Q]  Royston Loo
- [214299H]  Fong Chung Wai

## Project Description

Our web application is an online bookstore. It provides the service of purchasing books online. It allows users to create accounts so that their purchase history, email, and credit card details are kept. There are admin accounts used for managing books and users. Our web application is written in Python using Flask. Thus, it also uses Jinja templates.

**Python Version:** 3.8 and above required.

## Required libraries for project

**1. Flask** | `pip install flask `  
**2. Flask-Mail** | `pip install flask-mail`  
**3. Flask-Limiter** | `pip install Flask-Limiter`  
**4. email-validator** | `pip install email-validator`  
**5. WTForms** | `pip install wtforms`  
**6. Flask-WTF** | `pip install flask-wtf`  
**7. argon2-cffi** | `pip install argon2-cffi`  
**8. stripe** | `pip install stripe`  
**9. Pillow** | `pip install pillow`  
**10. flask-expects-json** | `pip install flask-expects-json`
**11. google-api-python-client** | `pip install google-api-python-client`  
**12. google-auth-httplib2** | `pip install google-auth-httplib2`  
**13. google-auth-oauthlib** | `pip install google-auth-oauthlib`  
**14. google-auth** | `pip install google-auth`  
**15. pyotp** | `pip install pyotp`

You may install all using: `pip3 install -r requirements.txt`

## Task Allocation

**Clarence Koh**
- (A3) Sensitive Data Exposure
- (A5) Broken Access Control

**Royston Loo**
- (A2) Broken Authentication
- (API4) Lack of Resources & Rate Limiting

**Fong Chung Wai**
- (A1) Injection
- (API5) Broken Function Level Authorization

**Jabriel Seah**
- (A7) Cross Site Scripting
- (A8) Insecure Deserialisation
