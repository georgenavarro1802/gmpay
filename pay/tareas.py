import threading
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from pagacompa.settings import EMAIL_HOST_USER


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, replyto=None):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.replyto = replyto
        threading.Thread.__init__(self)

    def run (self):
        try:
            headers = {}
            if self.replyto:
                headers['Reply-To'] = self.replyto
            msg = EmailMessage(self.subject, self.html_content, EMAIL_HOST_USER, self.recipient_list, headers=headers)
            msg.content_subtype = "html"
            msg.send()
        except:
            pass


def send_html_mail(subject, html_template, data, recipient_list, replyto=None):

    template = get_template(html_template)
    d = Context(data)
    html_content = template.render(d)

    EmailThread(subject, html_content, recipient_list, replyto).start()