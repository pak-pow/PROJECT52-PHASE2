import re

class UserAgentParser:
    @staticmethod
    def parse_user_agent(ua_string: str) -> dict:
        if not ua_string or not isinstance(ua_string, str):
            return {
                "device_type": "desktop",
                "browser": "Other",
                "os": "Other"
            }

        ua = ua_string.lower()

        # 1. Device Type Detection
        device_type = "desktop"
        if "tablet" in ua or "ipad" in ua or ("android" in ua and "mobile" not in ua):
            device_type = "tablet"
        elif "mobile" in ua or "iphone" in ua or "ipod" in ua or "android" in ua:
            device_type = "mobile"

        # 2. Browser Detection
        browser = "Other"
        if "edg/" in ua or "edge/" in ua:
            browser = "Edge"
        elif "opr/" in ua or "opera" in ua:
            browser = "Opera"
        elif "chrome" in ua and "chromium" not in ua:
            browser = "Chrome"
        elif "firefox" in ua:
            browser = "Firefox"
        elif "safari" in ua and "chrome" not in ua:
            browser = "Safari"

        # 3. Operating System Detection
        os_name = "Other"
        if "windows" in ua:
            os_name = "Windows"
        elif "iphone" in ua or "ipad" in ua or "ipod" in ua:
            os_name = "iOS"
        elif "macintosh" in ua or "mac os x" in ua:
            os_name = "MacOS"
        elif "android" in ua:
            os_name = "Android"
        elif "linux" in ua:
            os_name = "Linux"

        return {
            "device_type": device_type,
            "browser": browser,
            "os": os_name
        }

    @staticmethod
    def categorize_referrer(referrer: str) -> str:
        if not referrer or not isinstance(referrer, str) or referrer.strip() == "":
            return "Direct"
        
        ref = referrer.lower().strip()

        if any(s in ref for s in ["google.", "bing.", "duckduckgo.", "yahoo.", "baidu."]):
            return "Search Engines"
        if any(s in ref for s in ["twitter.com", "t.co", "x.com", "facebook.com", "instagram.com", "linkedin.com", "reddit.com"]):
            return "Social Media"
        if any(s in ref for s in ["github.com", "gitlab.com", "stackoverflow.com", "news.ycombinator.com"]):
            return "Developer / Tech"
        
        return "Referral / Other"
