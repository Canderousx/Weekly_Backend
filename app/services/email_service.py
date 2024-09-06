

from flask import jsonify,current_app as app
from flask_mail import Message
from app.services import security_service,user_service
from app import mail

footer = ("\n\n\n\n\n This message has been auto-generated. Please don't respond.\n"
          "If you have any concerns, please contact our support team instead \n\n"
          "\n"
          "Have a good day!\n"
          "Weekly Team")


def send_email(subject,recipients,message):
    body = "Hello there! \n\n\n\n"+message+footer
    if not isinstance(recipients,list):
        recipients = [recipients]
    msg = Message(subject,
                  sender= app.config['MAIL_USERNAME'],
                  recipients=recipients,
                  body=body
                  )
    mail.send(msg)


def send_email_confirmation_mail(email):
    token = security_service.generate_email_confirmation_token(email)
    message = ("To confirm your Weekly account use the following link: \n"
               +security_service.front_url+"/emailConfirmation?token="+token)
    send_email("Weekly: Email Confirmation",email,message)


def send_password_recovery_email(email):
    if user_service.email_exists(email):
        token = security_service.generate_password_recovery_token(email=email)
        message = ("To reset your password use the following link. It expires within 30 minutes since sending \n"
                   + security_service.front_url + "/passwordRestoration?token=" + token)
        send_email("Weekly: Password Recovery", email, message)

    return jsonify({"message":"If your account exists you should receive recovery details on your email."}),200