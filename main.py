#!/usr/bin/env python3
"""
eBay marketplace account deletion notification endpoint.
Railway.app deployment version - Fixed for Railway hosting.
"""

from flask import Flask, request, jsonify
import hashlib
import logging
import os
from datetime import datetime
import sys

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Get configuration from environment variables
EBAY_VERIFICATION_TOKEN = os.getenv(
    'EBAY_VERIFICATION_TOKEN', 
    'ebay_marketplace_deletion_verification_token_2025_secure_long_string_12345'
)

# Log startup info
logger.info("Starting eBay Notification Endpoint")
logger.info(f"Port: {os.environ.get('PORT', '5000')}")
logger.info(f"Verification token set: {bool(EBAY_VERIFICATION_TOKEN)}")
logger.info(f"Verification token length: {len(EBAY_VERIFICATION_TOKEN)}")

@app.route('/ebay/marketplace_account_deletion', methods=['GET', 'POST'])
def marketplace_account_deletion():
    """
    Handle eBay marketplace account deletion notifications.
    
    GET: Handle validation challenge from eBay
    POST: Handle actual deletion notifications
    """
    logger.info(f"Received {request.method} request to notification endpoint")
    logger.info(f"Request args: {request.args}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        if request.method == 'GET':
            return handle_validation_challenge()
        elif request.method == 'POST':
            return handle_deletion_notification()
        else:
            return jsonify({'error': 'Method not allowed'}), 405
    except Exception as e:
        logger.error(f"Error in marketplace_account_deletion: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

def handle_validation_challenge():
    """Handle eBay's validation challenge."""
    try:
        challenge_code = request.args.get('challenge_code')
        
        logger.info(f"Validation challenge - Challenge code: {challenge_code}")
        logger.info(f"Validation challenge - Using token length: {len(EBAY_VERIFICATION_TOKEN)}")
        
        if not challenge_code:
            logger.error("No challenge_code provided in request")
            return jsonify({'error': 'Missing challenge_code parameter'}), 400
        
        # Create hash using verification token
        hash_input = challenge_code + EBAY_VERIFICATION_TOKEN
        challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
        
        logger.info(f"Generated challenge response: {challenge_response}")
        
        response_data = {
            'challengeResponse': challenge_response,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in validation challenge: {e}")
        return jsonify({
            'error': 'Validation challenge failed', 
            'details': str(e)
        }), 500

def handle_deletion_notification():
    """Handle actual marketplace account deletion notifications from eBay."""
    try:
        notification_data = request.get_json()
        
        logger.info("Processing deletion notification")
        logger.info(f"Notification data: {notification_data}")
        
        if not notification_data:
            logger.error("No notification data received")
            return jsonify({'error': 'No notification data provided'}), 400
        
        # In production, process the deletion request here
        # For now, just acknowledge receipt and log
        response_data = {
            'status': 'received',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Marketplace account deletion notification processed successfully',
            'notification_id': notification_data.get('notificationId', 'unknown')
        }
        
        logger.info(f"Deletion notification processed: {response_data}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error processing deletion notification: {e}")
        return jsonify({
            'error': 'Failed to process deletion notification', 
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed status."""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'eBay Notification Endpoint',
            'version': '1.1.0',
            'deployment': 'Railway.app',
            'environment': {
                'port': os.environ.get('PORT', '5000'),
                'python_version': sys.version,
                'verification_token_configured': bool(EBAY_VERIFICATION_TOKEN),
                'verification_token_length': len(EBAY_VERIFICATION_TOKEN),
                'verification_token_valid': len(EBAY_VERIFICATION_TOKEN) >= 32
            }
        }
        
        logger.info("Health check requested")
        return jsonify(health_data), 200
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with service information."""
    try:
        home_data = {
            'service': 'eBay Marketplace Account Deletion Notification Endpoint',
            'status': 'running',
            'version': '1.1.0',
            'endpoints': {
                'notification': '/ebay/marketplace_account_deletion',
                'health': '/health'
            },
            'deployment': {
                'platform': 'Railway.app',
                'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production')
            },
            'configuration': {
                'verification_token_length': len(EBAY_VERIFICATION_TOKEN),
                'verification_token_valid': len(EBAY_VERIFICATION_TOKEN) >= 32
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info("Home page requested")
        return jsonify(home_data), 200
        
    except Exception as e:
        logger.error(f"Home page error: {e}")
        return jsonify({
            'error': 'Home page failed to load',
            'details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for debugging Railway deployment."""
    try:
        test_data = {
            'message': 'Test endpoint working',
            'timestamp': datetime.utcnow().isoformat(),
            'environment_variables': {
                'PORT': os.environ.get('PORT'),
                'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
                'EBAY_VERIFICATION_TOKEN_SET': bool(EBAY_VERIFICATION_TOKEN)
            },
            'request_info': {
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers)
            }
        }
        
        logger.info("Test endpoint called")
        return jsonify(test_data), 200
        
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    return jsonify({
        'error': 'Not Found',
        'message': f'The requested URL {request.url} was not found',
        'available_endpoints': [
            '/',
            '/health',
            '/test',
            '/ebay/marketplace_account_deletion'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'The server encountered an internal error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Verification token configured: {bool(EBAY_VERIFICATION_TOKEN)}")
    logger.info(f"Verification token length: {len(EBAY_VERIFICATION_TOKEN)} characters")
    
    # Run the app
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,  # Disable debug in production
        threaded=True
    )
