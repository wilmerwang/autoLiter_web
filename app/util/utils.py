import re 
import os 
import requests 
import logging

import feedparser
import urllib3
from retrying import retry
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
from urllib import parse
from unidecode import unidecode
from bs4 import BeautifulSoup 

from config import PROXY

# log config
logging.basicConfig()
logger = logging.getLogger('Sci-Hub')
logger.setLevel(logging.DEBUG)

urllib3.disable_warnings()
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class metaExtracter(object):
    def __init__(self):
        pass 

    def check_string(self, re_exp, str):
        res = re.search(re_exp, str)
        if res:
            return True
        else:
            return False

    def _classify(self, identifier):
        """
        Classify the type of identifier:
        arxivId - arxivId
        doi - digital object identifier
        """
        if self.check_string(r'10\.[0-9]{4}/.*', identifier):
            return 'doi'
        else:
            return 'arxivId'

    def doi2bib(self, doi):
        bare_url = "http://api.crossref.org/"
        # url = "{}works/{}/transform/application/x-bibtex"
        # TODO: url cannot return journal name
        url = "{}works/{}"
        url = url.format(bare_url, doi)
        
        try:
            r = requests.get(url)
            # found = False if r.status_code != 200 else True
            # bib = str(r.content, "utf-8")

            # if found:
            # bib_database = bibtexparser.loads(bib)
            # return bib_database.entries[0]
            bib = r.json()['message']
            pub_date = [str(i) for i in bib['published']["date-parts"][0]]
            pub_date = '-'.join(pub_date)

            authors = ' and '.join([i["family"]+" "+i['given'] for i in bib['author'] if "family" and "given" in i.keys()])

            if bib['short-container-title']:
                journal = bib['short-container-title'][0]
            else:
                journal = bib['container-title'][0]

            bib_dict = {
                "title": bib['title'][0],
                "author": authors,
                "journal": journal,
                "year": pub_date,
                "url": bib["URL"],
                "pdf_link": bib["link"][0]["URL"],
                "cited_count": bib["is-referenced-by-count"]
            }
            
            return bib_dict
        except:
            logger.info("DOI: {} is error.".format(doi))

    def arxivId2bib(self, arxivId):
        bare_url = "http://export.arxiv.org/api/query"

        params = "?search_query=id:"+quote(unidecode(arxivId))
        
        try:
            result = feedparser.parse(bare_url + params)
            items = result.entries
            # found = len(items) > 0

            item = items[0]
            # if found:
            if "arxiv_doi" in item:
                doi = item["arxiv_doi"]
                bib_dict = self.doi2bib(doi)
            else:
                paper_url = item.link 
                title = item.title
                journal = "arxiv"
                published = item.published.split("-")
                if len(published) > 1:
                    year = published[0]
                else: 
                    year = ' '
                
                authors = item.authors
                if len(authors) > 0:
                    first_author = authors[0]["name"].split(" ")
                    authors = " and ".join([author["name"] for author in authors])
                else:
                    first_author = authors
                    authors = authors

                bib_dict = {
                    "journal": journal,
                    "url": paper_url,
                    "title": title,
                    "year": year,
                    "author": authors,
                    "ENTRYTYPE": "article"
                }

            return bib_dict 
        except:
            logger.info("DOI: {} is error.".format(arxivId))

    def id2bib(self, identifier):
        id_type = self._classify(identifier)

        if id_type == "doi":
            bib_dict = self.doi2bib(identifier) 
        else:
            bib_dict = self.arxivId2bib(identifier) 

        return bib_dict
    
    
class urlDownload(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.available_base_url_list = self._get_available_scihub_urls()
        self.base_url = self.available_base_url_list[0] + '/'
        
    def set_proxy(self, proxy):
        '''
        set proxy for session
        :param proxy_dict:
        :return:
        '''
        if proxy:
            self.sess.proxies = {
                "http": proxy,
                "https": proxy, }

    def _get_available_scihub_urls(self):
        '''
        Finds available scihub urls via https://lovescihub.wordpress.com/
        '''
        urls = []
        res = requests.get('https://sci-hub.now.sh/')
        # res = requests.get('https://lovescihub.wordpress.com/')
        s = self._get_soup(res.content)
        for a in s.find_all('a', href=True):
            if 'sci-hub.' in a['href']:
                urls.append(a['href'])
        return urls

    def _change_base_url(self):
        if not self.available_base_url_list:
            raise Exception('Ran out of valid sci-hub urls')
        del self.available_base_url_list[0]
        self.base_url = self.available_base_url_list[0] + '/'
        logger.info("I'm changing to {}".format(self.available_base_url_list[0]))


    def check_string(self, re_exp, str):
        res = re.search(re_exp, str)
        if res:
            return True
        else:
            return False

    @retry(wait_random_min=100, wait_random_max=1000, stop_max_attempt_number=10)
    def download(self, identifier, destination='', path=None):
        """
        Downloads a paper from sci-hub given an indentifier (DOI, PMID, URL).
        Currently, this can potentially be blocked by a captcha if a certain
        limit has been reached.
        """
        data = self.fetch(identifier)
        if not 'err' in data:
            self._save(data['pdf'],
                    os.path.join(destination, path))

        return data

    def fetch(self, identifier):
        """
        Fetches the paper by first retrieving the direct link to the pdf.
        If the indentifier is a DOI, PMID, or URL pay-wall, then use Sci-Hub
        to access and download paper. Otherwise, just download paper directly.
        """
        try:
            url = self._get_direct_url(identifier)

            # verify=False is dangerous but sci-hub.io 
            # requires intermediate certificates to verify
            # and requests doesn't know how to download them.
            # as a hacky fix, you can add them to your store
            # and verifying would work. will fix this later.
            res = self.sess.get(url, verify=False)

            if res.headers['Content-Type'] != 'application/pdf':
                self._change_base_url()
                logger.info('Failed to fetch pdf with identifier %s '
                                           '(resolved url %s) due to captcha' % (identifier, url))
            else:
                return {
                    'pdf': res.content,
                    'url': url
                }
                
        except requests.exceptions.ConnectionError:
            logger.info('Cannot access {}, changing url'.format(self.available_base_url_list[0]))
            self._change_base_url()
            return {
                "err": "Failed"
            }

        except requests.exceptions.RequestException as e:
            logger.info('Failed to fetch pdf with identifier %s (resolved url %s) due to request exception.'
                       % (identifier, url))
            return {
                'err': 'Failed to fetch pdf with identifier %s (resolved url %s) due to request exception.'
                       % (identifier, url)
            }


    def _get_direct_url(self, identifier):
        """
        Finds the direct source url for a given identifier.
        """
        id_type = self._classify(identifier)

        if id_type == 'url-direct':
            return identifier
        elif id_type == 'url-non-direct':
            pass 
        elif id_type == 'arxivId':
            return "https://arxiv.org/pdf/" + identifier + ".pdf"
        else:
            return self._search_direct_url(identifier)

    def _search_direct_url(self, identifier):
        """
        Sci-Hub embeds papers in an iframe. This function finds the actual
        source url which looks something like https://moscow.sci-hub.io/.../....pdf.
        """
        res = self.sess.get(self.base_url + identifier, verify=False)
        s = self._get_soup(res.content)
        # print(s)

        embed_names = ['iframe', 'embed']
        for embed_name in embed_names:
            iframe = s.find(embed_name)
            if iframe != None:
                break 

        if iframe.get('src').startswith('//'):
            return 'https:' + iframe.get('src')
        else:
            return iframe.get('src')

    def _classify(self, identifier):
        """
        Classify the type of identifier:
        url-direct - openly accessible paper
        url-non-direct - pay-walled paper
        pmid - PubMed ID
        doi - digital object identifier
        """
        if (identifier.startswith('http') or identifier.startswith('https')):
            if identifier.endswith('pdf'):
                return 'url-direct'
            else:
                return "url-non-direct"
        elif identifier.isdigit():
            return 'pmid'
        elif self.check_string(r'10\.[0-9]{4}/.*', identifier):
            return 'doi'
        else:
            return 'arxivId'

    def _save(self, data, path):
        """
        Save a file give data and a path.
        """
        with open(path, 'wb') as f:
            f.write(data)

    def _get_soup(self, html):
        """
        Return html soup.
        """
        return BeautifulSoup(html, 'html.parser')
    

def download(paper_id, download_pdf, username):
    meta_extracter = metaExtracter()
    bib_dict = meta_extracter.id2bib(paper_id)
    
    if download_pdf == "1":
        url_download = urlDownload()
        url_download.set_proxy(PROXY)
        
        pdf_download_root = 'app/static/pdf/'
        if not os.path.exists(pdf_download_root):
            os.makedirs(pdf_download_root)
        pdf_name = bib_dict['year'] + '_' + bib_dict['title']
        pdf_name = pdf_name[:256] + '.pdf'
        pdf_path = os.path.join(pdf_download_root, pdf_name)
        dow_tag = True
        if "pdf_link" in bib_dict.keys():
            pdf_dict = url_download.fetch(bib_dict["pdf_link"])
            if "err" in pdf_dict.keys():
                try:
                    url_download.download(paper_id, destination=pdf_download_root, path=pdf_name)
                except:
                    dow_tag = False
            else:
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_dict['pdf'])
        else:
            try:
                url_download.download(paper_id, destination=pdf_download_root, path=pdf_name)
            except:
                dow_tag = False 
        
        # if 1, add pdf_path
        if dow_tag:
            bib_dict["pdf_path"] = os.path.join('/static/pdf/', pdf_name)

    return bib_dict
    

if __name__ == "__main__":
    proxy = "127.0.0.1:7890"
    doi_id = "10.1016/j.wneu.2012.11.074"
    arv_id = "2202.01351"
    
    paper_id = doi_id
    
    meta_extracter = metaExtracter()
    url_download = urlDownload()
    url_download.set_proxy(proxy)
    
    # Meta data
    bib_dict = meta_extracter.id2bib(paper_id)
    print(bib_dict)
    
    # PDF download
    if "pdf_link" in bib_dict.keys():
        pdf_dict = url_download.fetch(bib_dict["pdf_link"])
        if "err" in pdf_dict.keys():
            try:
                url_download.download(paper_id, destination='', path='test.pdf')
            except:
                print("下载失败")
                pass
    else:
        try:
            url_download.download(paper_id, destination='', path='test.pdf')
        except:
            pass 
        