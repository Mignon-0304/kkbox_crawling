import os
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
from urllib.error import URLError
from urllib.error import HTTPError
import shutil
import warnings
warnings.filterwarnings('ignore')

orpath=os.getcwd()
'''
前置作業：搜尋歌手 > 進入主頁面 > 進入熱門歌曲頁面
'''

# 執行後輸入歌手名稱，成為網頁搜尋提示詞
keyword = input('請輸入歌手名稱：')
resultUrl = "https://www.kkbox.com/tw/tc/search?q=" + quote(keyword)
html = urlopen(resultUrl).read().decode(encoding='utf-8')
searchObj = BeautifulSoup(html, "html.parser")
topTag = searchObj.find('div', class_='top-result-artist')

# 進入歌手主頁面 > 熱門歌曲頁面
url = ''
if topTag is None:
  print('查無此歌手')
else:
  artist = topTag.find('mark-text').get_text()
  print('最佳搜尋結果：', artist)
  urlTag = topTag.find('a')
  singerUrl = urlTag['href']
  
  html = urlopen(singerUrl).read().decode(encoding='utf-8')
  listObj = BeautifulSoup(html, "html.parser")
  seeAllTag = listObj.find('a', class_='see-all') #查看完整熱門歌單
  url = seeAllTag['href']

'''
在熱門歌曲頁面，爬取所需資料
'''
# 鎖定要爬取的網頁
if url == '':
  url = "https://www.kkbox.com/tw/tc/song-list/4qdLMDHW9u3pW-oxn6BQ=="
  print('未輸入指定歌手，預設歌手:韋禮安')


html = urlopen(url).read().decode(encoding='utf-8')
soup = BeautifulSoup(html, "html.parser")

# 爬取歌手姓名
tag_singer = soup.find("div", class_="creator")
singer = tag_singer.get('title')

# 爬取每一個歌曲區塊
tag_songs = soup.findAll("div", class_="song")


songs = []  # 儲存歌曲名稱的串列
paths = {}  # 儲存歌曲URL的字典，用歌曲名稱提取超連結
'''
爬取每一首歌的歌名及頁面超連結
'''

for tag_song in tag_songs:
  songtitle = tag_song.get('title')
  songurl = tag_song.find('a').get('href')
  songs.append(songtitle)
  paths[songtitle] = songurl

  

# 新增存放歌詞檔案的資料夾，命名為歌手名
if not os.path.isdir(singer):
  os.mkdir(singer)
os.chdir(singer) # 執行程式的位置轉移到這位歌手的資料夾內


'''
儲存爬取到的資料
'''

# 新增存放所有熱門歌曲名稱的檔案 
f = open(singer + '.txt', "w")  # 建立檔案
print('{}在kkbox上共有{}首歌曲'.format(singer, len(songs)), file=f)
for i in range(len(songs)):
  print('{}.{}'.format(i + 1, songs[i]), file=f)
f.close()  # 關閉檔案

with open('{}.txt'.format(singer)) as f: # 輸出歌曲
  html=''
  data=f.read()
  print('\n'+data)

'''
輪流進入歌曲網頁爬歌詞
'''

print('讀取歌詞中，請稍候...')

# 進入每首歌的網址爬取歌詞
for i in range(len(songs)):
  song = songs[i]
  path = paths[song]
  html = urlopen(path).read().decode(encoding='utf-8')
  searchObj = BeautifulSoup(html, "html.parser")
  topTag = searchObj.find('div', class_='lyrics')
  lyricss = topTag.get_text()
  try: #有時會爬取失敗！就略過那首歌
    f = open(song + '.txt', "w")  # 建立檔案
    f.write(lyricss)
    f.close()
    fpath=os.path.relpath('{}'.format(singer))
    file_path = os.path.join(fpath, song + '.txt')
  except FileNotFoundError:
    print('')
  
  
  
  
  try:
    html = urlopen(path).read().decode(encoding='utf-8')
  except (HTTPError, URLError) as e:
    print('網頁錯誤！', e)
    continue

soup = BeautifulSoup(html, "html.parser")

print('\n歌詞讀取完畢。\n')
while(True):
  whichsong=input('從以上歌單複製歌名獲得歌詞，或輸入0結束：')
  if whichsong=='0':
    print('Have a wonderful day!\nBest wishes\n'+'張又琦')
    break
  
  whichsong += '.txt' # 把input變成可以搜尋的樣子
  
  if os.path.isfile(whichsong): # 如果這份文字檔存在的話：
    with open(whichsong,"r") as f:
      ly=f.readlines()
      if ly[2]=='這首歌曲暫無歌詞，歡迎您投稿認養！\n':  # 不用幫kkbox推銷，所以替換掉
        print('\n這首歌曲暫無歌詞!\n')
      else:
        file = open(whichsong,"r").read() # 有歌詞的話就read整段歌詞出來
        print(file)
  else:
    print('提取歌詞失敗或輸入錯誤，再一次') # 不認識input內容
    continue
    
os.chdir(orpath) # 把執行程式的位置轉換到最外面一層
shutil.rmtree(singer) # 把這個歌手的資料夾連同裡面的文件全部刪掉