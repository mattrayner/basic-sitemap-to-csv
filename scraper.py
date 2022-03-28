import requests
from requests import Response
import csv
import xml.etree.ElementTree as ET
from typing import List

class SitemapScraper:
  def __init__(self, list_of_base_urls: List[str], sitemap_file: str = "/sitemap.xml", output_file: str = "sites.csv"):
    self.list_of_base_urls = list_of_base_urls
    self.sitemap_file = sitemap_file
    self.output_file = output_file
    self.paths_by_base = {}

  def build_urls(self):
    for base_url in self.list_of_base_urls:
      base_url_present = (self.paths_by_base.get(base_url, None) is not None)
      if base_url_present is False:
        self.paths_by_base[base_url] = []
      
      self.__get_sitemap(base_url=base_url)
      self.__generate_csv()

  def __generate_csv(self):
    with open(self.output_file, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=',',
                              quotechar='|', quoting=csv.QUOTE_MINIMAL)
      
      lines = [["site", "url"]]

      sites = self.paths_by_base.keys()
      for site in sites:
        for path in self.paths_by_base[site]:
          lines.append([site, f'{path}'])

      writer.writerows(lines)

  def __get_sitemap(self, base_url: str) -> List[str]:
    sitemap_url = f'{base_url}{self.sitemap_file}'
 
    r: Response = requests.get(sitemap_url)
    if r.status_code != 200:
      print(f'Expecting a 200 status from {sitemap_url}, got {r.status}')
      return None

    sitemap = r.text
    root = ET.fromstring(sitemap)
    
    if root.tag == 'urlset':
      print(f'Expecting root to be urlset, got {root.tag}')
      return None

    for children in root:
      url_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}url"
      loc_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
      if children.tag != url_tag:
        print(f'Expecting child node to be {url_tag}, got {children.tag} - {children}')

      loc = next(filter(lambda child: child.tag == loc_tag, children), None)
      if loc is None:
        print('No loc object found')
        continue

      path = loc.text
      
      self.paths_by_base[base_url].append(path)

with open('base_urls.csv', newline='') as csvfile:
  urls = []
  reader = csv.DictReader(csvfile)
  for row in reader:
    print(row['url'])
    urls.append(row['url'])

  scraper = SitemapScraper(list_of_base_urls=urls)
  scraper.build_urls()
