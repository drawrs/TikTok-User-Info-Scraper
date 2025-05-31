from flask import Flask, request, jsonify
from TikTok import get_user_info
from Instagram import InstagramScraper
import argparse

app = Flask(__name__)

@app.route('/tiktok/user_info/<identifier>', methods=['GET'])
def api_get_user_info(identifier):
    by_id = request.args.get('by_id', 'false').lower() == 'true'
    
    try:
        user_data = get_user_info(identifier, by_id=by_id)
        if user_data:
            formatted_data = {
                'platform': 'tiktok',
                'username': user_data.get('unique_id', identifier),
                'full_name': user_data.get('nickname', 'Not Available'),
                'biography': user_data.get('signature', 'Not Available'),
                'country': user_data.get('region', 'Not Available'),
                'url': f"https://www.tiktok.com/@{user_data.get('unique_id', identifier)}",
                'category': 'Not Available',
                'followers': user_data.get('followers', 'Not Available'),
                'following': user_data.get('following', 'Not Available'),
                'posts': user_data.get('videos', 'Not Available'),
                'is_verified': user_data.get('verified', 'Not Available'),
                'is_professional_account': 'Not Available',
                'average_likes': user_data.get('likes', 'Not Available'),
                'average_comments': 'Not Available',
                'engagement_rate': user_data.get('advanced_engagement_rate', 'Not Available'),
                'profile_pic_url_hd': user_data.get('profile_pic', 'Not Available')
            }
            return jsonify(formatted_data), 200
        else:
            return jsonify({"error": "User not found or unable to fetch profile"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tiktok/engagement_rate/<identifier>', methods=['GET'])
def api_get_engagement_rate(identifier):
    by_id = request.args.get('by_id', 'false').lower() == 'true'
    
    try:
        user_data = get_user_info(identifier, by_id=by_id)
        if user_data and 'engagement_rate' in user_data:
            formatted_data = {
                'username': user_data.get('unique_id', identifier),
                'full_name': user_data.get('nickname', 'Not Available'),
                'biography': user_data.get('signature', 'Not Available'),
                'country': user_data.get('region', 'Not Available'),
                'url': f"https://www.tiktok.com/@{user_data.get('unique_id', identifier)}",
                'category': 'Not Available',
                'followers': user_data.get('followers', 'Not Available'),
                'following': user_data.get('following', 'Not Available'),
                'posts': user_data.get('videos', 'Not Available'),
                'is_verified': user_data.get('verified', 'Not Available'),
                'is_professional_account': 'Not Available',
                'average_likes': user_data.get('likes', 'Not Available'),
                'average_comments': 'Not Available',
                'engagement_rate': user_data.get('engagement_rate', 'Not Available'),
                'basic_engagement_rate': user_data.get('engagement_rate', 'Not Available'),
                'advanced_engagement_rate': user_data.get('advanced_engagement_rate', 'Not Available'),
                'profile_pic_url_hd': user_data.get('profile_pic', 'Not Available'),
                'description': {
                    'basic': "(likes / followers) * 100",
                    'advanced': "(avg likes per video / followers) * 100"
                }
            }
            return jsonify(formatted_data), 200
        else:
            return jsonify({"error": "User not found or unable to fetch profile"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/instagram/user_info/<username>', methods=['GET'])
def api_get_instagram_user_info(username):
    try:
        scraper = InstagramScraper()
        user_data = scraper.scrape_profile(username)
        
        if user_data:
            formatted_data = {
                'platform': 'instagram',
                'username': username,
                'full_name': user_data.get('full_name', 'Not Available'),
                'biography': user_data.get('biography', 'Not Available'),
                'country': 'Not Available',
                'url': f"https://www.instagram.com/{username}/",
                'category': user_data.get('category', 'Not Available'),
                'followers': user_data.get('followers', 'Not Available'),
                'following': user_data.get('following', 'Not Available'),
                'posts': user_data.get('posts', 'Not Available'),
                'is_verified': user_data.get('is_verified', 'Not Available'),
                'is_professional_account': user_data.get('is_professional_account', 'Not Available'),
                'average_likes': user_data.get('average_likes', 'Not Available'),
                'average_comments': user_data.get('average_comments', 'Not Available'),
                'engagement_rate': user_data.get('engagement_rate', 'Not Available'),
                'profile_pic_url_hd': user_data.get('profile_pic_url_hd', 'Not Available')
            }
            return jsonify(formatted_data), 200
        else:
            return jsonify({"error": "User not found or unable to fetch profile"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Social Media User Info API")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the API on.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the API on.')
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=True)