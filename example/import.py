# Copyright 2021 dciangot
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
from boto3sts import credentials as creds
from boto3sts import utils

aws_session = creds.assumed_session("dodas_oidc-agen-profile")

s3 = aws_session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)

objects = []

for key in s3.list_objects(Bucket='ciangottini')['Contents']:
        print(key['Key'])
        objects.append(key['Key'])

presigned_urls = utils.presigned_urls(s3, "ciangottini", objects)
