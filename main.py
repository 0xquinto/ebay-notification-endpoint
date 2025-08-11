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

print(f"[STARTUP] Token configured: {bool(EBAY_VERIFICATION_TOKEN)}")
print(f"[STARTUP] Token length: {len(EBAY_VERIFICATION_TOKEN)}")
print(f"[STARTUP] Token first 10 chars: {EBAY_VERIFICATION_TOKEN[:10]}...")

@app.route('/')
def home():
    return jsonify({
        'service': 'eBay Notification Endpoint',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'token_configured': bool(EBAY_VERIFICATION_TOKEN),
        'token_length': len(EBAY_VERIFICATION_TOKEN)
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
    print(f"[REQUEST] Headers: {dict(request.headers)}")
    
    if request.method == 'GET':
        challenge_code = request.args.get('challenge_code')
        
        print(f"[VALIDATION] Challenge code received: {challenge_code}")
        print(f"[VALIDATION] Token length: {len(EBAY_VERIFICATION_TOKEN)}")
        print(f"[VALIDATION] Token first 10: {EBAY_VERIFICATION_TOKEN[:10]}...")
        
        if not challenge_code:
            print("[ERROR] No challenge_code in request")
            return jsonify({'error': 'Missing challenge_code'}), 400
        
        # Calculate response
        hash_input = challenge_code + EBAY_VERIFICATION_TOKEN
        challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
        
        print(f"[VALIDATION] Hash input length: {len(hash_input)}")
        print(f"[VALIDATION] Challenge response: {challenge_response}")
        
        response = {'challengeResponse': challenge_response}
        print(f"[RESPONSE] Sending: {response}")
        
        return jsonify(response), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        print(f"[NOTIFICATION] Received POST data: {data}")
        
        return jsonify({
            'status': 'received',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Notification processed'
        }), 200

@app.route('/test-validation', methods=['GET'])
def test_validation():
    """Test endpoint to verify validation is working"""
    test_challenge = 'test_challenge_123'
    hash_input = test_challenge + EBAY_VERIFICATION_TOKEN
    challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
    
    return jsonify({
        'test_challenge': test_challenge,
        'token_length': len(EBAY_VERIFICATION_TOKEN),
        'token_first_10': EBAY_VERIFICATION_TOKEN[:10],
        'expected_response': challenge_response,
        'test_url': f"{request.host_url}ebay/marketplace_account_deletion?challenge_code={test_challenge}",
        'instructions': 'Use the test_url to verify the endpoint returns the expected_response'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[STARTUP] Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
