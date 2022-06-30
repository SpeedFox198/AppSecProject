from __init__ import app
from itsdangerous import TimedJSONWebSignatureSerializer as jsonSerializer
from flask_mail import Message

# functions for reset password process via email
# helpful resources: https://stackoverflow.com/questions/56699115/timedjsonwebsignatureserializer-vs-urlsafetimedserializer-when-should-i-use-wha
# TimedJsonWebSignatureSerializer uses SHA512 by default
def get_reset_token(emailKey, expires_sec=600): # 10 mins
    s = jsonSerializer(app.config["SECRET_KEY"], expires_sec)
    return s.dumps({"user_id": emailKey.get_user_id()}).decode("utf-8")

def verify_reset_token(token):
    s = jsonSerializer(app.config["SECRET_KEY"])
    # try and except as if the token is invalid, it will raise an exception
    try:
        userID = s.loads(token)["user_id"] # get the token but if the token is invalid or expired, it will raise an exception
        return userID
    except:
        return None

def send_reset_email(email, emailKey):
    token = get_reset_token(emailKey)
    message = Message("[CourseFinity] Password Reset Request", sender="CourseFinity123@gmail.com", recipients=[email])
    message.html = f"""<p>Hello,</p>

<p>To reset your password, visit the following link:<br>
<a href="{url_for("resetPassword", token=token, _external=True)}" target="_blank">{url_for("resetPassword", token=token, _external=True)}</a></p>

<p>Do note that this link will expire in 10 minutes.<br>
If you did not make this request, please disregard this email.</p>

<p>Sincerely,<br>
<b>CourseFinity Team</b></p>
"""
    mail.send(message)

def send_email_change_notification(oldEmail, newEmail):
    message = Message("[CourseFinity] Email Changed", sender="CourseFinity123@gmail.com", recipients=[oldEmail])
    message.html = f"""<p>Hello,</p>

<p>You have recently changed your email from {oldEmail} to {newEmail}</p>

<p>If you did not make this change, your account may have been compromised.<br>
Please contact us if you require assistance with account recovery by making a support ticket in the <a href="{url_for("contactUs", _external=True)} target="_blank">contact us page</a>, or contacting support@coursefinity.com</p>

<p>Sincerely,<br>
<b>CourseFinity Team</b></p>
"""
    mail.send(message)

def send_password_change_notification(email):
    message = Message("[CourseFinity] Password Changed", sender="CourseFinity123@gmail.com", recipients=[email])
    message.html = f"""<p>Hello,</p>

<p>You have recently changed your password.</p>

<p>If you did not make this change, your account may have been compromised.<br>
Please contact us if you require assistance with account recovery by making a support ticket in the <a href="{url_for("contactUs", _external=True)} target="_blank">contact us page</a>, or contacting support@coursefinity.com</p>

<p>Sincerely,<br>
<b>CourseFinity Team</b></p>
"""
    mail.send(message)

# useful notes for verifying emails: https://www.chargebee.com/blog/avoid-friction-trial-sign-process/
# URLSafeTimedSerializer uses SHA1 by default
def generate_verify_email_token(userID, expires_sec=86400): # 1 day
    s = jsonSerializer(app.config["SECRET_KEY"], expires_sec)
    return s.dumps({"user_id": userID}).decode("utf-8")

def verify_email_token(token):
    s = jsonSerializer(app.config["SECRET_KEY"])
    try:
        userID = s.loads(token)["user_id"] # get the token but if the token is invalid or expired, it will raise an exception
        return userID
    except:
        return None

def send_verify_email(email, userID):
    token = generate_verify_email_token(userID)
    message = Message("[CourseFinity] Welcome to CourseFinity!", sender="CourseFinity123@gmail.com", recipients=[email])
    message.html = f"""<p>Hello,</p>

<p>Welcome to CourseFinity!<br>
We would like you to verify your email for verifications purposes.</p>

<p>Please click on this link to verify your email:<br>
<a href="{url_for("verifyEmailToken", token=token, _external=True)}" target="_blank">{url_for("verifyEmailToken", token=token, _external=True)}</a></p>

<p>Please contact us if you have any questions or concerns. Our customer support can be reached by making a support ticket in the <a href="{url_for("contactUs", _external=True)} target="_blank">contact us page</a>, or contacting support@coursefinity.com</p>

<p>Thank you.</p>

<p>Sincerely,<br>
<b>CourseFinity Team</b></p>
"""
    mail.send(message)

def send_verify_changed_email(email, oldEmail, userID):
    token = generate_verify_email_token(userID)
    message = Message("[CourseFinity] Verify Updated Email", sender="CourseFinity123@gmail.com", recipients=[email])
    message.html = f"""<p>Hello,</p>

<p>You have recently updated your email from {oldEmail} to {email}<br>
We would like you to verify your email for verifications purposes.</p>

<p>Please click on this link to verify your email:<br>
<a href="{url_for("verifyEmailToken", token=token, _external=True)}" target="_blank">{url_for("verifyEmailToken", token=token, _external=True)}</a></p>

<p>Please contact us if you have any questions or concerns. Our customer support can be reached by making a support ticket in the <a href="{url_for("contactUs", _external=True)} target="_blank">contact us page</a>, or contacting support@coursefinity.com</p>

<p>Thank you.</p>

<p>Sincerely,<br>
<b>CourseFinity Team</b></p>
"""
    mail.send(message)

def send_another_verify_email(email, userID):
    token = generate_verify_email_token(userID)
    message = Message("[CourseFinity] Verify Email", sender="CourseFinity123@gmail.com", recipients=[email])
    message.html = f"""<p>Hello,</p>

<p>We would like you to verify your email for verifications purposes.</p>

<p>Please click on this link to verify your email:<br>
<a href="{url_for("verifyEmailToken", token=token, _external=True)}" target="_blank">{url_for("verifyEmailToken", token=token, _external=True)}</a></p>

<p>Please contact us if you have any questions or concerns. Our customer support can be reached by making a support ticket in the <a href="{url_for("contactUs", _external=True)} target="_blank">contact us page</a>, or contacting support@coursefinity.com</p>

<p>Thank you.</p>

<p>Sincerely,<br>
<b>CourseFinity Team</b></p>
"""
    mail.send(message)