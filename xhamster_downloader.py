"""xhamster Downloader"""
import sys
from requests import get
from bs4 import BeautifulSoup
import m3u8
from tqdm import tqdm

# How To Use
# 1. Open terminal/powershell/cmd
# 2. python xhamster_downloader.py "url"


def get_title(soup, quality):
    """Video Name"""
    title_ = soup.find('main').find('h1').text
    video_name_ = f'{title_} {quality}.mp4'
    return video_name_


def downloader(video_name, v_quality, m3u8_seg_uris, base_url):
    """Downloader"""
    print('Name : ', video_name)
    print('Quality : ', v_quality)
    try:
        with open(file=video_name, mode='wb') as f:
            # Note : it's parts not MB
            for segement in tqdm(range(len(m3u8_seg_uris)), desc='Downloading In Parts '):
                segment_base_url = m3u8_seg_uris[segement]
                segment_url = f'{base_url}/{segment_base_url}'
                video_part = get(segment_url)
                f.write(video_part.content)
                # chunk_size = 256
                # for chunk in video_part.iter_content(chunk_size=chunk_size):
                #     f.write(chunk)
        print('Done')
    except:
        print('Download failed')

    print('\n')


def xhamster(xhamster_url: str):
    """xhamster"""
    r = get(xhamster_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    main_video_url = soup.find_all(
        'link', attrs={'rel': 'preload'})[1].get('href')
    r = get(main_video_url)

    m3u8_main_data = m3u8.loads(r.text)
    m3u8_quality_uris = [playlist['uri']
                         for playlist in m3u8_main_data.data['playlists']]

    # quality selection
    quality = [qlty.split('.')[0] for qlty in m3u8_quality_uris]
    available_qualities = '\n'.join([f'{index}.{q}' for index,
                                     q in enumerate(quality, start=1)])
    print(f"Quality Available :\n{available_qualities}")

    quality_selection = input(
        'Type to select quality eg. 1 2 (you can type single or multiple) : ')
    # convert to list eg.[1,2,3]
    quality_selection = quality_selection.split(' ')
    # filter out empty items
    quality_selection = list(filter(None, quality_selection))
    # converting to item to int in a list
    quality_selection = list(map(int, quality_selection))

    qualities = ' '.join([quality[s_q - 1] for s_q in quality_selection])
    print(f"""
        Total Downloads : {len(quality_selection)}
        Quality Selected : {qualities}
    """)

    for single_quality in quality_selection:
        playlist_uri = m3u8_quality_uris[single_quality - 1]
        main_list = main_video_url.split('/')
        main_list = main_list[:len(main_list) - 1]
        base_url = '/'.join(main_list)
        res_url = f'{base_url}/{playlist_uri}'
        r = get(res_url)
        playlist = m3u8.loads(r.text)

        m3u8_segment_uris = [segment['uri']
                             for segment in playlist.data['segments']]
        v_quality = quality[single_quality - 1]
        video_name = get_title(soup, v_quality)
        downloader(video_name, v_quality, m3u8_segment_uris, base_url)


if __name__ == '__main__':
    # URL = 'https://xhamster18.desi/videos/compilation-cum-in-mouth-over-50-times-huge-multiple-cum-compilation-4k-xhNXeDo'

    try:
        URL = sys.argv[1]
        xhamster(URL)
    except IndexError:
        print('NO URL Given\n')
        print("""
      ----How To Use----
1. Open terminal/powershell/cmd
2. python xhamster_downloader.py "url"
        """)
