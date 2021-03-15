This is a simple library to obtain an AWS STS refreshable credential using an OIDC provider as the source of throught for the AssumeRoleWithWebIdentity AWS AuthN flow.

## Requirements

- oidc-agent >= 4.0.x
  - with your oidc provider registered (e.g. INFN-Cloud IAM instance)

Iif you have oidc-agent active on your host, but you want to work inside a container, it would be enough to mount the oidc-agent socket inside the container with:

```bash
docker run -v $OIDC_SOCK:$OIDC_SOCK <your image>
```

## Install

```bash
pip3 install -U git+https://git@github.com/dodas-ts/boto3sts
```

## Example code

```python
import boto3
from boto3sts import credentials as creds

# Get your refreshble credentials session with the oidc-agent profile named e.g.: dodas_oidc-agen-profile
aws_session = creds.assumed_session("dodas_oidc-agen-profile")

# Use the generated session for all the data operations on an s3 bucket
s3 = aws_session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)
for key in s3.list_objects(Bucket='ciangottini')['Contents']:
        print(key['Key'])
```

Then you can, for instance, read a csv via pandas adding the following lines:

```python
import io
import pandas as pd
obj = s3.get_object(Bucket='bybucket', Key='test/mycsv.csv')
df = pd.read_csv(io.BytesIO(obj['Body'].read()))
```

### Get a presigned URL

You can obtain a temporary URL to download an object without the need of any credential:

```python
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

```

Then, for instance, you can pass this urls to a distributed system, without the need to distribute any credential.