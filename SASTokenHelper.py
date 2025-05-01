import urllib.parse
import hmac
import hashlib
import base64
import time

def generate_sas_token(uri, key, policy_name=None, expiry=3600):
    ttl = int(time.time() + expiry)
    sign_key = "%s\n%d" % (urllib.parse.quote(uri, safe=''), ttl)
    signature = base64.b64encode(
        hmac.new(base64.b64decode(key), sign_key.encode('utf-8'), hashlib.sha256).digest()
    )
    rawtoken = {
        'sr': uri,
        'sig': signature.decode(),
        'se': str(ttl)
    }
    if policy_name:
        rawtoken['skn'] = policy_name
    return 'SharedAccessSignature ' + urllib.parse.urlencode(rawtoken)
