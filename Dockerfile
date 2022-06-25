FROM python:3.10.5-alpine3.16

WORKDIR /src
COPY database/* database/
COPY download-dataset.sh .
COPY *.py ./
COPY .env .

RUN pip install treelib psycopg2-binary python-dotenv

RUN apk --no-cache add curl
RUN apk add --no-cache bash
RUN sh download-dataset.sh

CMD ["bash"]