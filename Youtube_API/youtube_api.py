import requests
import json
from tqdm import tqdm

class YTAPI:
    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_statistics = None
        self.video_data = None



    def get_channel_statistics(self):
        """Extract the channel statistics"""
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'
        #print(url)
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        #print(data)
        try:
            data = data["items"][0]["statistics"]
        except:
            data = None
        self.channel_statistics = data
        return data

    def get_channel_video_data(self):
        "Extract all video information of the channel"
        #1)get videos link of the channel
        channel_videos = self._get_channel_video(limit=50)
        print(len(channel_videos))

        # 2) get video stastistics
        parts = ["snippet", "statistics","contentDetails",]
        for video_id in tqdm(channel_videos):
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                channel_videos[video_id].update(data)

        self.video_data = channel_videos
        return channel_videos

    # get single video statistics parts information
    def _get_single_video_data(self, video_id, part):
        """
                Extract further information for a single video
                parts can be: 'snippet', 'statistics', 'contentDetails', 'topicDetails'
        """
        url = f'https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}'
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0][part]
        except KeyError as e:
            print(f'Error ! Could not get{part} part of data: \n{data}')
            data = dict()

        return data

    def _get_channel_video(self, limit=None):
        """
                Extract all videos and playlists, can check all available search pages
                channel_videos = videoId: title, publishedAt
                channel_playlists = playlistId: title, publishedAt
                return channel_videos, channel_playlists
        """
        url = f'https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}&part=snippet,id&order=date'
        if limit is not None and isinstance(limit, int):
            url +="&maxResults="+str(limit)
        vid, npt = self._get_channel_video_per_page(url)
        idx = 0
        while(npt is not None and idx < 10):
            nexturl = url + "&pageToken=" +npt
            next_vid, npt = self._get_channel_video_per_page(nexturl)
            vid.update(next_vid)
            #pl.update(next_pl)
            idx +=1

        return vid

    def _get_channel_video_per_page(self, url):
        """
                Extract all videos and playlists per page
                return channel_videos, channel_playlists, nextPageToken
        """
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        channel_videos = dict()
        #channel_playlists = dict()
        # now let's iterate the items list
        if 'items' not in data:
            print("Error ! Couldn't get correct channel data", data)
            return channel_videos, None
        # if we found data that would have every page token number
        nextPageToken = data.get("nextPageToken", None)

        # Let collect all itmes and store in list then iterate those
        item_data = data['items']
        for item in item_data:
            try:
                kind = item['id']['kind']
                if kind == 'youtube&video':
                    video_id = item['id']['videoId']
                    channel_videos[video_id] = dict()
            except KeyError:
                print('Error! Could not extract data from item:\n', item)

        return channel_videos, nextPageToken






    # Function to convert into json format
    def dump(self):
        """Dumps channel statistics and video data in a single json file"""
        if self.channel_statistics is None or self.video_data is None:
            print('data is missing!\nCall get_channel_statistics() and get_channel_video_data() first!')
            return
        # Let's make varible to store all video statics
        fused_data = {self.channel_id: {
            "channel statistics:": self.channel_statistics,
            "video data": self.video_data}}
        channel_title = self.video_data.popitem()[1].get('channelTitle', self.channel_id)
        channel_title = channel_title.replace(" ","_").lower()
        file_name = channel_title+ '.json'

        with open(file_name, 'w') as f:
            json.dump(fused_data, f, indent=4)
            print(" File Dumped to", file_name)