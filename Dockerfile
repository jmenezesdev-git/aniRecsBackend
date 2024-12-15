FROM python:3.12
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD ["backend.py"]
#CMD ["python", "-m", "flask", "--app", "'backend'", "run", "--host=0.0.0.0"]