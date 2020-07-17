#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import json
import requests
import mysql.connector
from bs4 import BeautifulSoup

class Error(Exception):
    pass

class RequestError(Error):
    pass

class ScriptureMap:
    """
    """
    url = "https://www.churchofjesuschrist.org/content/api/v2"
    scripture_map = {
        "pgp": {
            "name": "pearl of great price",
            "books": {
                "Moses": "moses",
                "Abraham": "abr",
                "Joseph Smith—Matthew": "js-m",
                "Joseph Smith—History": "js-h",
                "Articles of Faith": "a-of-f"
            }
        },
        "ot": {
            "name": "old testament",
            "books": {
                "Genesis": "gen",
                "Exodus": "ex",
                "Leviticus": "lev",
                "Numbers": "num",
                "Deuteronomy": "deut",
                "Joshua": "josh",
                "Judges": "judg",
                "Ruth": "ruth",
                "1 Samuel": "1-sam",
                "2 Samuel": "2-sam",
                "1 Kings": "1-kgs",
                "2 Kings": "2-kgs",
                "1 Chronicles": "1-chr",
                "2 Chronicles": "2-chr",
                "Ezra": "ezra",
                "Nehemiah": "neh",
                "Esther": "esth",
                "Job": "job",
                "Psalms": "ps",
                "Psalm": "ps",
                "Proverbs": "prov",
                "Ecclesiastes": "eccl",
                "Song of Solomon": "song",
                "Isaiah": "isa",
                "Jeremiah": "jer",
                "Lamentations": "lam",
                "Ezekiel": "ezek",
                "Daniel": "dan",
                "Hosea": "hosea",
                "Joel": "joel",
                "Amos": "amos",
                "Obadiah": "obad",
                "Jonah": "jonah",
                "Micah": "micah",
                "Nahum": "nahum",
                "Habakkuk": "hab",
                "Zephaniah": "zeph",
                "Haggai": "hag",
                "Zechariah": "zech",
                "Malachi": "mal"
            }
        },
        "nt": {
            "name": "new testament",
            "books": {
                "Matthew": "matt",
                "Mark": "mark",
                "Luke": "luke",
                "John": "john",
                "Acts": "acts",
                "Romans": "rom",
                "1 Corinthians": "1-cor",
                "2 Corinthians": "2-cor",
                "Galatians": "gal",
                "Ephesians": "eph",
                "Philippians": "philip",
                "Colossians": "col",
                "1 Thessalonians": "1-thes",
                "2 Thessalonians": "2-thes",
                "1 Timothy": "1-tim",
                "2 Timothy": "2-tim",
                "Titus": "titus",
                "Philemon": "philem",
                "Hebrews": "heb",
                "James": "james",
                "1 Peter": "1-pet",
                "2 Peter": "2-pet",
                "1 John": "1-jn",
                "2 John": "2-jn",
                "3 John": "3-jn",
                "Jude": "jude",
                "Revelation": "rev"
            }
        },
        "bofm": {
            "name": "book of mormon",
            "books": {
                "Title Page": "title-page",
                "Title Page of the Book of Mormon": "bofm-title",
                "Introduction": "introduction",
                "Testimony of Three Witnesses": "three",
                "Testimony of Eight Witnesses": "eight",
                "Testimony of the Prophet Joseph Smith": "js",
                "1 Nephi": "1-ne",
                "2 Nephi": "2-ne",
                "Jacob": "jacob",
                "Enos": "enos",
                "Jarom": "jarom",
                "Omni": "omni",
                "Words of Mormon": "w-of-m",
                "Mosiah": "mosiah",
                "Alma": "alma",
                "Helaman": "hel",
                "3 Nephi": "3-ne",
                "4 Nephi": "4-ne",
                "Mormon": "morm",
                "Ether": "ether",
                "Moroni": "moro"
            }
        },
        "dc-testament": {
            "name": "doctrine and covanants",
            "books": {
                "Doctrine and Covenants": "dc",
                "D&C": "dc"
            }
        },
    }

    def __init__(self, language="eng"):
        self.keys = ["ref", "uri", "text"]
        self.language = language
        self.scriptures = []

    def _reference_to_uri(self, reference):
        for publication, info in self.scripture_map.items():
            for book in info["books"]:
                if book in reference:
                    book_name = info["books"][book]
                    reference = reference.replace(book,"").strip()
                    chapter, verses = reference.split(":")
                    # verses = self.process_verses(verses)
                    verses = verses.replace("–", "-").replace(" ", "")
                    return f"/{self.language}/scriptures/{publication}/{book_name}/{chapter.strip()}.{verses.strip()}"

    def _get_text_from_content(self, content):
        text = []
        for c in content:
            t = c['markup']
            t = re.sub(r'<sup(.*?)</sup>', '',  t)
            t = t = re.sub(r'<span class=\"para-mark\">&#xB6; </span>', '',  t)
            soup = BeautifulSoup(t, "html.parser")
            text.append(soup.text)
        return "\n".join(text)

    def _make_request(self, uri_list):
        """
        Send POST reqeust and returns json data if the returned status_code
        is 200 (OK).
        """
        r = requests.post(self.url, data={ "uris": uri_list })
        if r.status_code != 200:
            raise RequestError(f"ERROR: Request returned status code of {r.status_code}")
        return r.json()

    def _process_request(self, response):
        """
        Processes the response and saves the text to the scripture data.
        """
        for uri, payload in response.items():
            for idx, data  in enumerate(self.scriptures):
                if uri == data['uri']:
                    data['text'] = self._get_text_from_content(payload['content'])
                    break

    def _chunk(self, l, maxlen=50):
        """
        Only 50 uris can be sent at a time. This limits the uris sent to _chunks
        of size `maxlen` (Default: 50) to prevent issues with overloading uris
        while also reducing the numbers of requests sent.
        """
        return [l[i:i + maxlen] for i in range(0, len(l), maxlen)]

    def _check_for_duplicates(self):
        """
        Checks for duplicate scriptures.
        """
        duplicates = 0
        text_list = self.get("text")
        for idx, val in enumerate(text_list):
            if val in text_list[idx + 1:]:
                duplicates += 1
        print(f"Found {duplicates} duplicate scriptures")

    def set_uris(self):
        for idx, reference in enumerate(self.scriptures):
            self.scriptures[idx] = {
                "ref": reference['ref'],
                "uri": self._reference_to_uri(reference['ref']),
                "text": ""
            }

    def set_text(self, text):
        for idx, reference in enumerate(self.scriptures):
            self.scriptures[idx] = {
                "ref": reference['ref'],
                "uri": reference['uri'],
                "text": text
            }

    def add(self, ref):
        if type(ref) is list:
            self.scriptures.extend([{
                "ref": r,
                "uri": "",
                "text": ""
            } for r in ref])
        else:
            self.scriptures.append({
                "ref": ref,
                "uri": "",
                "text": ""
            })

    def uri_to_text(self):
        """
        Takes uri list and obtains text from the API.
        """
        uri_list = self.get("uri")
        for uris in self._chunk(uri_list):
            response = self._make_request(uris)
            self._process_request(response)

    def get(self, key):
        """
        Returns all data from self.scriptures based on key.
        """
        if key in self.keys:
            return [data[key] for data in self.scriptures]

    def print_verses(self):
        for data in self.scriptures:
            ref = data['ref']
            text = data['text']
            if text != "":
                print(f"-- {ref} --\n{text}\n")

    def to_sql(self, conn, cursor):
        """

        """
        table_name = 'scriptures'
        for data in self.scriptures:
            ref = data['ref']
            text = data['text']
            uri = data['uri']
            is_used = False
            if text != "":
                cursor.execute(f"INSERT INTO `{table_name}` (reference, text, is_used, uri) VALUES (%s, %s, %s, %s)", (ref, text, is_used, uri))
        conn.commit()

    def run(self):
        """
        If the references have been added, this method will set uris and then
        obtain the text.
        """
        self.set_uris()
        self.uri_to_text()
