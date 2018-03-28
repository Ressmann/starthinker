###########################################################################
#
#  Copyright 2017 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

# http://stackoverflow.com/questions/25832631/download-attachments-from-gmail-using-gmail-api

import re
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from urllib2 import urlopen
from HTMLParser import HTMLParser
from apiclient import errors
from datetime import timedelta

from util.project import project
from util.auth import get_service
from util.regexp import parse_url, date_to_str
from util.storage import parse_filename

# ADD RETRY

def _retry(job, retries=10, wait=5):
  try:
    data = job.execute()
    return data
  except HttpError, e:
    if project.verbose: print 'ERROR', str(e)
    if e.resp.status in [403, 429, 500, 503]:
      if retries > 0:
        sleep(wait)
        if project.verbose: print 'RETRY', retries
        return _retry(job, retries - 1, wait * 2)
      elif json.loads(e.content)['error']['code'] == 409:
        return # already exists ( ignore )
    # raise all other errors
    raise


def _list_unique(seq):
  seen = set()
  seen_add = seen.add
  return [x for x in seq if not (x in seen or seen_add(x))]


def _get_subject(message):
  for header in message['payload']['headers']:
    if header.get('name', '') == 'Subject': return header['value']
  return ''


#def _get_snippet(message):
#  for header in message['payload']['headers']:
#    if header.get('name', '') == 'Sbippet': return header['value']
#  return ''


def _email_links(service, message, link_regexp, download=False):
  links = []
  html_parser = HTMLParser()
  link_filter = re.compile(r'%s' % link_regexp) if link_regexp else None

  try:
    for part in message['payload']['parts']:
      if 'data' in part['body']:
        data = part['body']['data']
        content = base64.urlsafe_b64decode(data.encode('UTF-8'))
        # plain text may be different than html
        if part['mimeType'] == 'text/plain': 
          links.extend(parse_url(content))
        # html needs to decode links
        elif part['mimeType'] == 'text/html': 
          links.extend(map(lambda link: html_parser.unescape(link), parse_url(content)))

  except errors.HttpError, error:
    print 'EMAIL LINK ERROR: %s' % error

  # remove duplicates
  links = _list_unique(links)

  # filter links
  if link_filter: links = [link for link in links if link_filter.match(link)]


  # for downloads convert links into files and data
  if download:
    for i, link in enumerate(links):
      try: links[i] = (parse_filename(link, url=True), BytesIO(urlopen(link).read()))
      except: 'ERROR: Unable To Download', link

  return links


def _email_attachments(service, message, attachment_regexp):
  attachments = []
  file_filter = re.compile(r'%s' % attachment_regexp) if attachment_regexp else None

  try:
    for part in message['payload']['parts']:
      if part['filename']:
        if 'data' in part['body']:
          data=part['body']['data']
        else:
          att_id=part['body']['attachmentId']
          att=_retry(service.users().messages().attachments().get(userId='me', messageId=message['id'], id=att_id))
          data=att['data']
        file_data = BytesIO(base64.urlsafe_b64decode(data.encode('UTF-8')))

        # filter regexp
        if not file_filter or file_filter.match(part['filename']): attachments.append((part['filename'], file_data))

  except errors.HttpError, e:
    print 'EMAIL ATTACHMENT ERROR:', str(e)

  return attachments


def _email_message(service, message, link_regexp, attachment_regexp, download=False):
  return {
    'subject':_get_subject(message),
    'snippet':message['snippet'],
    'links':_email_links(service, message, link_regexp, download),
    'attachments':_email_attachments(service, message, attachment_regexp),
  } 


def _email_find(service, email_from, email_to, date_min=None, date_max=None):
  query = 'from:%s AND to:%s' % (email_from, email_to)
  if date_min: query += ' AND after:%s' % date_to_str(date_min)
  if date_max: query += ' AND before:%s' % date_to_str(date_max + timedelta(days=1)) # make it inclusive
  if project.verbose: print 'EMAIL SEARCH:', query
  results = _retry(service.users().messages().list(userId='me', q=query))
  messages = results.get('messages', [])
  if project.verbose: print 'EMAILS FOUND:', len(messages)
  return messages


def get_email_attachments(auth, email_from, email_to, date_min, date_max, subject_regexp=None, attachment_regexp=None):
  if project.verbose: print 'GETTING EMAIL ATTACHMENTS'
  attachements = []
  service = get_service('gmail', 'v1', auth)
  messages = _email_find(service, email_from, email_to, date_min, date_max)
  subject_filter = re.compile(r'%s' % subject_regexp) if subject_regexp else None
  for message in messages:
    message = _retry(service.users().messages().get(userId='me', id=message['id']))
    if subject_filter is None or subject_filter.match(_get_subject(message)):
      attachements.extend(_email_attachments(service, message, attachment_regexp))
  return attachements


def get_email_links(auth, email_from, email_to, date_min, date_max, subject_regexp=None, link_regexp=None, download=False):
  if project.verbose: print 'GETTING EMAIL LINKS'
  links = []
  service = get_service('gmail', 'v1', auth)
  messages = _email_find(service, email_from, email_to, date_min, date_max)
  subject_filter = re.compile(r'%s' % subject_regexp) if subject_regexp else None
  for message in messages:
    message = _retry(service.users().messages().get(userId='me', id=message['id']))
    if subject_filter is None or subject_filter.match(_get_subject(message)):
      links.extend(_email_links(service, message, link_regexp, download))
  return links


def get_email_messages(auth, email_from, email_to, date_min, date_max, subject_regexp=None, link_regexp=None, attachment_regexp=None, download=False):
  if project.verbose: print 'GETTING EMAILS'
  emails = []
  service = get_service('gmail', 'v1', auth)
  messages = _email_find(service, email_from, email_to, date_min, date_max)
  subject_filter = re.compile(r'%s' % subject_regexp) if subject_regexp else None
  for message in messages:
    message = _retry(service.users().messages().get(userId='me', id=message['id']))
    if subject_filter is None or subject_filter.match(_get_subject(message)):
      emails.append(_email_message(service, message, link_regexp, attachment_regexp, download))
  return emails


def send_email(auth, email_to, email_from, email_cc, subject, text, html):
  if project.verbose: print 'Send email'
  
  service = get_service('gmail', 'v1', auth)
  message = MIMEMultipart('alternative')

  message['to'] = email_to
  message['cc'] = email_cc
  message['from'] = email_from
  message['subject'] = subject
  text_part = MIMEText(text, 'plain')
  html_part = MIMEText(html, 'html')
  message.attach(text_part)
  message.attach(html_part)
  
  _retry(service.users().messages().send(userId='me', body={'raw': base64.urlsafe_b64encode(message.as_string())}))
  
 
