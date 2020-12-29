WSGI Types for Python
=====================

This is an attempt to bring some type safety to WSGI applications using Python's new
typing features (TypedDicts, Protocols). It seems to work OK but may still be full of gaps,
holes, bugs, missteps, etc. It helped bring a lot of extra safety to a couple of places
that really needed it though, and seemed to remain quite stable for a couple of months.

This is implemented as a Python module, rather than MyPy stubs, as it represents a
protocol things can satisfy rather than a set of types for something concrete.

This package came together during an exploration documented here:
https://github.com/python/mypy/issues/7654

Define a callable application as a class:

.. code-block:: py

    import wsgitypes
    
    class MyApplication(wsgitypes.Application):
        def __call__(
            self, 
            environ: wsgitypes.Environ,
            start_response: wsgitypes.StartResponse,
        ) -> wsgitypes.Response:
            my_header = environ.get("REQUEST_METHOD", "")
            return []

Environ should be type-safe:

.. code-block:: py

    class MyApplication(wsgitypes.Application):
        def __call__(
            self,
            environ: wsgitypes.Environ,
            start_response: wsgitypes.StartResponse,
        ) -> wsgitypes.Response:
            environ["wsgi.input"] # Good
            environ["wsgi.unpot"] # BORK! MyPy will catch this.
            return []

You can define your own extensions to ``Environ`` using ``TypedDict`` inheritance,
like so:

.. code-block:: py

    class MyEnviron(wsgitypes.Environ):
        HTTP_X_MY_HEADER: t.Optional[str]
    
    class MyApplication(wsgitypes.Application):
        def __call__(
            self,
            environ: MyEnviron,
            start_response: wsgitypes.StartResponse,
        ) -> wsgitypes.Response:
            environ = typing.cast(MyEnviron, environ)
            environ.get("HTTP_X_MY_HEADER") # Good
            return []

Note that you need to use ``typing.cast`` to convert the incoming `Environ` to your
derived version. An attempt was made to use a type param for Environ, but it wasn't
viable (even with GVR helping!): https://github.com/python/mypy/issues/7654

