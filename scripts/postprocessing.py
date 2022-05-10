from argparse import ArgumentParser
from pathlib import Path
import lxml.html
import shutil

parser = ArgumentParser()
parser.add_argument('raw_archive_path',
                    help="Path to the input directory containing raw archive files")
parser.add_argument(
    'site_dist_path', help="Path to the output directory where processed files should be placed")
args = parser.parse_args()

raw_archive_path = Path(args.raw_archive_path)
site_dist_path = Path(args.site_dist_path)

shutil.rmtree(site_dist_path)
shutil.copytree(raw_archive_path, site_dist_path)

# Strip analytics scripts from HTML files
html_paths = [path for path in site_dist_path.rglob(
    "*") if path.suffix == ".html"]

for html_path in html_paths:
    parsed_html = lxml.html.parse(html_path)
    cloudflare_scripts = parsed_html.xpath(
        "//script[contains(@src, 'cdn-cgi') or contains(text(), 'cdn-cgi')]")
    google_analytics_scripts = parsed_html.xpath(
        "//script[contains(text(), 'google-analytics.com') or contains(text(), '_getTracker')]")
    google_ad_scripts = parsed_html.xpath(
        "//script[contains(@src, 'googlesyndication.com') or contains(text(), 'google_ad') or contains(text(), 'googlesyndication.com')]")

    for script_element in cloudflare_scripts:
        script_element.getparent().remove(script_element)

    for script_element in google_analytics_scripts:
        script_element.getparent().remove(script_element)

    for script_element in google_ad_scripts:
        script_element.getparent().remove(script_element)

    with open(html_path, 'wb') as html_outfile:
        # Include the original meta_content_type and doctype here, as they are stripped during HTML processing
        html_outfile.write(lxml.html.tostring(parsed_html, method='html', include_meta_content_type=True,
                doctype='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'))

# Remove bundled analytics scripts
shutil.rmtree(site_dist_path / Path("cdn-cgi"))