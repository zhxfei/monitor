FROM python:3.5

LABEL maintainer="<dylan@zhxfei.com>"

ENV PATH $PATH:/code

ADD . /code

WORKDIR /code

RUN pip install -r requirments.txt -i https://pypi.douban.com/simple

# when docker container start, if CMD api ,should define api_host and api_port env

ENTRYPOINT [ "run.sh" ]

CMD []