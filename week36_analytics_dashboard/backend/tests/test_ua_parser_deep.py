import pytest
from app.services.ua_parser import UserAgentParser

def test_ua_edge_browser():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["browser"] == "Edge"
    assert parsed["os"] == "Windows"
    assert parsed["device_type"] == "desktop"

def test_ua_firefox_linux():
    ua = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["browser"] == "Firefox"
    assert parsed["os"] == "Linux"
    assert parsed["device_type"] == "desktop"

def test_ua_opera_windows():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["browser"] == "Opera"
    assert parsed["os"] == "Windows"

def test_ua_android_mobile_chrome():
    ua = "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["browser"] == "Chrome"
    assert parsed["os"] == "Android"
    assert parsed["device_type"] == "mobile"

def test_ua_android_tablet():
    ua = "Mozilla/5.0 (Linux; Android 12; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["os"] == "Android"
    assert parsed["device_type"] == "tablet"

def test_ua_ipad_safari():
    ua = "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["browser"] == "Safari"
    assert parsed["os"] == "iOS"
    assert parsed["device_type"] == "tablet"

def test_ua_macos_safari():
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["browser"] == "Safari"
    assert parsed["os"] == "MacOS"
    assert parsed["device_type"] == "desktop"

def test_ua_none_or_non_string():
    assert UserAgentParser.parse_user_agent(None)["browser"] == "Other"
    assert UserAgentParser.parse_user_agent(12345)["browser"] == "Other"
    assert UserAgentParser.parse_user_agent({})["browser"] == "Other"

def test_ua_unknown_bot_string():
    ua = "Googlebot/2.1 (+http://www.google.com/bot.html)"
    parsed = UserAgentParser.parse_user_agent(ua)
    assert parsed["device_type"] == "desktop"
    assert parsed["browser"] == "Other"

def test_referrer_google_search():
    assert UserAgentParser.categorize_referrer("https://www.google.com/") == "Search Engines"
    assert UserAgentParser.categorize_referrer("https://google.co.uk/search?q=test") == "Search Engines"

def test_referrer_bing_search():
    assert UserAgentParser.categorize_referrer("https://www.bing.com/search?q=flask") == "Search Engines"

def test_referrer_duckduckgo_search():
    assert UserAgentParser.categorize_referrer("https://duckduckgo.com/?q=analytics") == "Search Engines"

def test_referrer_yahoo_search():
    assert UserAgentParser.categorize_referrer("https://search.yahoo.com/") == "Search Engines"

def test_referrer_twitter_and_x():
    assert UserAgentParser.categorize_referrer("https://twitter.com/dev/status/123") == "Social Media"
    assert UserAgentParser.categorize_referrer("https://x.com/explore") == "Social Media"
    assert UserAgentParser.categorize_referrer("https://t.co/shortlink") == "Social Media"

def test_referrer_facebook_instagram():
    assert UserAgentParser.categorize_referrer("https://m.facebook.com/") == "Social Media"
    assert UserAgentParser.categorize_referrer("https://www.instagram.com/") == "Social Media"

def test_referrer_linkedin_reddit():
    assert UserAgentParser.categorize_referrer("https://www.linkedin.com/feed/") == "Social Media"
    assert UserAgentParser.categorize_referrer("https://www.reddit.com/r/programming") == "Social Media"

def test_referrer_github_gitlab():
    assert UserAgentParser.categorize_referrer("https://github.com/trending") == "Developer / Tech"
    assert UserAgentParser.categorize_referrer("https://gitlab.com/repo") == "Developer / Tech"

def test_referrer_hackernews_stackoverflow():
    assert UserAgentParser.categorize_referrer("https://news.ycombinator.com/item?id=999") == "Developer / Tech"
    assert UserAgentParser.categorize_referrer("https://stackoverflow.com/questions/123") == "Developer / Tech"

def test_referrer_direct_variations():
    assert UserAgentParser.categorize_referrer("") == "Direct"
    assert UserAgentParser.categorize_referrer("   ") == "Direct"
    assert UserAgentParser.categorize_referrer(None) == "Direct"
    assert UserAgentParser.categorize_referrer(1234) == "Direct"

def test_referrer_other_random_website():
    assert UserAgentParser.categorize_referrer("https://random-tech-blog-123.io/post/1") == "Referral / Other"
