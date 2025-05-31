import requests
import json
import re
import time
import random

class InstagramScraper:
    def __init__(self):
        # Use a more browser-like user agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.instagram.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        # Use Instagram's API endpoint directly
        self.api_url = "https://i.instagram.com/api/v1/users/web_profile_info/?username={}"
        # Backup URL if API fails
        self.backup_url = "https://www.instagram.com/{}/"

    def scrape_profile(self, username):
        """Scrape Instagram profile information using Instagram's API"""
        print(f"Scraping profile for: {username}")
        
        # Initialize profile data with default values
        profile_data = {
            "average_comments": "Not Available",
            "average_likes": "Not Available",
            "biography": "Not Available",
            "category": "Not Available",
            "country": "ID",  # Default to Indonesia as per example
            "engagement_rate": 0,
            "followers": "0",
            "following": "0",
            "full_name": "Not Available",
            "is_professional_account": "Not Available",
            "is_verified": "false",
            "platform": "instagram",
            "posts": "0",
            "profile_pic_url_hd": "",
            "instagram_url": f"https://www.instagram.com/{username}/",  # Changed key name to avoid duplication
            "username": username
        }
        
        # Try to get data from Instagram API
        api_data = self._fetch_from_api(username)
        if api_data and 'data' in api_data and 'user' in api_data['data']:
            print("Successfully fetched data from Instagram API")
            return self._parse_api_data(api_data, profile_data)
        
        # If API fails, try to scrape from Instagram website
        print("API fetch failed, trying to scrape from Instagram website...")
        web_data = self._fetch_from_web(username)
        if web_data:
            return self._parse_web_data(web_data, profile_data)
        
        # If all methods fail, return the default profile data
        print("All scraping methods failed. Returning default data.")
        return profile_data
    
    def _fetch_from_api(self, username):
        """Fetch profile data from Instagram's API"""
        url = self.api_url.format(username)
        print(f"Fetching from API: {url}")
        
        try:
            # Add a random delay to avoid rate limiting
            time.sleep(random.uniform(1.5, 3.0))
            
            # Add Instagram-specific headers
            api_headers = self.headers.copy()
            api_headers['x-ig-app-id'] = '936619743392459'  # Instagram web app ID
            
            response = requests.get(url, headers=api_headers)
            response.raise_for_status()
            
            # Save the API response for debugging
            with open(f"{username}_api_response.json", "w", encoding="utf-8") as f:
                json.dump(response.json(), f, indent=2, ensure_ascii=False)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from API: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding API response: {e}")
            return None
    
    def _fetch_from_web(self, username):
        """Fetch profile data from Instagram website"""
        url = self.backup_url.format(username)
        print(f"Fetching from web: {url}")
        
        try:
            # Add a random delay to avoid rate limiting
            time.sleep(random.uniform(2.0, 4.0))
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save the HTML response for debugging
            with open(f"{username}_web_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Look for the shared_data JSON in the HTML
            match = re.search(r'<script type="text/javascript">window\._sharedData = (.*?);</script>', response.text)
            if match:
                shared_data = json.loads(match.group(1))
                return shared_data
            
            # Alternative: look for the additional_data JSON
            match = re.search(r'window\.__additionalDataLoaded\([^,]+,\s*(\{.*?\})\);', response.text)
            if match:
                additional_data = json.loads(match.group(1))
                return additional_data
            
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from web: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding web response: {e}")
            return None
    
    def _parse_api_data(self, api_data, profile_data):
        """Parse profile data from Instagram API response"""
        try:
            user = api_data['data']['user']
            
            # Extract basic profile information
            if 'full_name' in user and user['full_name']:
                profile_data['full_name'] = user['full_name']
                print(f"Found full name: {profile_data['full_name']}")
            
            if 'biography' in user and user['biography']:
                profile_data['biography'] = user['biography']
                print(f"Found biography: {profile_data['biography'][:50]}...")
            
            if 'is_verified' in user:
                profile_data['is_verified'] = str(user['is_verified']).lower()
                print(f"Verification status: {profile_data['is_verified']}")
            
            if 'profile_pic_url_hd' in user and user['profile_pic_url_hd']:
                profile_data['profile_pic_url_hd'] = user['profile_pic_url_hd']
                print(f"Found profile picture URL")
            
            # Extract counts
            if 'edge_followed_by' in user and 'count' in user['edge_followed_by']:
                profile_data['followers'] = str(user['edge_followed_by']['count'])
                print(f"Found followers count: {profile_data['followers']}")
            
            if 'edge_follow' in user and 'count' in user['edge_follow']:
                profile_data['following'] = str(user['edge_follow']['count'])
                print(f"Found following count: {profile_data['following']}")
            
            if 'edge_owner_to_timeline_media' in user and 'count' in user['edge_owner_to_timeline_media']:
                profile_data['posts'] = str(user['edge_owner_to_timeline_media']['count'])
                print(f"Found posts count: {profile_data['posts']}")
            
            # Extract category if available
            if 'category_name' in user and user['category_name']:
                profile_data['category'] = user['category_name']
                print(f"Found category: {profile_data['category']}")
            
            # Check if it's a professional account
            if 'is_business_account' in user:
                profile_data['is_professional_account'] = str(user['is_business_account']).lower()
                print(f"Professional account status: {profile_data['is_professional_account']}")
            
            # Extract engagement metrics from recent posts
            if 'edge_owner_to_timeline_media' in user and 'edges' in user['edge_owner_to_timeline_media']:
                posts = user['edge_owner_to_timeline_media']['edges']
                like_counts = []
                comment_counts = []
                
                for post in posts:
                    if 'node' in post:
                        node = post['node']
                        if 'edge_liked_by' in node and 'count' in node['edge_liked_by']:
                            like_counts.append(node['edge_liked_by']['count'])
                        if 'edge_media_to_comment' in node and 'count' in node['edge_media_to_comment']:
                            comment_counts.append(node['edge_media_to_comment']['count'])
                
                # Calculate average likes and comments
                if like_counts:
                    avg_likes = sum(like_counts) / len(like_counts)
                    profile_data['average_likes'] = str(int(avg_likes))
                    print(f"Average likes: {profile_data['average_likes']}")
                
                if comment_counts:
                    avg_comments = sum(comment_counts) / len(comment_counts)
                    profile_data['average_comments'] = str(int(avg_comments))
                    print(f"Average comments: {profile_data['average_comments']}")
            
            # Calculate engagement rate
            if profile_data['followers'] != "0" and profile_data['average_likes'] != "Not Available":
                followers_count = self._extract_number(profile_data['followers'])
                avg_likes_count = self._extract_number(profile_data['average_likes'])
                
                if followers_count > 0:
                    engagement_rate = (avg_likes_count / followers_count) * 100
                    profile_data['engagement_rate'] = round(engagement_rate, 1)
                    print(f"Calculated engagement rate: {profile_data['engagement_rate']}%")
            
        except Exception as e:
            print(f"Error parsing API data: {e}")
            import traceback
            traceback.print_exc()
        
        return profile_data
    
    def _parse_web_data(self, web_data, profile_data):
        """Parse profile data from Instagram website response"""
        try:
            # Try to find user data in different possible locations in the JSON
            user = None
            
            # Check in entry_data.ProfilePage[0].graphql.user
            if 'entry_data' in web_data and 'ProfilePage' in web_data['entry_data'] and len(web_data['entry_data']['ProfilePage']) > 0:
                if 'graphql' in web_data['entry_data']['ProfilePage'][0] and 'user' in web_data['entry_data']['ProfilePage'][0]['graphql']:
                    user = web_data['entry_data']['ProfilePage'][0]['graphql']['user']
            
            # Check in graphql.user
            if not user and 'graphql' in web_data and 'user' in web_data['graphql']:
                user = web_data['graphql']['user']
            
            # Check in data.user
            if not user and 'data' in web_data and 'user' in web_data['data']:
                user = web_data['data']['user']
            
            if not user:
                print("Could not find user data in web response")
                return profile_data
            
            # Extract basic profile information
            if 'full_name' in user and user['full_name']:
                profile_data['full_name'] = user['full_name']
                print(f"Found full name: {profile_data['full_name']}")
            
            if 'biography' in user and user['biography']:
                profile_data['biography'] = user['biography']
                print(f"Found biography: {profile_data['biography'][:50]}...")
            
            if 'is_verified' in user:
                profile_data['is_verified'] = str(user['is_verified']).lower()
                print(f"Verification status: {profile_data['is_verified']}")
            
            if 'profile_pic_url_hd' in user and user['profile_pic_url_hd']:
                profile_data['profile_pic_url_hd'] = user['profile_pic_url_hd']
                print(f"Found profile picture URL")
            
            # Extract counts
            if 'edge_followed_by' in user and 'count' in user['edge_followed_by']:
                profile_data['followers'] = str(user['edge_followed_by']['count'])
                print(f"Found followers count: {profile_data['followers']}")
            
            if 'edge_follow' in user and 'count' in user['edge_follow']:
                profile_data['following'] = str(user['edge_follow']['count'])
                print(f"Found following count: {profile_data['following']}")
            
            if 'edge_owner_to_timeline_media' in user and 'count' in user['edge_owner_to_timeline_media']:
                profile_data['posts'] = str(user['edge_owner_to_timeline_media']['count'])
                print(f"Found posts count: {profile_data['posts']}")
            
            # Extract category if available
            if 'category_name' in user and user['category_name']:
                profile_data['category'] = user['category_name']
                print(f"Found category: {profile_data['category']}")
            
            # Check if it's a professional account
            if 'is_business_account' in user:
                profile_data['is_professional_account'] = str(user['is_business_account']).lower()
                print(f"Professional account status: {profile_data['is_professional_account']}")
            
            # Extract engagement metrics from recent posts
            if 'edge_owner_to_timeline_media' in user and 'edges' in user['edge_owner_to_timeline_media']:
                posts = user['edge_owner_to_timeline_media']['edges']
                like_counts = []
                comment_counts = []
                
                for post in posts:
                    if 'node' in post:
                        node = post['node']
                        if 'edge_liked_by' in node and 'count' in node['edge_liked_by']:
                            like_counts.append(node['edge_liked_by']['count'])
                        if 'edge_media_to_comment' in node and 'count' in node['edge_media_to_comment']:
                            comment_counts.append(node['edge_media_to_comment']['count'])
                
                # Calculate average likes and comments
                if like_counts:
                    avg_likes = sum(like_counts) / len(like_counts)
                    profile_data['average_likes'] = str(int(avg_likes))
                    print(f"Average likes: {profile_data['average_likes']}")
                
                if comment_counts:
                    avg_comments = sum(comment_counts) / len(comment_counts)
                    profile_data['average_comments'] = str(int(avg_comments))
                    print(f"Average comments: {profile_data['average_comments']}")
            
            # Calculate engagement rate
            if profile_data['followers'] != "0" and profile_data['average_likes'] != "Not Available":
                followers_count = self._extract_number(profile_data['followers'])
                avg_likes_count = self._extract_number(profile_data['average_likes'])
                
                if followers_count > 0:
                    engagement_rate = (avg_likes_count / followers_count) * 100
                    profile_data['engagement_rate'] = round(engagement_rate, 1)
                    print(f"Calculated engagement rate: {profile_data['engagement_rate']}%")
            
        except Exception as e:
            print(f"Error parsing web data: {e}")
            import traceback
            traceback.print_exc()
        
        return profile_data
    
    def _extract_number(self, text):
        """Extract numeric value from text that may contain K, M, B suffixes"""
        if not text or text == "Not Available":
            return 0
        
        # If it's already a number, just convert it
        if isinstance(text, (int, float)):
            return int(text)
        
        text = str(text).strip().replace(',', '')
        
        # Extract the numeric part with potential suffix
        match = re.search(r'([\d.]+)\s*([KMBkmb])?', text)
        if not match:
            return 0
        
        value = float(match.group(1))
        suffix = match.group(2).upper() if match.group(2) else ''
        
        if suffix == 'K':
            value *= 1000
        elif suffix == 'M':
            value *= 1000000
        elif suffix == 'B':
            value *= 1000000000
        
        return int(value)
    
def main():
    # Get username from command line arguments
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <username>")
        sys.exit(1)
    
    username = sys.argv[1].strip()
    print(f"Scraping profile for username: {username}")
    
    # Create scraper instance and scrape profile
    scraper = InstagramScraper()
    profile_data = scraper.scrape_profile(username)
    
    # Ensure we don't have duplicate keys in the output
    if 'url' in profile_data:
        # If 'url' exists but 'instagram_url' doesn't, copy the value
        if 'instagram_url' not in profile_data:
            profile_data['instagram_url'] = profile_data['url']
        # Remove the duplicate 'url' key
        del profile_data['url']
    
    # Print profile data
    print("\nProfile Data:")
    # Convert to JSON string first to avoid duplicate output
    json_str = json.dumps(profile_data, indent=2, ensure_ascii=False)
    print(json_str)
    
    # Save profile data to file
    output_file = f"{username}_profile.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json_str)
    
    print(f"\nProfile data saved to {output_file}")

if __name__ == "__main__":
    main()