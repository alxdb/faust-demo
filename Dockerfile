FROM python:3.9 AS build
RUN pip install poetry

COPY . faust-demo
WORKDIR /faust-demo
RUN poetry build -n -f wheel

FROM python:3.9
RUN mkdir /app
WORKDIR /app

COPY --from=build /faust-demo/dist .
RUN pip install faust_demo-0.1.0-py3-none-any.whl
CMD faust -A faust_demo.app worker -l info

