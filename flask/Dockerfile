FROM python:3.6
ENV PATH /usr/local/bin:$PATH
COPY . /flask/code
WORKDIR /flask/code
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5001
