"""
REF
https://www.gormanalysis.com/blog/connecting-to-aws-s3-with-python/


bucket name = img-upload-bucket-printify
username using the access id and key below: bernardi-1
"""


import logging
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import sys
import requests

#dynamic adding to path
from os.path import dirname,abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)



load_dotenv()
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# print(f"Access Key: {access_key}")
# print(f"Secret Key: {secret_key}")

#Create s3 client and auth connection for user 
# REF: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
s3 = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret_key)


def uploadFile(file_name,bucket,object_name=None):

    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        response = s3.upload_file(file_name,bucket,object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# Filename='Printify_scripts\images\mr.fish.png'
# bucket_name = 'img-upload-bucket-printify'
# print(uploadFile(Filename,bucket_name))


def upload_img_files_to_bucket(images_list:list,bucket_name,img_folder_abs_path='Printify_scripts\images',object_name=None):

    img_folder_path = img_folder_abs_path
    
    for img in images_list:
        file_name = os.path.join(img_folder_path,img)
        print(f"filename: {file_name}")
        
        
        object_name = os.path.basename(img)

        try:
            response = s3.upload_file(file_name,bucket_name,object_name)
        except ClientError as e:
            logging.error(e)
            # return False
        
    return "successfully uploaded images to bucket"

imgs_list = [
    'mr.fish.png','Zen as fuck.png'
]

bucket_name = 'img-upload-bucket-printify'

img_folder_abs_path = r'C:\Users\balma\Documents\Programming\Python\Python Projects\photoshop_printify_gui_tools\Printify_scripts\images'


# print(upload_img_files(imgs_list,bucket_name,img_folder_abs_path))


"""
this function will take an img name Ex. mr.fish, and return its bucket url
"""
def get_img_url_from_bucket(img_name):
    # t = f"s3://img-upload-bucket-printify/{img_name}"
    X = f"https://img-upload-bucket-printify.s3.us-east-1.amazonaws.com/{img_name}"
    return X

def access_img_test(img='mr.fish.png'):

    # url = get_img_url_from_bucket(img)
    # print(url)
    response = requests.get('https://img-upload-bucket-printify.s3.us-east-1.amazonaws.com/mr.fish.png')
    print(response)

if __name__ == '__main__':
    # print(upload_img_files_to_bucket(imgs_list,bucket_name,img_folder_abs_path))

    access_img_test()