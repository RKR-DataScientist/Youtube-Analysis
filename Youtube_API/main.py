#from youtube_api import YTAPI
from yts_api import YTstats


'''
yt.get_channel_statistics()
yt.get_channel_video_data()
yt.dump()

'''
API_KEY = "AIzaSyCoFJ3E1tDN1jHgxfgedVVxYnZJisoQzoU"
channel_id = input("Paste Channel ID :- ")

yt = YTstats(API_KEY, channel_id)
yt.get_channel_video_data()
yt.get_channel_statistics()
yt.dump()


