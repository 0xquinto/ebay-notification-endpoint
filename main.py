#!/usr/bin/env python3
"""
eBay marketplace account deletion notification endpoint.
Railway.app deployment version.
"""

from flask import Flask, request, jsonify
import hashlib
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get configuration from environment variables
EBAY_VERIFICATION_TOKEN = os.getenv('EBAY_VERIFICATION_TOKEN', 'default_verification_token_change_me')

@app.route('/ebay/marketplace_account_deletion', methods=['GET', 'POST'])
def marketplace_account_deletion():
    """
    Handle eBay marketplace account deletion notifications.
    
    GET: Handle validation challenge from eBay
    POST: Handle actual deletion notifications
    """
    
    if request.method == 'GET':
        return handle_validation_challenge()
    elif request.method == 'POST':
        return handle_deletion_notification()

def handle_validation_challenge():
    """Handle eBay's validation challenge."""
    try:
        challenge_code = request.args.get('challenge_code')
        
        if not challenge_code:
            logger.error("No challenge_code provided")
            return jsonify({'error': 'Missing challenge_code'}), 400
        
        # Create hash using verification token
        hash_input = challenge_code + EBAY_VERIFICATION_TOKEN
        challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
        
        logger.info(f"Validation challenge received: {challenge_code}")
        logger.info(f"Sending response hash: {challenge_response}")
        
        return jsonify({
            'challengeResponse': challenge_response
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling validation challenge: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def handle_deletion_notification():
    """Handle actual marketplace account deletion notifications from eBay."""
    try:
        notification_data = request.get_json()
        
        if not notification_data:
            logger.error("No notification data received")
            return jsonify({'error': 'No data'}), 400
        
        logger.info("Received marketplace account deletion notification:")
        logger.info(f"Notification data: {notification_data}")
        
        # In production, process the deletion request here
        # For now, just acknowledge receipt
        return jsonify({
            'status': 'received',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Notification processed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling deletion notification: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'eBay Notification Endpoint',
        'verification_token_set': bool(EBAY_VERIFICATION_TOKEN != 'default_verification_token_change_me')
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint."""
    return jsonify({
        'service': 'eBay Marketplace Account Deletion Notification Endpoint',
        'status': 'running',
        'endpoints': {
            'notification': '/ebay/marketplace_account_deletion',
            'health': '/health'
        },
        'deployment': 'Railway.app',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
