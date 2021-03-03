This is a simple library to obtain an AWS STS refreshable credential using an OIDC provider as the source of throught for the AssumeRoleWithWebIdentity AWS AuthN flow.

## Requirements

- oidc-agent >= 4.0.x
  - with your oidc provider registered (e.g. INFN-Cloud IAM instance)
## Install

```bash
pip3 install -U git+ssh://git@github.com/dodas-ts/boto3sts
```

## Example code

```python
from boto3sts import credentials as creds

# Get your refreshble credentials session with the oidc-agent profile named e.g.: dodas_oidc-agen-profile
aws_session = creds.assumed_session("dodas_oidc-agen-profile")

# Use the generated session for all the data operations on an s3 bucket
s3 = aws_session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)
for key in s3.list_objects(Bucket='ciangottini')['Contents']:
        print(key['Key'])
```