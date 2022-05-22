# Japanese French Toast IT2555 Application Security Project

**PEM Group:** SF2102

### Team members:

- [211973E]  Jabriel Seah **-(Leader)-**
- [210162M]  Clarence Koh
- [214242Q]  Royston Loo
- [214299H]  Fong Chung Wai

## Project Description

Our web application is an online bookstore. It provides the service of purchasing books online. It allows users to create accounts so that their purchase history, email, and credit card details are kept. There are admin accounts used for managing books and users. Our web application is written in Python using Flask. Thus, it also uses Jinja templates.

Under this circumstance, We as creative, enthusiastic and innovative programmers do not want to see the city of books die down and become a figment left behind in Singapore history books. Therefore we have decided to help store owners transition digitally in this Covid-19 affected world as well as create solutions that meet the needs of the business as well as the customers patronising these shop owners' stores.

**Python Version:** 3.8 and above required.

## Required libraries for project

**1. Flask** | `pip install flask `  
**2. Flask-Mail** | `pip install flask-mail`  
**3. email-validator** | `pip install email-validator`  
**4. WTForms** | `pip install wtforms`  
**5. Flask-WTF** | `pip install flask-wtf`  
**6. argon2-cffi** | `pip install argon2-cffi`  
**7. stripe** | `pip install stripe`  
**8. Pillow** | `pip install pillow`  

You may install using: `pip3 install -r requirements.txt`

## Task Allocation

**Clarence Koh**
- (A5) Broken Access Control
- (A3) Sensitive Data Exposure

**Royston Loo**
- (API4) Lack of Resources & Rate Limiting
- (A2) Broken Authentication

**Fong Chung Wai**
- (A1) Injection
- (API5) Broken Function Level Authorization

**Jabriel Seah**
- (A7) Cross Site Scripting
- (A8) Insecure Deserialisation
