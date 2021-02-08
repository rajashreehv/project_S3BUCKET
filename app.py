from flask import Flask, render_template, redirect, request
from werkzeug.utils import secure_filename
import boto3, botocore

import os

S3_BUCKET = ""
S3_KEY = ""
S3_SECRET = ""
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
SECRET_KEY = os.urandom(32)
DEBUG = True
PORT = 5000
s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# function to check file extension
def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)


def upload_file_to_s3(file, bucket_name, acl="public-read"):
    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    print(file.content_type)
    print(bucket_name)
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return "{}{}".format(S3_LOCATION, file.filename)


@app.route("/", methods=['POST', 'GET'])
def upload_file():
    if request.method == "POST":
        # A
        if "user_file" not in request.files:
            return "No user_file key in request.files"
        # B
        file = request.files["user_file"]
        """
            These attributes are also available
            file.filename               # The actual name of the file
            file.content_type
            file.content_length
            file.mimetype
        """
        # C.
        if file.filename == "":
            return "Please select a file"
        # D.
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output = upload_file_to_s3(file, S3_BUCKET)
            return str(output)
        else:
            return redirect("/")
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
