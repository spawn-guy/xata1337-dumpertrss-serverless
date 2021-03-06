import datetime
import os
from email.utils import formatdate

import requests
from dateutil.parser import parse
from feedgen.feed import FeedGenerator

DUMPERT_HOST = os.getenv("DUMPERT_HOST")
DUMPERT_API_ROOT = os.getenv("DUMPERT_API_ROOT")
FEED_TYPE = os.getenv("FEED_TYPE")
OUTPUT_TYPE = os.getenv("OUTPUT_TYPE")


def create_tags_html(tags: str):
    result = ""

    for tag in tags.split(" "):
        result += f"<a href=\"{DUMPERT_HOST}/tag/{tag}\">{tag}</a> "

    return result.strip()


def match_source_variant(variants, version="stream"):
    match = next(
        (
            source_variant for source_variant in variants
            if source_variant["version"] == version
        ),
        None  # return None if there is no match
    )
    return match


def compose_description_video(item):
    source_variant_match = match_source_variant(variants=item['media'][0]['variants'], version="stream")
    tags_str = create_tags_html(item["tags"])

    result = f"<video " \
             f"preload=\"auto\" " \
             f"poster=\"{item['still']}\" " \
             f"loop muted autoplay=\"autoplay\" controls=\"controls\" " \
             f"style=\"width:100%;height:auto;margin:0 auto;\" autoplay>" \
             f"<source " \
             f"src=\"{source_variant_match['uri']}\" " \
             f"type=\"application/x-mpegURL\"" \
             f">" \
             f"</video>" \
             f"<br />" \
             f"{item['description']}" \
             f"<p>Tags: {tags_str}" \
             f"<p>{item['stats']['kudos_total']} kudos, {item['stats']['views_total']} views.</p>"

    return result


def compose_description_image(item):
    source_variant_match = match_source_variant(variants=item['media'][0]['variants'], version="foto")
    tags_str = create_tags_html(item["tags"])

    result = f"<img src=\"{source_variant_match['uri']}\" />" \
             f"<br />" \
             f"{item['description']}" \
             f"<p>Tags: {tags_str}" \
             f"<p>{item['stats']['kudos_total']} kudos, {item['stats']['views_total']} views.</p>"

    return result


def main(event, context):
    # load json from API: https://github.com/Reaguurders/API-Spec
    d_response = requests.get(url=f"{DUMPERT_API_ROOT}{FEED_TYPE}")

    d_data = d_response.json()

    if not d_data["items"]:
        exit(1)

    # prepare generator
    fg = FeedGenerator()

    # fg.id("http://lernfunk.de/media/654321")
    # fg.logo("http://ex.com/logo.jpg")
    fg.title("dumpert.nl - Laatste 50 embeded-entries")
    fg.subtitle("dumpert.nl RSS Embed Feed")
    fg.link(href=f"{DUMPERT_HOST}/rss", rel="self")
    # fg.link(href="https://spawn-guy.name", rel="alternate")
    fg.language("nl")

    date_updated = datetime.datetime.utcfromtimestamp(d_data["gentime"])
    if date_updated.utcoffset() is None:
        date_updated = date_updated.replace(tzinfo=datetime.timezone.utc)
        
    fg.updated(date_updated)

    # fg.author(name="John Doe", email="jdoe@example.com")
    # fg.contributor( name="John Doe", email="jdoe@example.com" )

    for item in d_data["items"]:
        fe = fg.add_entry()

        if item["nsfw"]:
            fe.title(f"NSFW: {item['title']}")
        else:
            fe.title(item["title"])

        description = compose_description_video(item) \
            if item["media_type"] == "VIDEO" \
            else compose_description_image(item)

        fe.description(description)

        # fe.category()
        item_date_published = parse(item["date"])
        if item_date_published.utcoffset() is None:
            item_date_published = item_date_published.replace(tzinfo=datetime.timezone.utc)

        fe.published(item_date_published)

        web_url = f"{DUMPERT_HOST}/item/{item['id']}"
        # fe.id(web_url)
        fe.link(href=web_url)
        fe.guid(guid=web_url, permalink=True)

    # output result
    content_type = "application/xml"

    if OUTPUT_TYPE == "atom":
        content_type = "application/atom+xml"
        # Get the ATOM feed as string.
        # py38: returns Bytes, unless encoding="unicode"
        feed_encoded = fg.atom_str()
    else:
        content_type = "application/rss+xml"
        # Get the RSS feed as string
        # py38: returns Bytes, unless encoding="unicode"
        feed_encoded = fg.rss_str()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Last-Modified": formatdate(
                timeval=d_data["gentime"],
                localtime=False,
                usegmt=True
            )
        },
        "body": feed_encoded
    }


if __name__ == "__main__":
    main(None, None)
