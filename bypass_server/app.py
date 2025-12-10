# # ===========================================
# # bypass_server/app.py
# # ===========================================
# from flask import Flask, request, redirect, render_template_string
# from datetime import datetime, timedelta
# import asyncio
# import sys
# import os

# # Add parent directory to path for imports
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from database.connection import Database
# from database.operations import TokenOperations
# from config.settings import Config
# from utils.url_shortener import URLShortener

# app = Flask(__name__)

# # Initialize database connection
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(Database.connect())

# @app.route('/redirect')
# async def handle_redirect():
#     """Handle verification redirect with bypass detection"""
#     token = request.args.get('token')
    
#     if not token:
#         return render_template_string(ERROR_TEMPLATE, 
#             message="Token not provided",
#             bot_link=f"https://t.me/{Config.USER_BOT_TOKEN.split(':')[0]}?start=newToken"
#         )
    
#     # Get token from database
#     token_data = await TokenOperations.get_token(token)
    
#     if not token_data:
#         return render_template_string(ERROR_TEMPLATE,
#             message="Token invalid, expired, or already used",
#             bot_link=f"https://t.me/{Config.USER_BOT_TOKEN.split(':')[0]}?start=newToken"
#         )
    
#     # Check if token is expired (2 days)
#     created_at = token_data["created_at"]
#     if datetime.utcnow() - created_at > timedelta(days=Config.TOKEN_EXPIRY_DAYS):
#         await TokenOperations.delete_token(token)
#         return render_template_string(ERROR_TEMPLATE,
#             message="Token expired",
#             bot_link=f"https://t.me/{Config.USER_BOT_TOKEN.split(':')[0]}?start=newToken"
#         )
    
#     # Check if token already used
#     if token_data["status"] in ["verified", "bypassed"]:
#         return render_template_string(ERROR_TEMPLATE,
#             message="Token already used",
#             bot_link=f"https://t.me/{Config.USER_BOT_TOKEN.split(':')[0]}?start=newToken"
#         )
    
#     # Bypass detection checks
#     created_at = token_data["created_at"]
#     time_diff = datetime.utcnow() - created_at
    
#     # Check 1: Time difference must be at least 2 minutes
#     if time_diff < timedelta(minutes=2):
#         # Bypass detected: Too fast
#         await TokenOperations.update_token_status(token, "bypassed")
#         unique_id = token_data["unique_id"]
#         user_id = token_data["created_by"]
#         bot_username = Config.USER_BOT_TOKEN.split(':')[0]
#         redirect_url = f"https://t.me/{bot_username}?start=verify_{unique_id}_{user_id}"
        
#         return render_template_string(REDIRECT_TEMPLATE,
#             redirect_url=redirect_url,
#             status="bypassed",
#             delay=3
#         )
    
#     # Check 2: Cross-origin check
#     referer = request.headers.get('Referer', '')
#     whitelist_domains = URLShortener.get_whitelist_domains()
    
#     is_whitelisted = False
#     if referer:
#         for domain in whitelist_domains:
#             if domain in referer:
#                 is_whitelisted = True
#                 break
    
#     if not is_whitelisted:
#         # Bypass detected: Invalid cross-origin
#         await TokenOperations.update_token_status(token, "bypassed")
#         unique_id = token_data["unique_id"]
#         user_id = token_data["created_by"]
#         bot_username = Config.USER_BOT_TOKEN.split(':')[0]
#         redirect_url = f"https://t.me/{bot_username}?start=verify_{unique_id}_{user_id}"
        
#         return render_template_string(REDIRECT_TEMPLATE,
#             redirect_url=redirect_url,
#             status="bypassed",
#             delay=3
#         )
    
#     # All checks passed - Mark as verified
#     await TokenOperations.update_token_status(token, "verified")
#     unique_id = token_data["unique_id"]
#     user_id = token_data["created_by"]
#     bot_username = Config.USER_BOT_TOKEN.split(':')[0]
#     redirect_url = f"https://t.me/{bot_username}?start=verify_{unique_id}_{user_id}"
    
#     return render_template_string(REDIRECT_TEMPLATE,
#         redirect_url=redirect_url,
#         status="verified",
#         delay=3
#     )

# # ===========================================
# # HTML Templates
# # ===========================================

# ERROR_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Verification Error</title>
#     <style>
#         * {
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }
        
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             min-height: 100vh;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             padding: 20px;
#         }
        
#         .container {
#             background: white;
#             border-radius: 20px;
#             padding: 40px;
#             max-width: 500px;
#             width: 100%;
#             box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
#             text-align: center;
#             animation: slideUp 0.5s ease-out;
#         }
        
#         @keyframes slideUp {
#             from {
#                 opacity: 0;
#                 transform: translateY(30px);
#             }
#             to {
#                 opacity: 1;
#                 transform: translateY(0);
#             }
#         }
        
#         .error-icon {
#             font-size: 80px;
#             margin-bottom: 20px;
#             animation: shake 0.5s ease-in-out;
#         }
        
#         @keyframes shake {
#             0%, 100% { transform: translateX(0); }
#             25% { transform: translateX(-10px); }
#             75% { transform: translateX(10px); }
#         }
        
#         h1 {
#             color: #e74c3c;
#             font-size: 28px;
#             margin-bottom: 15px;
#         }
        
#         p {
#             color: #555;
#             font-size: 16px;
#             margin-bottom: 30px;
#             line-height: 1.6;
#         }
        
#         .message {
#             background: #fee;
#             border-left: 4px solid #e74c3c;
#             padding: 15px;
#             margin-bottom: 30px;
#             border-radius: 5px;
#             text-align: left;
#         }
        
#         .btn {
#             display: inline-block;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 15px 40px;
#             border-radius: 50px;
#             text-decoration: none;
#             font-size: 16px;
#             font-weight: bold;
#             transition: transform 0.3s, box-shadow 0.3s;
#             box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
#         }
        
#         .btn:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
#         }
        
#         .info {
#             margin-top: 20px;
#             font-size: 14px;
#             color: #888;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="error-icon">❌</div>
#         <h1>Token Error</h1>
#         <div class="message">
#             <strong>{{ message }}</strong>
#         </div>
#         <p>To get another token, click the button below:</p>
#         <a href="{{ bot_link }}" class="btn">🔄 Get New Token</a>
#         <p class="info">You can generate up to 15 tokens per day</p>
#     </div>
# </body>
# </html>
# '''

# REDIRECT_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Redirecting...</title>
#     <style>
#         * {
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }
        
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             min-height: 100vh;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             padding: 20px;
#         }
        
#         .container {
#             background: white;
#             border-radius: 20px;
#             padding: 50px;
#             max-width: 500px;
#             width: 100%;
#             box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
#             text-align: center;
#             animation: fadeIn 0.5s ease-out;
#         }
        
#         @keyframes fadeIn {
#             from { opacity: 0; }
#             to { opacity: 1; }
#         }
        
#         .status-icon {
#             font-size: 100px;
#             margin-bottom: 20px;
#             animation: bounce 1s infinite;
#         }
        
#         @keyframes bounce {
#             0%, 100% { transform: translateY(0); }
#             50% { transform: translateY(-20px); }
#         }
        
#         h1 {
#             color: #333;
#             font-size: 32px;
#             margin-bottom: 15px;
#         }
        
#         p {
#             color: #666;
#             font-size: 18px;
#             margin-bottom: 30px;
#         }
        
#         .countdown {
#             font-size: 60px;
#             font-weight: bold;
#             color: #667eea;
#             margin: 30px 0;
#             animation: pulse 1s infinite;
#         }
        
#         @keyframes pulse {
#             0%, 100% { transform: scale(1); }
#             50% { transform: scale(1.1); }
#         }
        
#         .loader {
#             width: 50px;
#             height: 50px;
#             border: 5px solid #f3f3f3;
#             border-top: 5px solid #667eea;
#             border-radius: 50%;
#             animation: spin 1s linear infinite;
#             margin: 20px auto;
#         }
        
#         @keyframes spin {
#             0% { transform: rotate(0deg); }
#             100% { transform: rotate(360deg); }
#         }
        
#         .status-verified {
#             color: #27ae60;
#         }
        
#         .status-bypassed {
#             color: #e74c3c;
#         }
#     </style>
#     <script>
#         let countdown = {{ delay }};
        
#         function updateCountdown() {
#             document.getElementById('countdown').textContent = countdown;
#             countdown--;
            
#             if (countdown < 0) {
#                 window.location.href = '{{ redirect_url }}';
#             }
#         }
        
#         setInterval(updateCountdown, 1000);
#         updateCountdown();
#     </script>
# </head>
# <body>
#     <div class="container">
#         {% if status == 'verified' %}
#             <div class="status-icon">✅</div>
#             <h1 class="status-verified">Verification Successful!</h1>
#             <p>You will be redirected to the bot...</p>
#         {% else %}
#             <div class="status-icon">⚠️</div>
#             <h1 class="status-bypassed">Bypass Detected!</h1>
#             <p>Please complete the verification properly...</p>
#         {% endif %}
        
#         <div class="countdown" id="countdown">{{ delay }}</div>
#         <div class="loader"></div>
#         <p style="font-size: 14px; color: #888;">If not redirected automatically, <a href="{{ redirect_url }}">click here</a></p>
#     </div>
# </body>
# </html>
# '''

# if __name__ == '__main__':
#     app.run(
#         host=Config.SERVER_HOST,
#         port=Config.SERVER_PORT,
#         debug=True
#     )

# ===========================================
# bypass_server/app.py
# ===========================================
from flask import Flask, request, redirect, render_template_string
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import Database
from database.operations import TokenOperations
from config.settings import Config
from utils.url_shortener import URLShortener

app = Flask(__name__)

# Initialize database connection
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(Database.connect())

def get_user_bot_username():
    """Get user bot username from token"""
    # Extract bot username from token (first part before ':')
    return Config.USER_BOT_TOKEN.split(':')[0]

@app.route('/redirect')
def handle_redirect():
    """Handle verification redirect with bypass detection"""
    token = request.args.get('token')
    
    if not token:
        return render_template_string(ERROR_TEMPLATE, 
            message="Token not provided",
            bot_link=f"https://t.me/{get_user_bot_username()}?start=newToken"
        )
    
    # Get token from database (run async in sync context)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    token_data = loop.run_until_complete(TokenOperations.get_token(token))
    
    if not token_data:
        return render_template_string(ERROR_TEMPLATE,
            message="Token invalid, expired, or already used",
            bot_link=f"https://t.me/{get_user_bot_username()}?start=newToken"
        )
    
    # Check if token is expired (2 days)
    created_at = token_data["created_at"]
    if datetime.utcnow() - created_at > timedelta(days=Config.TOKEN_EXPIRY_DAYS):
        loop.run_until_complete(TokenOperations.delete_token(token))
        return render_template_string(ERROR_TEMPLATE,
            message="Token expired",
            bot_link=f"https://t.me/{get_user_bot_username()}?start=newToken"
        )
    
    # Check if token already used
    if token_data["status"] in ["verified", "bypassed"]:
        return render_template_string(ERROR_TEMPLATE,
            message="Token already used",
            bot_link=f"https://t.me/{get_user_bot_username()}?start=newToken"
        )
    
    # Bypass detection checks
    created_at = token_data["created_at"]
    time_diff = datetime.utcnow() - created_at
    
    # Check 1: Time difference must be at least 2 minutes
    if time_diff < timedelta(minutes=2):
        # Bypass detected: Too fast
        loop.run_until_complete(TokenOperations.update_token_status(token, "bypassed"))
        unique_id = token_data["unique_id"]
        user_id = token_data["created_by"]
        bot_username = get_user_bot_username()
        redirect_url = f"https://t.me/{bot_username}?start=verify_{unique_id}_{user_id}"
        
        return render_template_string(REDIRECT_TEMPLATE,
            redirect_url=redirect_url,
            status="bypassed",
            delay=3
        )
    
    # Check 2: Cross-origin check
    referer = request.headers.get('Referer', '')
    whitelist_domains = URLShortener.get_whitelist_domains()
    
    is_whitelisted = False
    if referer:
        for domain in whitelist_domains:
            if domain in referer:
                is_whitelisted = True
                break
    
    if not is_whitelisted:
        # Bypass detected: Invalid cross-origin
        loop.run_until_complete(TokenOperations.update_token_status(token, "bypassed"))
        unique_id = token_data["unique_id"]
        user_id = token_data["created_by"]
        bot_username = get_user_bot_username()
        redirect_url = f"https://t.me/{bot_username}?start=verify_{unique_id}_{user_id}"
        
        return render_template_string(REDIRECT_TEMPLATE,
            redirect_url=redirect_url,
            status="bypassed",
            delay=3
        )
    
    # All checks passed - Mark as verified
    loop.run_until_complete(TokenOperations.update_token_status(token, "verified"))
    unique_id = token_data["unique_id"]
    user_id = token_data["created_by"]
    bot_username = get_user_bot_username()
    redirect_url = f"https://t.me/{bot_username}?start=verify_{unique_id}_{user_id}"
    
    loop.close()
    
    return render_template_string(REDIRECT_TEMPLATE,
        redirect_url=redirect_url,
        status="verified",
        delay=3
    )

# ===========================================
# HTML Templates
# ===========================================

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Error</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .error-icon {
            font-size: 80px;
            margin-bottom: 20px;
            animation: shake 0.5s ease-in-out;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        h1 {
            color: #e74c3c;
            font-size: 28px;
            margin-bottom: 15px;
        }
        
        p {
            color: #555;
            font-size: 16px;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .message {
            background: #fee;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
            text-align: left;
        }
        
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .info {
            margin-top: 20px;
            font-size: 14px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>Token Error</h1>
        <div class="message">
            <strong>{{ message }}</strong>
        </div>
        <p>To get another token, click the button below:</p>
        <a href="{{ bot_link }}" class="btn">🔄 Get New Token</a>
        <p class="info">You can generate up to 15 tokens per day</p>
    </div>
</body>
</html>
'''

REDIRECT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting...</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 50px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .status-icon {
            font-size: 100px;
            margin-bottom: 20px;
            animation: bounce 1s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 15px;
        }
        
        p {
            color: #666;
            font-size: 18px;
            margin-bottom: 30px;
        }
        
        .countdown {
            font-size: 60px;
            font-weight: bold;
            color: #667eea;
            margin: 30px 0;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .loader {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status-verified {
            color: #27ae60;
        }
        
        .status-bypassed {
            color: #e74c3c;
        }
    </style>
    <script>
        let countdown = {{ delay }};
        
        function updateCountdown() {
            document.getElementById('countdown').textContent = countdown;
            countdown--;
            
            if (countdown < 0) {
                window.location.href = '{{ redirect_url }}';
            }
        }
        
        setInterval(updateCountdown, 1000);
        updateCountdown();
    </script>
</head>
<body>
    <div class="container">
        {% if status == 'verified' %}
            <div class="status-icon">✅</div>
            <h1 class="status-verified">Verification Successful!</h1>
            <p>You will be redirected to the bot...</p>
        {% else %}
            <div class="status-icon">⚠️</div>
            <h1 class="status-bypassed">Bypass Detected!</h1>
            <p>Please complete the verification properly...</p>
        {% endif %}
        
        <div class="countdown" id="countdown">{{ delay }}</div>
        <div class="loader"></div>
        <p style="font-size: 14px; color: #888;">If not redirected automatically, <a href="{{ redirect_url }}">click here</a></p>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=True
    )