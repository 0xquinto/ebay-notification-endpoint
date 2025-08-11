from flask import Flask, request, jsonify
import hashlib
import os
from datetime import datetime

app = Flask(__name__)

# Get token from environment
EBAY_VERIFICATION_TOKEN = os.environ.get(
    'EBAY_VERIFICATION_TOKEN', 
    'ebay_marketplace_deletion_verification_token_2025_secure_long_string_12345'
)

# Your Render endpoint URL (CRITICAL - must match exactly what you told eBay)
ENDPOINT_URL = 'https://ebay-notification-endpoint-3frs.onrender.com/ebay/marketplace_account_deletion'

print(f"[STARTUP] Token configured: {bool(EBAY_VERIFICATION_TOKEN)}")
print(f"[STARTUP] Token length: {len(EBAY_VERIFICATION_TOKEN)}")
print(f"[STARTUP] Endpoint URL: {ENDPOINT_URL}")

@app.route('/')
def home():
    return jsonify({
        'service': 'eBay Notification Endpoint',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'token_configured': bool(EBAY_VERIFICATION_TOKEN),
        'token_length': len(EBAY_VERIFICATION_TOKEN),
        'endpoint_url': ENDPOINT_URL
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/ebay/marketplace_account_deletion', methods=['GET', 'POST'])
def marketplace_account_deletion():
    print(f"[REQUEST] Method: {request.method}")
    print(f"[REQUEST] URL: {request.url}")
    print(f"[REQUEST] Args: {dict(request.args)}")
    
    if request.method == 'GET':
        challenge_code = request.args.get('challenge_code')
        
        print(f"[VALIDATION] Challenge code received: {challenge_code}")
        
        if not challenge_code:
            print("[ERROR] No challenge_code in request")
            return jsonify({'error': 'Missing challenge_code'}), 400
        
        # CORRECT CALCULATION: challenge_code + verification_token + endpoint_url
        hash_input = challenge_code + EBAY_VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
        
        print(f"[VALIDATION] Hash components:")
        print(f"  - Challenge: {challenge_code}")
        print(f"  - Token length: {len(EBAY_VERIFICATION_TOKEN)}")
        print(f"  - Endpoint URL: {ENDPOINT_URL}")
        print(f"[VALIDATION] Challenge response: {challenge_response}")
        
        # Return with proper content-type header
        response = jsonify({'challengeResponse': challenge_response})
        response.headers['Content-Type'] = 'application/json'
        
        return response, 200
    
    elif request.method == 'POST':
        data = request.get_json()
        print(f"[NOTIFICATION] Received POST data: {data}")
        
        # Handle the marketplace account deletion notification
        if data and 'notification' in data:
            notification = data['notification']
            notification_data = notification.get('data', {})
            
            print(f"[DELETION] Username: {notification_data.get('username')}")
            print(f"[DELETION] UserId: {notification_data.get('userId')}")
            print(f"[DELETION] EiasToken: {notification_data.get('eiasToken')}")
            
            # Process the deletion (in production, you'd delete user data here)
            
        # Return one of the accepted status codes
        return '', 204  # 204 No Content

@app.route('/test-validation', methods=['GET'])
def test_validation():
    """Test endpoint to verify validation is working"""
    test_challenge = 'test_challenge_123'
    
    # Show both calculations for comparison
    old_hash_input = test_challenge + EBAY_VERIFICATION_TOKEN
    old_response = hashlib.sha256(old_hash_input.encode()).hexdigest()
    
    new_hash_input = test_challenge + EBAY_VERIFICATION_TOKEN + ENDPOINT_URL
    new_response = hashlib.sha256(new_hash_input.encode()).hexdigest()
    
    return jsonify({
        'test_challenge': test_challenge,
        'token_length': len(EBAY_VERIFICATION_TOKEN),
        'endpoint_url': ENDPOINT_URL,
        'old_calculation': {
            'method': 'challenge + token',
            'response': old_response
        },
        'correct_calculation': {
            'method': 'challenge + token + endpoint_url',
            'response': new_response
        },
        'test_url': f"https://ebay-notification-endpoint-3frs.onrender.com/ebay/marketplace_account_deletion?challenge_code={test_challenge}",
        'instructions': 'The correct_calculation is what eBay expects'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[STARTUP] Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
