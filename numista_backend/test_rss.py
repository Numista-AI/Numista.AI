import feedparser
f = feedparser.parse('https://www.coinworld.com/rss/all-news.xml')
print(f'CoinWorld: {len(f.entries)} entries')
if f.entries:
    print(f'  First: {f.entries[0].title}')
f2 = feedparser.parse('https://www.numismaticnews.net/.rss/full/')
print(f'NumNews: {len(f2.entries)} entries')
if f2.entries:
    print(f'  First: {f2.entries[0].title}')
