# import boto3
# from clogger import logger



# # Initialize the S3 client
# s3 = boto3.client('s3')

# def upload_file_to_s3(bucket_name, file_path, s3_key):
#     try:
#         s3.upload_file(file_path, bucket_name, s3_key)
#         print(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{s3_key}'.")
#     except Exception as e:
#         print(f"An error occurred while uploading: {e}")

# def download_file_from_s3(bucket_name, s3_key, download_path):
#     try:
#         s3.download_file(bucket_name, s3_key, download_path)
#         print(f"File '{s3_key}' downloaded from bucket '{bucket_name}' to '{download_path}'.")
#     except Exception as e:
#         print(f"An error occurred while downloading: {e}")