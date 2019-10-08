Experimental WSGI Types for Python
==================================

This is an attempt to bring some type safety to WSGI applications using Python's new
typing features (TypedDicts, Protocols). It seems to work OK but it'll be full of gaps,
holes, bugs, missteps, etc. I would not recommend depending on it.

This is implemented as a Python module, rather than MyPy stubs, as it represents a
protocol things can satisfy rather than a set of types for something concrete.

This package came together during an exploration documented here:
https://github.com/python/mypy/issues/7654

Define your own extensions to ``Environ`` like so::

    class MyEnviron(wsgitypes.Environ):
        HTTP_X_MY_HEADER: t.Optional[str]

Define a callable application as a class::

    class MyApplication(wsgitypes.Application[MyEnviron]):
        def __call__(
            self, 
            environ: MyEnviron,
            start_response: wsgitypes.StartResponse,
        ) -> wsgitypes.ResponseBody:
            my_header = environ.get("HTTP_X_MY_HEADER", "")
            return []

Environ should be type-safe::

    class MyApplication(wsgitypes.Application[MyEnviron]):
        def __call__(self, environ: MyEnviron, start_response: wsgitypes.StartResponse) -> wsgitypes.ResponseBody:
            environ["wsgi.input"] # Good
            environ["wsgi.unpot"] # BORK! MyPy will catch this.
            return []

