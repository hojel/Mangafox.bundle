PLUGIN_PREFIX   = "/photos/Mangafox"
PLUGIN_TITLE    = "Mangafox Reader"
ROOT_URL        = "http://mangafox.me"
MANGAFOX_QUERY  = ROOT_URL+"/search.php?name=%s&advopts=1"

ART         = "art-default.jpg"
ICON        = "icon-default.png"

GENRES = [
  'Action', 'Adult', 'Adventure', 'Comedy', 'Doujinshi',
  'Drama', 'Ecchi', 'Fantasy', 'Gender Bender', 'Harem',
  'Historical', 'Horror', 'Josei', 'Martial Arts', 'Mature',
  'Mecha', 'Mystery', 'One Shot', 'Psychological', 'Romance',
  'School Life', 'Sci-fi', 'Seinen', 'Shoujo', 'Shoujo Ai',
  'Shounen', 'Shounen Ai', 'Slice of Life', 'Smut', 'Sports',
  'Supernatural', 'Tragedy', 'Webtoons', 'Yaoi', 'Yuri',
]

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, ICON, ART)
  Plugin.AddViewGroup("ImageStream", viewMode="Pictures", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

  #ObjectContainer.art       = R(ART)
  ObjectContainer.title1     = PLUGIN_TITLE
  ObjectContainer.view_group = "InfoList"
  DirectoryObject.thumb      = R(ICON)

  HTTP.CacheTime = CACHE_1DAY

####################################################################################################
def MainMenu():
  oc = ObjectContainer(view_group = "InfoList")
  oc.add(DirectoryObject(key=Callback(AlphabetList), title="Alphabets"))
  oc.add(DirectoryObject(key=Callback(GenreList), title="Genres"))
  oc.add(InputDirectoryObject(key=Callback(Search), title='Search Manga', prompt='Search Manga'))
  return oc

@route(PLUGIN_PREFIX+'/alphabets')
def AlphabetList():
  oc = ObjectContainer(view_group = "List")
  oc.add( DirectoryObject(key=Callback(DirectoryList, pname='9'), title='#') )
  for pname in map(chr, range(ord('A'), ord('Z')+1)):
    oc.add( DirectoryObject(key=Callback(DirectoryList, page=1, pname=pname.lower()), title=pname) )
  return oc

@route(PLUGIN_PREFIX+'/genres')
def GenreList():
  oc = ObjectContainer(view_group = "List")
  for title in GENRES:
    pname = title.lower().replace(' ','-')
    oc.add( DirectoryObject(key=Callback(DirectoryList, page=1, pname=pname), title=title) )
  return oc

@route(PLUGIN_PREFIX+'/directory/{pname}')
def DirectoryList(page, pname):
  oc = ObjectContainer(view_group = "List")
  url = ROOT_URL+"/directory/%s/%s.htm" %(pname, page)
  try:
    html = HTML.ElementFromURL(url)
  except:
    raise Ex.MediaNotAvailable

  for node in html.xpath("//ul[@class='list']/li"):
    thumb = node.xpath(".//img")[0].get('src')
    node2 = node.xpath(".//a[@class='title']")[0]
    url = node2.get('href')
    if url[-1] == '/': url = url[:-1]
    manga = url.rsplit('/',2)[-1]
    oc.add(DirectoryObject(key=Callback(MangaPage, manga=manga), title=node2.text, thumb=thumb))

  nextpg_node = html.xpath("//div[@id='nav']/ul/li/a/span[@class='next']/..")
  if nextpg_node:
    nextpg = int(nextpg_node[0].get('href').split('.')[0])
    Log.Debug("NextPage = %d" % nextpg)
    oc.add(NextPageObject(key=Callback(DirectoryList, page=nextpg, pname=pname), title="Next Page>>"))
  return oc

@route(PLUGIN_PREFIX+'/search')
def Search(query='one piece'):
  Log.Debug("Search "+query)
  url = MANGAFOX_QUERY % String.Quote(query, usePlus=False)
  try:
    html = HTML.ElementFromURL(url)
  except:
    raise Ex.MediaExpired
  oc = ObjectContainer(view_group = "List")
  for node in html.xpath("//table[@id='listing']//a[contains(@class, 'manga_open')]"):
    url = node.get('href')
    if url[-1] == '/': url = url[:-1]
    manga = url.rsplit('/',2)[-1]
    oc.add(DirectoryObject(key=Callback(MangaPage, manga=manga), title=node.text))
  return oc

@route(PLUGIN_PREFIX+'/manga/{manga}')
def MangaPage(manga):
  oc = ObjectContainer(view_group = "List")
  url = ROOT_URL+'/manga/'+manga
  try:
    html = HTML.ElementFromURL(url, timeout=10.0)
  except:
    raise Ex.MediaNotAvailable
  for node in html.xpath("//div[@id='chapters']//a[@class='tips']"):
    url = node.get('href')
    oc.add( PhotoAlbumObject(url=url, title=node.text, thumb=None) )
  return oc
