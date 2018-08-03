#coding:utf-8
import collector
import argparse
from bs4 import BeautifulSoup,Comment
from bs4 import BeautifulSoup, NavigableString, Declaration, Comment

def write_content(filepath,filename,content):
    filepath = filepath + "/" + filename

    with open(filepath,"w") as f:
        f.write(content)


def getNavigableStrings(soup):
    if isinstance(soup, NavigableString):
        if type(soup) not in (Comment, Declaration) and soup.strip():
            yield soup
    elif soup.name not in ('script', 'style'):
        for c in soup.contents:
            for g in getNavigableStrings(c):
                yield g


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy_host",help="set Tor proxy host")
    parser.add_argument("--proxy_port",help="set Tor proxy port")
    parser.add_argument("--filepath",help="set output filepath")
    args = parser.parse_args()

    host = args.proxy_host
    port = args.proxy_port
    filepath = args.filepath

    cl = collector.Collector(host,port)
    hs_lst = cl.get_link()

    for hs_url in hs_lst:
        try:
            output = ""
            content = cl.get_content(hs_url)
            soup = BeautifulSoup(content,"html.parser")

            """
            for comment in soup(text=lambda x:isinstance(x,Comment)):
                comment.extract()

            for script in soup.find_all('script',src=False):
                script.decompose()

            for text in soup.find_all(text=True):
                if text.strip():
                    output += text
            """

            output = '\n'.join(getNavigableStrings(soup))

            if output != "":
                write_content(filepath,hs_url,output)
        except:
            pass
