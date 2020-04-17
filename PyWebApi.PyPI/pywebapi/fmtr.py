# -*- coding: utf-8 -*-
"""
    fmtr.py
    This module implements the conversion from the result object returned by the function to the requested media type.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT (See LICENSE file in the repository root for details)
"""

from collections import Iterable
from abc import ABCMeta, abstractmethod


def _str_iterable_to_set(str_iterable) -> set:
    if str_iterable:
        if isinstance(str_iterable, Iterable):
            if isinstance(str_iterable, str):
                str_iterable = str_iterable.split(',')
            return set(filter(None, map(lambda mt: mt.strip().lower(), str_iterable)))
    return set()


class MediaTypeFormatter(metaclass=ABCMeta):
    """ This is the abstract base class for the concrete class of MediaTypeFormatter """

    @property
    @abstractmethod
    def supported_media_types(self) -> Iterable:
        """ This property should return a list of media types supported by this class """
        pass


    def can_support_media_types(this, media_types:str) -> set:
        """ This function can be used to discover which media types expected by the request can be supported by this MediaTypeFormatter class

            :param media_types:  The media type(s) expected by current request - it usually comes from the 'Accept' header, separated by commas between multiple media types.
            :return:  An intersection set between the media types expected by the request and the media types supported by this class.
        """
        supported_media_types = this.supported_media_types
        if not supported_media_types:
            raise NotImplementedError(f"property 'supported_media_types(self)' is not defined in {rept(this.__class__.__name__)}")

        if isinstance(media_types, str):
            mt_set = _str_iterable_to_set(media_types)
            if mt_set:
                sp_set = _str_iterable_to_set(supported_media_types)
                return sp_set & mt_set
            else:
                return set()
        else:
            raise TypeError(f"the 'media_types' argument passed in ({repr(media_types)}) is not a string")


    @abstractmethod
    def format(self, obj, media_type:str, **kwargs):
        """ This function provides a concrete implementation of converting the original result object to the target media type content

            :param obj:  The original result object.
            :param media_type:  The target media type.
            :param kwargs:  Other optional keyworded arguments will be passed to the provider that implements the format conversion.
            :return:  The converted content for response
        """
        pass


class MediaTypeFormatterManager(object):
    """ This class manages all media type formatters that will be needed for responses. Pick the appropriate media type formatter for each request.

        :param default_formatter:  The default MediaTypeFormatter can be registered when initializing this manager class, or it can be registered separately later.
    """

    def __init__(self, default_formatter:MediaTypeFormatter=None):
        self._register = []
        self._default_formatter = None

        if default_formatter:
            self.register(default_formatter, True)


    def register(self, new_formatter:MediaTypeFormatter, set_as_default:False):
        """ This function is used to register a new MediaTypeFormatter to the MediaTypeFormatterManager. 
            If the media types supported by the newly registered MediaTypeFormatter can cover an existing one, the old one will be replaced by the new one.

            :param new_formatter:  A new MediaTypeFormatter to be registered.
            :param set_as_default:  A boolean value indicates whether this formatter is set as the default formatter.
        """
        if not isinstance(new_formatter, MediaTypeFormatter):
            raise TypeError("The class of 'new_formatter' to be registered must be inherited from the abstract base class MediaTypeFormatter")

        new_mts = _str_iterable_to_set(new_formatter.supported_media_types)
        if not new_mts:
            raise TypeError(f"the {rept(new_formatter.__class__.__name__)} to be registered must support at least one media type")

        i = len(self._register) - 1
        while i >= 0:
            mtf = self._register[i]
            if new_mts.issuperset(mtf):
                self._register[i] = new_formatter
                break
            i -= 1

        if i < 0:
            self._register.append(new_formatter)

        if set_as_default:
            self._default_formatter = new_formatter


    @property
    def default_formatter(self) -> MediaTypeFormatter:
        """ The default media type formatter """
        if self._default_formatter:
            return self._default_formatter
        else:
            raise NotImplementedError("the default MediaTypeFormatter has not been registered")


    def _get_formatter(self, media_types:str):
        if not self._register:
            raise NotImplementedError("no MediaTypeFormatter has been registered")

        if media_types:
            for mtf in self._register:
                ss = mtf.can_support_media_types(media_types)
                if ss:
                    return (mtf, ss.pop())

        return (self.default_formatter, self.default_formatter.supported_media_types[0])


    def respond_as(self, obj, media_types:str, response_headers:dict):
        """ This function picks a registered MediaTypeFormatter which matches the media type expected by the request, 
            and converts the original result object to the target media type content

            :param obj:  The original result object.
            :param media_types:  The media type(s) expected by current request - it usually comes from the 'Accept' header, separated by commas between multiple media types.
            :param response_headers:  the response.headers.dict - if this argument is a dict container, the final matched media type information will be set back to the 'Content-Type' header.
            :return:  The converted content for response
        """
        formatter, media_type = self._get_formatter(media_types)

        if isinstance(response_headers, dict):
            response_headers['Content-Type'] = [media_type]

        return formatter.format(obj, media_type)
