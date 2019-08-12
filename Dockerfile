FROM python:latest
MAINTAINER arusinov@intermedia.net
RUN pip install imapclient
ADD ["./test-imap.py", \
     "/"]
ENTRYPOINT ["/usr/local/bin/python", \
            "/test-imap.py"]
