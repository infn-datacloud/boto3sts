from botocore.exceptions import ClientError


def presigned_urls(s3_client, bucket, objects, expiration=3600):

    urls = []

    for obj in objects:
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                                              Params={'Bucket': bucket,
                                                                              'Key': obj},
                                                                              ExpiresIn=expiration)
        except ClientError as e:
            print(e)
            return None

        urls.append(response)

    return urls