import csv
import json
from bs4 import BeautifulSoup
import urllib.request as urllib
import requests
import pprint
import ibm_boto3
from ibm_botocore.client import Config
import boto3
import os
import random
import string
import time
from multiprocessing import Pool

cos_credentials = {
  "apikey": "gF_7Gjvqflf4TPju7t5lbgR4NB9dDAQ8EVwf1DmwKGDo",
  "cos_hmac_keys": {
    "access_key_id": "2b946807fa48404bb2cf98fb1987b97b",
    "secret_access_key": "c5a0f3b7a406621dd66847800dfb32eb98aecf35773528fe"
  },
  "endpoints": "https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints",
  "iam_apikey_description": "Auto-generated for key 2b946807-fa48-404b-b2cf-98fb1987b97b",
  "iam_apikey_name": "credentials",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/f8a68e33cf3f4b72bf16e2d2827a16c5::serviceid:ServiceId-dc98af04-3ddb-4f94-9c22-7b2744342cd1",
  "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/f8a68e33cf3f4b72bf16e2d2827a16c5:cbb6b174-e693-43b3-ba00-eff5c448394d::"
}

service_endpoint = 'https://s3.private.us-east.cloud-object-storage.appdomain.cloud'

cos_client = boto3.client('s3', 
                          endpoint_url = service_endpoint, 
                          aws_access_key_id=cos_credentials["cos_hmac_keys"]["access_key_id"], 
                          aws_secret_access_key=cos_credentials["cos_hmac_keys"]["secret_access_key"])

# Return all buckets in your COS instance
def get_all_buckets(cos_client):
    response = cos_client.list_buckets()
    allbuckets = []
    for bucket in response['Buckets']:
        allbuckets.append(bucket['Name'])
    return allbuckets

# Return all the objects in a COS bucket
def get_objects_in_bucket(cos_client,bucket_name):
    return cos_client.list_objects(Bucket=bucket_name)

# Create a unique COS bucket
def create_unique_bucket(cos_client, bucket_prefix):
    # Create a random 10 digit string
    # this random string increases the likelihood of the bucket name to be unique
    lst = [random.choice(string.ascii_letters + string.digits) for n in range(10)]
    random_string = "".join(lst).lower()
    bucket = "%s-%s" % (bucket_prefix, random_string)
    
    #print("creating bucket: ", bucket)
    cos_client.create_bucket(Bucket=bucket)
    print("Bucket %s created" % bucket)

# Upload objects to COS bucket
def upload_file_to_bucket(cos_client,f,bucket):
    file_name = os.path.basename(f)
    # print("Uploading %s to bucket: %s" % (file_name,bucket))
    cos_client.upload_file(Filename = f, Bucket = bucket, Key = file_name)

# Download objects from a URL 
def download_file_from_url(file_url, file_name, save_directory=None):
    # If save directory provided then don't delete local downloads
    working_directory = "temp_cos_files"
    if save_directory is not None:
        working_directory = save_directory
    os.makedirs(working_directory, exist_ok=True)

    # file_name = os.path.basename(file_url)
    # Delete file if present as perhaps download failed and file corrupted
    file_path = os.path.join(working_directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    file_path, _ = urllib.urlretrieve(file_url, file_path)
    # stat_info = os.stat(file_path)
    # print('Downloaded', file_path, stat_info.st_size, 'bytes.')
    
# Remove files from the specified directory in the local environment
def remove_files_from_dir(dir):
    for f in os.listdir(dir):
        file_path = os.path.join(dir, f)
        if os.path.exists(file_path):
            os.remove(file_path)


#############################################################JUPYTER NOTEBOOK FUNCTIONS################################################################



def make_keyword():
    search_terms = []
    with open('item_no_image_with_names.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                search_terms.append(" ".join([row[1], row[3], row[5]]))
                line_count += 1

    print(f'Processed {line_count} lines.')
    return search_terms

# def scrape_google():
#     response = google_images_download.googleimagesdownload()   #class instantiation
#     for query in search_terms:
#         try:
#             arguments = {"keywords":query,"limit":2, "print_urls":True}   #creating list of arguments
#             response.download(arguments)   #passing the arguments to the function
#         except:
#             print(query)
#     # print(paths)   #printing absolute paths of the downloaded images


def get_link_from_html(query):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    url = "https://www.google.com/search?tbm=isch&q=" + query
    headers = {'User-Agent': user_agent, }
    request = urllib.Request(url, None, headers)
    html = urllib.urlopen(request).read()
    soup = BeautifulSoup(html,'html.parser')
    for link in soup.find_all('a'):
        print(link)
        #PROBLEM HERE: where is the image link within the html?
    return 0  

def download_image(query):
    working_dir = "/mnt/restofallpaintings"
    url = get_link_from_html(query)
    download_file_from_url(url, query, save_directory=working_dir)  



def run():
    pool = Pool()
    search_terms = make_keyword()
    pool.map(download_image, search_terms)


# def get_url_from_html():




# 
# get_text_from_html("cat")

# parallelize: Pool.map
#threads rather than processing 
#data list is the queries
#function retrieves the query, query must be parsed, get first image in results, curl, save to bucket