import typing as t
import typing_extensions as tx


"""
Experimental WSGI types

https://www.python.org/dev/peps/pep-3333/
https://wsgi.readthedocs.io/en/latest/definitions.html#
"""


# The server is not required to read past the client's specified
# Content-Length, and should simulate an end-of-file condition if the
# application attempts to read past that point. The application should not
# attempt to read more data than is specified by the CONTENT_LENGTH
# variable.
#
# A server should return empty bytestrings from any attempt to read from an
# empty or exhausted input stream.
class InputStream(tx.Protocol):
    # A server should allow read() to be called without an argument, and return
    # the remainder of the client's input stream.
    def read(self, size: t.Optional[int] = None) -> bytes: ...

    # Servers should support the optional "size" argument to readline(), but as
    # in WSGI 1.0, they are allowed to omit support for it.
    #
    # (In WSGI 1.0, the size argument was not supported, on the grounds that it
    # might have been complex to implement, and was not often used in
    # practice... but then the cgi module started using it, and so practical
    # servers had to start supporting it anyway!)
    def readline(self, size: t.Optional[int] = None) -> bytes: ...

    # Note that the hint argument to readlines() is optional for both caller
    # and implementer. The application is free not to supply it, and the server
    # or gateway is free to ignore it.
    def readlines(self, hint: int = -1) -> t.List[bytes]: ...

    def __iter__(self) -> t.Iterator[bytes]: ...


class ErrorStream(tx.Protocol):
    # XXX: this is documented in the PEP as 'write(str)', which suggests it's a
    # "native string" rather than a "bytestring", but it's not clear. The
    # WSGI.org docs suggest this should be a "text-mode stream", lending
    # further weight to 'str':
    def write(self, b: str) -> None: ...

    def writelines(self, seq: t.Sequence[str]) -> None: ...

    # Since the errors stream may not be rewound, servers and gateways are free
    # to forward write operations immediately, without buffering. In this case,
    # the flush() method may be a no-op. Portable applications, however, cannot
    # assume that output is unbuffered or that flush() is a no-op. They must
    # call flush() if they need to ensure that output has in fact been written.
    # (For example, to minimize intermingling of data from multiple processes
    # writing to the same error log.)
    def flush(self) -> None: ...


# https://wsgi.readthedocs.io/en/latest/definitions.html
StandardEnviron = tx.TypedDict("StandardEnviron", {
    # The HTTP request method, such as GET or POST. This cannot ever be an
    # empty string, and so is always required.
    "REQUEST_METHOD": str,

    # The remainder of the request URL’s “path”, designating the virtual
    # “location” of the request’s target within the application. This may be an
    # empty string, if the request URL targets the application root and does
    # not have a trailing slash.
    "PATH_INFO": str,

    # The initial portion of the request URL’s “path” that corresponds to the
    # application object, so that the application knows its virtual “location”.
    # This may be an empty string, if the application corresponds to the “root”
    # of the server.
    "SCRIPT_NAME": str,

    # The portion of the request URL that follows the “?”, if any. May be empty
    # or absent.
    "QUERY_STRING": t.Optional[str],

    # The contents of any Content-Type fields in the HTTP request. May be empty
    # or absent.
    "CONTENT_TYPE": t.Optional[str],
})


WSGIEnviron = tx.TypedDict("WSGIEnviron", {
    # The tuple (1, 0), representing WSGI version 1.0.
    "wsgi.version": t.Tuple[int, int],

    # A string representing the “scheme” portion of the URL at which the
    # application is being invoked. Normally, this will have the value “http”
    # or “https”, as appropriate.
    "wsgi.url_scheme": str,

    # An input stream (file-like object) from which the HTTP request body can
    # be read. (The server or gateway may perform reads on-demand as requested
    # by the application, or it may pre- read the client’s request body and
    # buffer it in-memory or on disk, or use any other technique for providing
    # such an input stream, according to its preference.)
    "wsgi.input": InputStream,

    # An output stream (file-like object) to which error output can be written,
    # for the purpose of recording program or other errors in a standardized
    # and possibly centralized location. This should be a “text mode” stream;
    # i.e., applications should use “n” as a line ending, and assume that it
    # will be converted to the correct line ending by the server/gateway.
    #
    # For many servers, wsgi.errors will be the server’s main error log.
    # Alternatively, this may be sys.stderr, or a log file of some sort. The
    # server’s documentation should include an explanation of how to configure
    # this or where to find the recorded output. A server or gateway may supply
    # different error streams to different applications, if this is desired
    "wsgi.output": ErrorStream,

    # This value should evaluate true if the application object may be
    # simultaneously invoked by another thread in the same process, and should
    # evaluate false otherwise.
    "wsgi.multithread": bool,

    # This value should evaluate true if an equivalent application object may
    # be simultaneously invoked by another process, and should evaluate false
    # otherwise.
    "wsgi.multiprocess": bool,

    # This value should evaluate true if the server or gateway expects (but
    # does not guarantee!) that the application will only be invoked this one
    # time during the life of its containing process. Normally, this will only
    # be true for a gateway based on CGI (or something similar).
    "wsgi.run_once": bool,
})


class Environ(StandardEnviron, WSGIEnviron):
    pass


Headers = t.List[t.Tuple[str, str]]
StartResponse = t.Callable[[str, Headers], None]
Response = t.Iterable[bytes]

# When called by the server, the application object must return an iterable
# yielding zero or more bytestrings. This can be accomplished in a variety of
# ways, such as by returning a list of bytestrings, or by the application being
# a generator function that yields bytestrings, or by the application being a
# class whose instances are iterable. Regardless of how it is accomplished, the
# application object must always return an iterable yielding zero or more
# bytestrings.
#
# NOTE: when using this from mypy, you may wish to extend your Environ. This
# can be done using TypedDict inheritance, though you will need to use a
# `cast` before you use your inherited Environ:
#
#   class MoreSpecificEnviron(wsgitypes.Environ):
#       HTTP_X_EXTRA: str
#
#   class MyApplication(wsgitypes.Application):
#       def __call__(self, environ: wsgitypes.Environ, start_response: wsgitypes.StartResponse) -> wsgitypes.Response:
#           environ = typing.cast(MoreSpecificEnviron, environ)
#           environ.get("HTTP_X_EXTRA")
#           return []
# 
# An attempt was made to use a type param for Environ, but it wasn't viable:
# https://github.com/python/mypy/issues/7654
#       
class Application(tx.Protocol):
    def __call__(self, environ: Environ, start_response: StartResponse) -> Response:
        ...

