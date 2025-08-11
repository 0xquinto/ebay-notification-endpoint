from flask import Flask, request, jsonify
import hashlib
import os
from datetime import datetime

app = Flask(__name__)

# Simple environment variable handling
EBAY_VERIFICATION_TOKEN = os.environ.get(
    'EBAY_VERIFICATION_TOKEN', 
    'ebay_marketplace_deletion_verification_token_2025_secure_long_string_12345'
)

@app.route('/')
def home():
    return jsonify({
        'service': 'eBay Notification Endpoint',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'token_length': len(EBAY_VERIFICATION_TOKEN)
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'port': os.environ.get('PORT', '5000'),
        'token_set': bool(EBAY_VERIFICATION_TOKEN)
    })

@app.route('/ebay/marketplace_account_deletion', methods=['GET', 'POST'])
def marketplace_account_deletion():
    if request.method == 'GET':
        challenge_code = request.args.get('challenge_code')
        if not challenge_code:
            return jsonify({'error': 'Missing challenge_code'}), 400
        
        hash_input = challenge_code + EBAY_VERIFICATION_TOKEN
        challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
        
        return jsonify({'challengeResponse': challenge_response})
    
    elif request.method == 'POST':
        return jsonify({
            'status': 'received',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Notification processed'
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
