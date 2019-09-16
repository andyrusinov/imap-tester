#/usr/local/bin/python
import os, urllib.parse, email, ssl
from imapclient import IMAPClient


# returns True if one of args is None
def var_is_none(*args):
  for h in args:
    if h is None:
      return True
  return False


def print_tabbed(output):
  # determine string lengths to make output more fancy
  lengths=[0]*4
  format=""
  for x in output:
    for i in range(4):
      lengths[i]=max(lengths[i],len(str(x[i]))+2)
  lengths[0]=min(lengths[0],35) # trim very long uid
  for i in range(4):
    format+='{:'+str(lengths[i])+'}\t'
  for x in output:
    print(format.format(*x))
  return True


# process folder, print number of messages
def process_folder(server, folder):
  try:
    server.select_folder(folder, readonly=True)
  except IMAPClientError:
    print("Could not select subscribed folder" + folder)
    return True # exit from procedure, do not process further
  messages = server.search()
  print(f"Processing folder {folder}. {len(messages)} messages found")
  output = [("uid","From","Subject","Size")] if len(messages) else [] # if there is 0 messages, we are not printing anything
  for uid, message_data in server.fetch(messages, 'RFC822').items():
    email_message = email.message_from_bytes(message_data[b'RFC822'])
    message_from = email_message.get('From') if email_message.get('From') else ""
    message_subject = email_message.get('Subject') if email_message.get('Subject') else ""
    if len(message_subject) > 60:
      message_subject = message_subject[:60] + '...'
    message_size = str(len(email_message.__bytes__())) if email_message.__bytes__() else "0"
    output += [(uid, message_from, message_subject, message_size)]
  print_tabbed(output)
  print()
  return True

  

def main():
  username,password,servername = os.environ.get('username'), \
                                 os.environ.get('password'), \
                                 os.environ.get('server')

  ssl_context = ssl.create_default_context()
  if not os.environ.get('insecure') is None: # variable "insecure" is set, need to disable cert check
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

  # check variables
  if var_is_none(username, password, servername):
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
    folders = [f[-1] for f in server.list_sub_folders()]
    for folder in folders:
      process_folder(server, folder)

  print ("Logging out")



# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
