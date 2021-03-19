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
# possible options are:
# creds.assumed_session("dodas_oidc-agen-profile", endpoint="https://minio.cloud.infn.it/", verify=True)
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

# possible options are: creds.assumed_session("dodas_oidc-agen-profile", endpoint="https://minio.cloud.infn.it/", verify=True)
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

```bash
curl -XGET {{my_presigned_url}} > /tmp/myfile.txt
```

## F.A.Q.

### OidcAgentConnectError: OIDC_REMOTE_SOCK env var not set

This error means that oidc-agent is not properly configured. Please note that the following steps should be done to get a proper environment set by the oidc-agent:

1. check if you can retrieve a valid token with
```bash
oidc-token <profile name you choose, e.g. infncloud>
```
if this succeed and you still find this error, please feel free to file a issue. Otherwise go to the next point.
2. try the following:
```bash
oidc-keychain
```
if you obtain a valid response, a simple `eval \`oidc-keychain\`` should solve the error. After that you can quicly check that everything is ok by re-trying to get a valid token from cli with `oidc-token <profile name you choose, e.g. infncloud>`. If now you get a "Account not loaded" error, this means that the oidc-agent has been recently restarted (e.g. a reboot of the system) and you should go to the next point.
3. refresh your authorization for your oidc profile.
```bash
oidc-gen --reauthenticate --flow device <profile name you choose, e.g. infncloud>
```
aat this point if this fails or it succeeds and you still get the error running boto3sts please feel free to file a issue.
