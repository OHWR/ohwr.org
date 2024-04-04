# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load, parse and validate newsfeed."""

import datetime
import re
from typing import Optional
from urllib import request
from urllib.error import URLError

from base import URL, BaseModelForbidExtra
from pydantic import ValidationError


class NewsfeedError(Exception):
    """Failed to load, parse or validate newsfeed."""


class News(BaseModelForbidExtra):
    """Parses and validates news."""

    title: str
    date: datetime.date
    images: Optional[list[URL]] = None
    topics: Optional[list[str]] = None
    content: Optional[str] = None  # noqa: WPS110

    @classmethod
    def load(cls, md: str):  # noqa: WPS210
        """
        Parse and validate Markdown news.

        Parameters:
            md: Markdown news.

        Returns:
            News object.

        Raises:
            NewsfeedError: if parsing or validating the news fails.
        """
        try:
            title, after_title = md.split('\n', 1)
        except ValueError as title_error:
            msg = 'Failed to fetch title from news item:\n↳ {0}'
            raise NewsfeedError(msg.format(title_error))

        try:
            date, after_date = after_title.strip().split('\n', 1)
        except ValueError as date_error:
            msg = 'Failed to fetch date from news item:\n↳ {0}'
            raise NewsfeedError(msg.format(date_error))
        date = datetime.date.fromisoformat(date)

        image_pattern = r'!\[.*?\]\((.*?)\)'
        images = re.findall(image_pattern, after_date)
        content = re.sub(image_pattern, '', after_date).strip()  # noqa: WPS110

        try:
            return cls(title=title, date=date, images=images, content=content)
        except ValidationError as news_error:
            msg = 'News is not valid:\n↳ {0}'
            raise NewsfeedError(msg.format(news_error))


class Newsfeed(BaseModelForbidExtra):
    """Loads, parses and validates newsfeed."""

    news: Optional[list[News]] = None

    @classmethod
    def from_url(cls, url: str):
        """
        Load a Markdown newsfeed from a URL.

        Parameters:
            url: Markdown newsfeed URL.

        Returns:
            Newsfeed object.

        Raises:
            NewsfeedError: if loading the newsfeed fails.
        """
        try:
            with request.urlopen(url) as response:  # noqa: S310
                return cls.load(response.read().decode('utf-8'))
        except URLError as error:
            msg = 'Failed to request {0}:\n↳ {1}'
            raise NewsfeedError(msg.format(url, error))

    @classmethod
    def load(cls, md: str):  # noqa: WPS210
        """
        Parse and validate Markdown newsfeed.

        Parameters:
            md: Markdown newsfeed.

        Returns:
            Newsfeed object.

        Raises:
            NewsfeedError: if parsing or validating the newsfeed fails.
        """
        try:
            md = re.sub('<!--(.*?)-->', '', md, flags=re.DOTALL).strip()
        except ValueError as re_error:
            msg = 'Failed to process Markdown content:\n↳ {0}'
            raise NewsfeedError(msg.format(re_error))

        news_list = []
        news_items = md.split('## ')[1:]
        for news_item in news_items:
            news = News.load(news_item)
            news_list.append(news)

        try:
            return cls(news=news_list)
        except ValidationError as validation_error:
            msg = 'Newsfeed is not valid:\n↳ {0}'
            raise NewsfeedError(msg.format(validation_error))
