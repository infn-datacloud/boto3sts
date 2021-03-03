import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
import requests
import xmltodict
import liboidcagent as agent
from boto3 import Session


def assumed_session(oidc_profile, session=None):
    """STS Role assume a boto3.Session

    With automatic credential renewal.

    Args:
      oidc_profile: the name of the oidc-agent profile to be used for the identity provider
      session: an optional extant session, note session is captured
               in a function closure for renewing the sts assumed role.

    Notes: We have to poke at botocore internals a few times
    """
    if session is None:
        session = Session()

    def refresh():
        token = agent.get_access_token(oidc_profile, 60, "Example-Py-App")
        r = requests.post("https://minio.cloud.infn.it/",
                  data={
                      'Action':
                      "AssumeRoleWithWebIdentity",
                      'Version': "2011-06-15",
                      'WebIdentityToken': token,
                      'DurationSeconds': 9000
                  },
                  verify=True)

        tree = xmltodict.parse(r.content)

        credentials = dict(tree['AssumeRoleWithWebIdentityResponse']
                    ['AssumeRoleWithWebIdentityResult']['Credentials'])

        return dict(
            access_key=credentials['AccessKeyId'],
            secret_key=credentials['SecretAccessKey'],
            token=credentials['SessionToken'],
            # Silly that we basically stringify so it can be parsed again
            expiry_time=credentials['Expiration'])

    session_credentials = RefreshableCredentials.create_from_metadata(
        metadata=refresh(),
        refresh_using=refresh,
        method='sts')

    # so dirty.. it hurts, no clean way to set this outside of the internals poke
    s = get_session()
    s._credentials = session_credentials
    return Session(botocore_session=s)
