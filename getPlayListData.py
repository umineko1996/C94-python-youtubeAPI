#!/usr/bin/python

import csv
import codecs
from datetime import datetime
import apiclient
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = {DEVELOPER_KEY}
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
				developerKey=DEVELOPER_KEY)

# 指定されたIDの再生リストに含まれている動画のIDのリストとIDをキーとした辞書を作成して返却する
def get_youtube_playlist_videos(playlist_id) :
	# 初回リクエスト
	playlistItem_request = youtube.playlistItems().list(
		part="snippet",
		playlistId=playlist_id,
		maxResults=50
	)

	videoIDs = []
	videoInfo = {}

	while True :   # すべてのデータを取得しきるまでループ
		playlistItems_result = playlistItem_request.execute()

		for playlist_item in playlistItems_result["items"] :
			title = playlist_item["snippet"]["title"]
			videoID = playlist_item["snippet"]["resourceId"]["videoId"]
			print ("%s (%s)" % (title, videoID))
			videoIDs.append(videoID)
			videoInfo[videoID] = dict(title=title)


		# MEMO 動画が50以上があるときは文字列が入っており、無いときは空になる
		next_page = playlistItems_result.get("nextPageToken", "")
		if not next_page : # 次のページが無い場合ループ終了
			break

		# 次のページがある場合次のページを指定したリクエストを作成
		playlistItem_request = youtube.playlistItems().list(
			part="snippet",
			playlistId=playlist_id,
			pageToken=next_page,
			maxResults=50
		)


	return videoIDs, videoInfo

# 指定されたIDの再生リストのタイトルを返却する
def get_youtube_playlist_title(playlist_id) :
	playlist_request = youtube.playlists().list(
		part="snippet",
		id=playlist_id
	).execute()

	playlist_resource = playlist_request.get("items", [])

	if not playlist_resource :
		print("error can't get playlist resource. playlistID : %s" % playlist_id)
		return "unknown"
	
	playlist_resource = playlist_resource[0]
	channel_title = playlist_resource["snippet"]["channelTitle"]
	playlist_title = playlist_resource["snippet"]["title"]

	return "チャンネル名：%s　再生リスト名：%s" % (channel_title, playlist_title)

# 指定された動画IDの再生回数と、再生時間を返却します。
def get_youtube_video_data(video_id) :
	videos_response = youtube.videos().list(
		part="statistics,contentDetails",
		id=video_id
	).execute()

	videos_resource = videos_response.get("items", [])
	
	if not videos_resource :
		print("error can't get videos resource. videosID : %s" % video_id)
		return 0, 0

	# 一つしかないので先頭のみ取り出す
	video_resource = videos_resource[0]

	view_count = video_resource["statistics"]["viewCount"]
	duration = video_resource["contentDetails"]["duration"]

	return view_count, duration


SPH = 60 * 60
SPM = 60
# youtubeから返される #PT#M#S の文字列を秒に変換して返却する
# MEMO とりあえず動く形にしただけで完璧じゃないので注意
def conv_second(duration) :
	hour = 0
	minute = 0
	seconds = 0

	try :
		tmp = str(duration).split("PT")[1]
		# 00の項目は単位ごとカットされた形でyoutubeから返される
		if "H" in tmp :
			tmp = str(tmp).split("H")
			hour = int(tmp[0])
			tmp = tmp[1]
		if "M" in tmp :
			tmp = str(tmp).split("M")
			minute = int(tmp[0])
			tmp = tmp[1]
		if "S" in tmp :
			seconds = int(tmp.split("S")[0])
			
		return	 hour * SPH + minute * SPM + seconds

	except :
		print("error not duration format")
		return 0


# 秒で与えられた時間を HH:mm:ss の文字列に変換して返却する
def conv_timeFormat(seconds) :
	hour = seconds // SPH
	seconds = seconds % SPH
	minute = seconds // SPM
	seconds = seconds % SPM
	
	return "%d:%02d:%02d" % (hour, minute, seconds)




if __name__ == "__main__" :
	argparser.add_argument("--id", help="PlaylistID", default="PLXIjpt4IkxKNrB-OsMmtjkcktQgGulH6D") # はんなりバリカタ！再生リストID
	args = argparser.parse_args()
	data_title = ""

	try:
		data_title = get_youtube_playlist_title(args.id)
		print (data_title)
		
		videoIDs, videoInfo = get_youtube_playlist_videos(args.id)
		
		total_view = 0
		total_time = 0
		average_view = 0
		average_time = 0

		for videoID in videoIDs :
			view,duration = get_youtube_video_data(videoID)
			total_view += int(view)
			time = conv_second(duration)
			total_time += time

			v = videoInfo[videoID]
			v["view"] = view
			v["time"] = conv_timeFormat(time)
			print("%s <%6s> %s" % (v["title"], v["view"], v["time"]))
		
		average_view = total_view // len(videoIDs)
		average_time = total_time // len(videoIDs)
		total_time = conv_timeFormat(total_time)
		average_time = conv_timeFormat(average_time)

	except HttpError as e :
		print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

	with codecs.open ("result.csv", "w", "shift_jis") as f :
		f.write("%s\n" % data_title)
		f.write("再生リスト内動画数：%s\n" % len(videoIDs))
		f.write("データ取得時間：%s\n\n" % datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
		csv_clum = ("title", "view", "time")
		header = dict(title="動画タイトル", view="再生回数", time="再生時間")
		writer = csv.DictWriter(f, csv_clum)
		writer.writerow(header)

		for videoID in videoIDs :
			writer.writerow(videoInfo[videoID])
		
		f.write("\n")
		writer.writerow(dict(title="合計", view=total_view, time=total_time))
		writer.writerow(dict(title="平均", view=average_view, time=average_time))
	print ("total Videos : %s" % len(videoIDs))
	print ("total View : %s" % total_view)
	print ("total Time : %s" % total_time)
	print ("average View : %s" % average_view)
	print ("average Time : %s" % average_time)