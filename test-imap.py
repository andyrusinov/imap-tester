#/usr/local/bin/python
import os, urllib.parse, email, ssl
from imapclient import IMAPClient


def main():
  username,password,servername = os.environ.get('username'), \
                                 os.environ.get('password'), \
                                 os.environ.get('server')

  ssl_context = ssl.create_default_context()
  if not os.environ.get('insecure') is None: # variable "insecure" is set, need to disable cert check
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

  # check variables
  if username is None or \
    password is None or \
    servername is None:
    print('ERROR: need to set username password and server vars:\n' + \
          'docker run --env username=\'account\' --env password=\'password\'' + \
          '--env server=\'server\' [--env insecure=yes] --rm -it andyrusinov/imap-tester\n' + \
	  'optional var [insecure] drops SSL secure requirements\n' + \
          'Note: this script never saves the messages. All it does is downloading ' + \
          'them from INBOX, printing their size and dropping them (thus checking the connection)')
    exit()
  
  # connect
  with IMAPClient(servername, ssl_context=ssl_context) as server:
    server.login(username, password)
    server.select_folder('INBOX', readonly=True)

    # find messages, print their size
    messages = server.search()
    for uid, message_data in server.fetch(messages, 'RFC822').items():
      email_message = email.message_from_bytes(message_data[b'RFC822'])
      print(uid, email_message.get('From'), email_message.get('Subject'), "Size = " + \
      str(len(email_message.__bytes__() if email_message.__bytes__() else '')) )


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
