import traceback, time, datetime
import subprocess, os


def get_timestamps(pbf):
	timestamps = []
	try:
		with open(pbf, 'rb') as f:
			contents = f.read().decode('utf-8' , errors='replace').replace('\x00', '')
			content_split = contents.split('=')
			for content in content_split:
				if '*' in content:
					element = content.split('*')[0]
					if int(element) < 1000:
						element = '1000' 
					timestamp = datetime.timedelta(seconds=(int(element[:-3])))
					timestamps.append(timestamp)
	except:
		return timestamps
	return timestamps


def get_fileName(extensions):
	files = []
	for file in os.listdir(os.getcwd()):
		for extension in extensions:
			if file.endswith(extension):
				files.append(file)
	return files

def is_video(filename):
	try:
		result = subprocess.check_output(
		f'ffprobe -loglevel quiet -show_entries stream=codec_type -of json "{filename}"',
		shell=True).decode()
		if 'video' or 'audio' in result:
			return True
		else:
			return False
	except:
		return False

def get_partial_filename(file):
	partial_filename = ''.join(file.split('.')[:-1])
	return partial_filename


def get_videos(pbfs_partial_filenames):
	videos = set()
	for file in os.listdir(os.getcwd()):
		filename = get_partial_filename(file)
		if filename in pbfs_partial_filenames:
			if is_video(file):
				videos.add(file)
	return videos


def main():
	print('Initializing....')
	extensions = {}
	start_time = time.time()
	pbfs = get_fileName(['.pbf'])
	filenames = set()
	for pbf in pbfs:
		filename = get_partial_filename(pbf)
		filenames.add(filename)
	videos = get_videos(filenames)
	for video in videos:
		video_name = video[:video.rfind('.')]
		extension_name = video[video.rfind('.'):]
		extensions[video_name] = extension_name
	print('Initialization complete!\n')
	for file in pbfs:
		timestamps = get_timestamps(file)
		file_name = file.replace('.pbf', '')
		if timestamps:
			print('Extracting from ', file_name+extension_name+'....')
		try:
			extension_name = extensions[file_name]
		except KeyError:
			continue
		segment_count = 0
		while timestamps:
			try:
				start = timestamps.pop(0)
				end = timestamps.pop(0)
				segment_count += 1
			except IndexError:
				continue
			duration = end - start
			duration_second = duration.seconds
			sufix = str(start).replace(':', '')
			command = 'ffmpeg -loglevel quiet -ss ' +str(start) +' -i ' \
			+ '"'+file_name+extension_name+'"' +' -t ' \
			+str(duration_second) +' -c copy ' + '"'+file_name+'"' \
			+'_'+sufix+extension_name
			subprocess.call(command, shell=True)
		if segment_count:
			print('Extraction from  ', file_name+extension_name+' completed!\n')
	end_time = time.time()
	print('Process took', str(datetime.timedelta(seconds=end_time - start_time)).split('.')[0])


if __name__ == '__main__':
	main()
	