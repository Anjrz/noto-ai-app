# ads.py
from kivmob import KivMob, TestIds

class AdsManager:
    def __init__(self, app):
        self.ads = KivMob(TestIds.APP)
        self.ads.new_banner(TestIds.BANNER, top_pos=True)
        self.ads.request_banner()
        self.ads.show_banner()
