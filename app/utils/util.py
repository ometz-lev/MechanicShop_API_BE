#This function is used to create a token that can be used to authenticate a user. The token is created using the jose library and is encoded using a secret key. 
# The token contains the customer_id, the time it was issued, and the time it will expire. The token is then returned to the user.
# app/utils/util.py
from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify, current_app


#Create authentication token
def encode_token(user_id, user_type): #using unique pieces of info to make our tokens user specific

    secret_key = current_app.config['SECRET_KEY']

    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(user_id), #This needs to be a string or the token will be malformed and won't be able to be decoded.
        'user_type': user_type
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


# This function is a decorator that can be used to protect routes that require authentication. 
# It checks for the presence of a token in the request headers, decodes it, and verifies its validity. 
# If the token is valid, the wrapped function is executed; otherwise, an error response is returned.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            secret_key = current_app.config['SECRET_KEY']
            data = jwt.decode(token, secret_key, algorithms=['HS256'])

            print('Decoded token data =', data)
            authenticated_user_id = data['sub']   # Fetch the User ID
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, authenticated_user_id=authenticated_user_id, **kwargs)

    return decorated