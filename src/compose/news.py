# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load, parse and validate news."""

import re
from datetime import date
from typing import Optional
from urllib import request
from dataclasses import dataclass

from markdown import Markdown, Section
from pydantic import BaseModel, Field
from url import URL


class NewsError(Exception):
    """Failed to load, parse, validate or dump news."""


class News(BaseModel, extra='forbid'):
    title: str
    date: date
    topics: Optional[list[str]] = Field(default_factory=list)
    images: Optional[list[URL]] = None
    content: Optional[str] = None

    @classmethod
    def from_markdown(cls, section: Section):
        date_str = re.match(r'^.*?(?=\n|$)', section.markdown).group()
        topics_pattern = re.compile(r'^(?:.*\n){2}Topics: (.+?)(?=\n|$)')
        topics_match = topics_pattern.search(section.markdown)
        if topics_match:
            topics = list(map(str.strip, topics_match.group(1).split(',')))
            content = '\n'.join(section.markdown.splitlines()[3:])
        else:
            topics = []
            content = '\n'.join(section.markdown.splitlines()[1:])
        return cls(
            title=section.heading,
            date=date.fromisoformat(date_str),
            topics=topics,
            images=re.findall(r'\!\[.*?\]\((.*?)\)', content),
            content=re.sub(r'\!\[.*?\]\(.*?\)', '', content),
        )

@dataclass
class Newsfeed(object):
    news: list[News]

    @classmethod
    def from_url(cls, url: str):
        with request.urlopen(url) as response:
            return cls.from_markdown(Markdown(response.read().decode()))

    @classmethod
    def from_markdown(cls, markdown: Markdown):
        newsfeed_section = markdown.find('News')
        if not newsfeed_section:
            raise NewsError('No News section found in Markdown')
        news = []
        for news_section in newsfeed_section.sections:
            news.append(News.from_markdown(news_section))
        return cls(news)
