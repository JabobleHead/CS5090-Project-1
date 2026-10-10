# Phase 2 review sheet

For each item: read the PROMPT, then the MODEL OUTPUT, then (last) the ORIGINAL. Decide `accept`, `edit` or `reject` and write it in `judgments.csv` (see docs/phase2.md). Judge whether the model's code is correct and usable for the signature/docstring, not whether it matches the original. `parses` only means it is valid Python.


---

## p2-01  (numpy/numpy/ma/extras.py)   parses: True

**PROMPT (what the model saw)**
```python
def setxor1d(ar1, ar2, assume_unique=False):
    """
    Set exclusive-or of 1-D arrays with unique elements.

    The output is always a masked array. See `numpy.setxor1d` for more details.

    See Also
    --------
    numpy.setxor1d : Equivalent function for ndarrays.

    Examples
    --------
    >>> import numpy as np
    >>> ar1 = np.ma.array([1, 2, 3, 2, 4])
    >>> ar2 = np.ma.array([2, 3, 5, 7, 5])
    >>> np.ma.setxor1d(ar1, ar2)
    masked_array(data=[1, 4, 5, 7],
                 mask=False,
           fill_value=999999)

    """
```

**MODEL OUTPUT (the body it wrote)**
```python
    if not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma.array(ar1, ar2, assume_unique=False)
    elif not assume_unique:
        return np.ma
```

**ORIGINAL BODY (for comparison only)**
```python
    if not assume_unique:
        ar1 = unique(ar1)
        ar2 = unique(ar2)

    aux = ma.concatenate((ar1, ar2), axis=None)
    if aux.size == 0:
        return aux
    aux.sort()
    auxf = aux.filled()
#    flag = ediff1d( aux, to_end = 1, to_begin = 1 ) == 0
    flag = ma.concatenate(([True], (auxf[1:] != auxf[:-1]), [True]))
#    flag2 = ediff1d( flag ) == 0
    flag2 = (flag[1:] == flag[:-1])
    return aux[flag2]
```


---

## p2-02  (werkzeug/src/werkzeug/_internal.py)   parses: True

**PROMPT (what the model saw)**
```python
def _log(type: str, message: str, *args: t.Any, **kwargs: t.Any) -> None:
    """Log a message to the 'werkzeug' logger.

    The logger is created the first time it is needed. If there is no
    level set, it is set to :data:`logging.INFO`. If there is no handler
    for the logger's effective level, a :class:`logging.StreamHandler`
    is added.
    """
```

**MODEL OUTPUT (the body it wrote)**
```python
    if isinstance(message, str):
        message = message.replace(" ", "")
    else:
        message = message.replace(" ", "")
    return message
```

**ORIGINAL BODY (for comparison only)**
```python
    global _logger

    if _logger is None:
        _logger = logging.getLogger("werkzeug")

        if _logger.level == logging.NOTSET:
            _logger.setLevel(logging.INFO)

        if not _has_level_handler(_logger):
            _logger.addHandler(_ColorStreamHandler())

    getattr(_logger, type)(message.rstrip(), *args, **kwargs)
```


---

## p2-03  (click/tests/test_chain.py)   parses: True

**PROMPT (what the model saw)**
```python
@pytest.mark.parametrize(
    ("args", "input", "expect"),
    [
        (["-f", "-"], "foo\nbar", ["foo", "bar"]),
        (["-f", "-", "strip"], "foo \n bar", ["foo", "bar"]),
        (["-f", "-", "strip", "uppercase"], "foo \n bar", ["FOO", "BAR"]),
    ],
)
def test_pipeline(runner, args, input, expect):
    @click.group(chain=True, invoke_without_command=True)
    @click.option("-f", type=click.File("r"))
```

**MODEL OUTPUT (the body it wrote)**
```python
    def cli(f):
        click.echo(f"--{arg} --{arg}")

    result = runner.invoke(cli, args, input=output)
    assert result.exit_code == 0
    assert result.output == expect
```

**ORIGINAL BODY (for comparison only)**
```python
    def cli(f):
        pass

    @cli.result_callback()
    def process_pipeline(processors, f):
        iterator = (x.rstrip("\r\n") for x in f)
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click.echo(item)

    @cli.command("uppercase")
    def make_uppercase():
        def processor(iterator):
            for line in iterator:
                yield line.upper()

        return processor

    @cli.command("strip")
    def make_strip():
        def processor(iterator):
            for line in iterator:
                yield line.strip()

        return processor

    result = runner.invoke(cli, args, input=input)
    assert not result.exception
    assert result.output.splitlines() == expect
```


---

## p2-04  (scrapy/scrapy/spiders/crawl.py)   parses: False

**PROMPT (what the model saw)**
```python
def __init__(self, *a: Any, **kw: Any):
```

**MODEL OUTPUT (the body it wrote)**
```python
    """Initialize the *a*-through*-through*-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-through-
```

**ORIGINAL BODY (for comparison only)**
```python
    super().__init__(*a, **kw)
    self._compile_rules()
    if method_is_overridden(self.__class__, CrawlSpider, "_parse_response"):
        warnings.warn(
            "The CrawlSpider._parse_response method, which the "
            f"{global_object_name(self.__class__)} class overrides, is "
            "deprecated: it will be removed in future Scrapy releases. "
            "Please override the CrawlSpider.parse_with_rules method "
            "instead.",
            ScrapyDeprecationWarning,
            stacklevel=2,
        )
```


---

## p2-05  (aiohttp/tests/test_web_middleware.py)   parses: False

**PROMPT (what the model saw)**
```python
@pytest.mark.parametrize(
    ["append_slash", "remove_slash"],
    [
        (True, False),
        (False, True),
        (False, False),
    ],
)
async def test_open_redirects(
    self, append_slash: bool, remove_slash: bool, aiohttp_client: AiohttpClient
) -> None:
```

**MODEL OUTPUT (the body it wrote)**
```python
    """Test that the redirects are not reached."""
    response = ClientResponse(
        "get",
        url,
        writer=WriterMock(),
        continue100=True,
        timer=TimerNoop(),
        traces=[],
        loop=asyncio.get_running_loop(),
        session=session,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state,
        session_state=session_state
```

**ORIGINAL BODY (for comparison only)**
```python
    async def handle(request: web.Request) -> web.StreamResponse:
        pytest.fail(
            "Security advisory 'GHSA-v6wp-4m6f-gcjg' test handler "
            "matched unexpectedly",
            pytrace=False,
        )
    app = web.Application(
        middlewares=[
            web.normalize_path_middleware(
                append_slash=append_slash, remove_slash=remove_slash
            )
        ]
    )
    app.add_routes([web.get("/", handle), web.get("/google.com", handle)])
    client = await aiohttp_client(app, server_kwargs={"skip_url_asserts": True})
    resp = await client.get("//google.com", allow_redirects=False)
    assert resp.status == 308
    assert resp.headers["Location"] == "/google.com"
    assert resp.url.query == URL("//google.com").query
```


---

## p2-06  (pydantic/pydantic-core/tests/serializers/test_ordered_dict.py)   parses: False

**PROMPT (what the model saw)**
```python
def test_ordered_dict_subclass() -> None:
```

**MODEL OUTPUT (the body it wrote)**
```python
    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class CustomDict(dict):
        pass

    class Custom
```

**ORIGINAL BODY (for comparison only)**
```python
    class MyOrderedDict(OrderedDict):
        pass

    s = SchemaSerializer(cs.ordered_dict_schema(cs.str_schema(), cs.int_schema()))
    output = s.to_python(MyOrderedDict({'a': 1}))
    assert output == OrderedDict({'a': 1})
    assert type(output) is OrderedDict
    assert s.to_json(MyOrderedDict({'a': 1})) == b'{"a":1}'
```


---

## p2-07  (scikit-learn/sklearn/linear_model/tests/test_linear_loss.py)   parses: False

**PROMPT (what the model saw)**
```python
@pytest.mark.parametrize("base_loss", LOSSES)
@pytest.mark.parametrize("fit_intercept", [False, True])
@pytest.mark.parametrize("n_features", [0, 1, 10])
@pytest.mark.parametrize("dtype", [None, np.float32, np.float64, np.int64])
def test_init_zero_coef(
    base_loss, fit_intercept, n_features, dtype, global_random_seed
):
    """Test that init_zero_coef initializes coef correctly."""
```

**MODEL OUTPUT (the body it wrote)**
```python
    rng = np.random.RandomState(global_random_seed)
    X = rng.randn(n_samples, n_features)
    y = rng.randn(n_samples, n_features)
    X_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_samples, n_features)
    y_transformed = rng.randn(n_
```

**ORIGINAL BODY (for comparison only)**
```python
    loss = LinearModelLoss(base_loss=base_loss(), fit_intercept=fit_intercept)
    rng = np.random.RandomState(global_random_seed)
    X = rng.normal(size=(5, n_features))
    coef = loss.init_zero_coef(X, dtype=dtype)
    if loss.base_loss.is_multiclass:
        n_classes = loss.base_loss.n_classes
        assert coef.shape == (n_classes, n_features + fit_intercept)
        assert coef.flags["F_CONTIGUOUS"]
    else:
        assert coef.shape == (n_features + fit_intercept,)

    if dtype is None:
        assert coef.dtype == X.dtype
    else:
        assert coef.dtype == dtype

    assert np.count_nonzero(coef) == 0
```


---

## p2-08  (jinja/src/jinja2/ext.py)   parses: True

**PROMPT (what the model saw)**
```python
def call_method(
    self,
    name: str,
    args: list[nodes.Expr] | None = None,
    kwargs: list[nodes.Keyword] | None = None,
    dyn_args: nodes.Expr | None = None,
    dyn_kwargs: nodes.Expr | None = None,
    lineno: int | None = None,
) -> nodes.Call:
    """Call a method of the extension.  This is a shortcut for
    :meth:`attr` + :class:`jinja2.nodes.Call`.
    """
```

**MODEL OUTPUT (the body it wrote)**
```python
    if name in self.args:
        return nodes.Call(name=name, args=args, kwargs=kwargs, lineno=lineno)
    else:
        return nodes.Call(name=name, args=args, kwargs=kwargs, lineno=lineno)
```

**ORIGINAL BODY (for comparison only)**
```python
    if args is None:
        args = []
    if kwargs is None:
        kwargs = []
    return nodes.Call(
        self.attr(name, lineno=lineno),
        args,
        kwargs,
        dyn_args,
        dyn_kwargs,
        lineno=lineno,
    )
```


---

## p2-09  (pillow/Tests/test_file_webp_lossless.py)   parses: False

**PROMPT (what the model saw)**
```python
def test_write_lossless_rgb(tmp_path: Path) -> None:
```

**MODEL OUTPUT (the body it wrote)**
```python
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # Actual test for gh-259
    # A
```

**ORIGINAL BODY (for comparison only)**
```python
    temp_file = tmp_path / "temp.webp"

    hopper(RGB_MODE).save(temp_file, lossless=True)

    with Image.open(temp_file) as image:
        image.load()

        assert image.mode == RGB_MODE
        assert image.size == (128, 128)
        assert image.format == "WEBP"
        image.load()

        assert_image_equal(image, hopper(RGB_MODE))
```


---

## p2-10  (httpx/tests/test_wsgi.py)   parses: False

**PROMPT (what the model saw)**
```python
def raise_exc(
    environ: WSGIEnvironment,
    start_response: StartResponse,
    exc: type[Exception] = ValueError,
) -> typing.Iterable[bytes]:
```

**MODEL OUTPUT (the body it wrote)**
```python
    """
    A WSGI environ that matches a request.

    :param start_response: The response to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc: The exception to be sent to the response.
    :param exc:
```

**ORIGINAL BODY (for comparison only)**
```python
    status = "500 Server Error"
    output = b"Nope!"

    response_headers = [
        ("Content-type", "text/plain"),
    ]

    try:
        raise exc()
    except exc:
        exc_info = sys.exc_info()
        start_response(status, response_headers, exc_info)

    return [output]
```


---

## p2-11  (django/tests/postgres_tests/test_hstore.py)   parses: True

**PROMPT (what the model saw)**
```python
def test_field_has_changed(self):
```

**MODEL OUTPUT (the body it wrote)**
```python
    class Model(BaseModel):
        a: int = Field(alias='a')

    assert Model.model_dump() == {'a': 1}
```

**ORIGINAL BODY (for comparison only)**
```python
    class HStoreFormTest(Form):
        f1 = forms.HStoreField()
    form_w_hstore = HStoreFormTest()
    self.assertFalse(form_w_hstore.has_changed())
    form_w_hstore = HStoreFormTest({"f1": '{"a": 1}'})
    self.assertTrue(form_w_hstore.has_changed())
    form_w_hstore = HStoreFormTest({"f1": '{"a": 1}'}, initial={"f1": '{"a": 1}'})
    self.assertFalse(form_w_hstore.has_changed())
    form_w_hstore = HStoreFormTest({"f1": '{"a": 2}'}, initial={"f1": '{"a": 1}'})
    self.assertTrue(form_w_hstore.has_changed())
    form_w_hstore = HStoreFormTest({"f1": '{"a": 1}'}, initial={"f1": {"a": 1}})
    self.assertFalse(form_w_hstore.has_changed())
    form_w_hstore = HStoreFormTest({"f1": '{"a": 2}'}, initial={"f1": {"a": 1}})
    self.assertTrue(form_w_hstore.has_changed())
```


---

## p2-12  (celery/t/unit/bin/test_daemonization.py)   parses: False

**PROMPT (what the model saw)**
```python
@pytest.mark.usefixtures('depends_on_current_app')
@pytest.mark.parametrize("daemon", ["worker", "beat", "events"])
def test_daemon_options_from_config(daemon: str, cli_runner: CliRunner):
```

**MODEL OUTPUT (the body it wrote)**
```python
    @click.command()
    @click.option("--pdb", type=click.Choice(["-pdb", "pdb", "pdb", "pdb", "pdb"])
    def cli_runner(pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb: str, pdb:
```

**ORIGINAL BODY (for comparison only)**
```python
    with patch(f"celery.bin.{daemon}.{daemon}.callback") as mock:
        cli_runner.invoke(celery, f"-A t.unit.bin.proj.daemon {daemon}")

    mock.assert_called_once()
    for param in "logfile", "pidfile", "uid", "gid", "umask", "executable":
        assert mock.call_args.kwargs[param] == getattr(config, f"{daemon}_{param}")
```


---

## p2-13  (black/tests/test_ranges.py)   parses: False

**PROMPT (what the model saw)**
```python
@pytest.mark.parametrize(
    "lines,sanitized",
    [
        (
            [(1, 4)],
            [(1, 4)],
        ),
        (
            [(2, 3)],
            [(2, 3)],
        ),
        (
            [(2, 10)],
            [(2, 4)],
        ),
        (
            [(0, 3)],
            [(1, 3)],
        ),
        (
            [(0, 10)],
            [(1, 4)],
        ),
        (
            [(-2, 3)],
            [(1, 3)],
        ),
        (
            [(0, 0)],
            [],
        ),
        (
            [(-2, -1)],
            [],
        ),
        (
            [(-1, 0)],
            [],
        ),
        (
            [(3, 1), (1, 3), (5, 6)],
            [(1, 3)],
        ),
    ],
)
def test_sanitize(
    lines: list[tuple[int, int]], sanitized: list[tuple[int, int]]
) -> None:
```

**MODEL OUTPUT (the body it wrote)**
```python
    lines = []
    for line in lines:
        if line.startswith("[") or sanitized:
            lines.append(line)
        else:
            lines.append(line)
    assert lines == [
        (
            [(1, 4)],
            [(1, 4)],
            [(1, 4)],
        ),
        (
            [(1, 2)],
            [(1, 3)],
            [(1, 4)],
        ),
        (
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1, 3)],
        ),
        (
            [(1, 2)],
            [(1, 3)],
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1, 3)],
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1, 2)],
            [(1
```

**ORIGINAL BODY (for comparison only)**
```python
    source = """\
1. import re
2. def func(arg1,
3.   arg2, arg3):
4.   pass
"""
    assert sanitized == sanitized_lines(lines, source)

    source_no_trailing_nl = """\
    1. import re
    2. def func(arg1,
    3.   arg2, arg3):
    4.   pass"""
    assert sanitized == sanitized_lines(lines, source_no_trailing_nl)
```


---

## p2-14  (starlette/starlette/formparsers.py)   parses: False

**PROMPT (what the model saw)**
```python
def __init__(
    self,
    headers: Headers,
    stream: AsyncGenerator[bytes, None],
    *,
    max_fields: int | float = 1000,
    max_part_size: int = 1024 * 1024,  # 1MB
) -> None:
```

**MODEL OUTPUT (the body it wrote)**
```python
    """
    Create a new stream.

    :param headers: Headers to use for the stream.
    :param stream: The stream to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_size: The maximum number of bytes to use for the stream.
    :param max_part_
```

**ORIGINAL BODY (for comparison only)**
```python
    assert multipart is not None, "The `python-multipart` library must be installed to use form parsing."
    self.headers = headers
    self.stream = stream
    self.max_fields = max_fields
    self.max_part_size = max_part_size
    self.messages: list[tuple[FormMessage, bytes]] = []
    self._current_field_size = 0
    self._current_fields = 0
```


---

## p2-15  (attrs/src/attr/_cmp.py)   parses: False

**PROMPT (what the model saw)**
```python
def _make_init():
    """
    Create __init__ method.
    """
```

**MODEL OUTPUT (the body it wrote)**
```python
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.args[0]

    def __call__(self, *args, **kwargs):
        return self.args[1]

    def __call__(self, *args, **kwargs):
        return self.args[0]

    def __call__(self, *args, **kwargs):
        return self.args[1]

    def __call__(self, *args, **kwargs):
        return self.args[1]

    def __call__(self, *args, **kwargs):
        return self.args[1]

    def __call__(self, *args, **kwargs):
        return self.args[1]

    def __call__(self, *args, **kwargs):
        return self.args[1]

    def
```

**ORIGINAL BODY (for comparison only)**
```python
    def __init__(self, value):
        """
        Initialize object with *value*.
        """
        self.value = value

    return __init__
```


---

## p2-16  (fastapi/tests/test_empty_router.py)   parses: True

**PROMPT (what the model saw)**
```python
def test_use_empty():
```

**MODEL OUTPUT (the body it wrote)**
```python
    # GH#5186
    df = pd.DataFrame(
        {"a": [1, 2, 3], "b": [4, 5, 6], "c": [8, 9, 10], "d": [8, 9, 10]}
    )
    df.to_hdf(temp_h5_path, key="a", use_empty=True)
    with pytest.raises(ValueError, match="Unable to parse string"):
        df.to_hdf(temp_h5_path, key="a", use_empty=True)
```

**ORIGINAL BODY (for comparison only)**
```python
    with client:
        response = client.get("/prefix")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]

        response = client.get("/prefix/")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]
```


---

## p2-17  (rich/rich/jupyter.py)   parses: False

**PROMPT (what the model saw)**
```python
def _render_segments(segments: Iterable[Segment]) -> str:
```

**MODEL OUTPUT (the body it wrote)**
```python
    """
    Helper function to render the text.

    Args:
       segments: Iterable[Segment]
        """
    ) -> tuple[Segment, Segment]:
        """
        Helper function to render the text.

        Args:
           segments: Iterable[Segment]
            """
    ) -> tuple[Segment, Segment]:
        """
        Helper function to render the text.

        Args:
           segments: Iterable[Segment]
            """
    ) -> tuple[Segment, Segment]:
        """
        Helper function to render the text.

        Args:
           segments: Iterable[Segment]
            """
    ) -> tuple[Segment, Segment]:
        """
        Helper function to render the text.

        Args:
           segments: Iterable[Segment]
            """
    ) -> tuple[Segment, Segment]:
        """
        Helper function to render the text.

        Args:
```

**ORIGINAL BODY (for comparison only)**
```python
    def escape(text: str) -> str:
        """Escape html."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    fragments: List[str] = []
    append_fragment = fragments.append
    theme = DEFAULT_TERMINAL_THEME
    for text, style, control in Segment.simplify(segments):
        if control:
            continue
        text = escape(text)
        if style:
            rule = style.get_html_style(theme)
            text = f'<span style="{rule}">{text}</span>' if rule else text
            if style.link:
                text = f'<a href="{style.link}" target="_blank">{text}</a>'
        append_fragment(text)

    code = "".join(fragments)
    html = JUPYTER_HTML_FORMAT.format(code=code)

    return html
```


---

## p2-18  (sympy/sympy/polys/tests/test_densebasic.py)   parses: False

**PROMPT (what the model saw)**
```python
def test_dmp_permute():
```

**MODEL OUTPUT (the body it wrote)**
```python
    assert dmp_permute([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    assert dmp_permute([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    assert dmp_permute([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    assert dmp_permute([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    assert dmp_permute([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    assert dmp_permute([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    assert dmp_permute([1, 2, 3], [2, 3, 4]) ==
```

**ORIGINAL BODY (for comparison only)**
```python
    f = dmp_normal([[1, 0, 0], [], [1, 0], [], [1]], 1, ZZ)
    g = dmp_normal([[1, 0, 0, 0, 0], [1, 0, 0], [1]], 1, ZZ)

    assert dmp_permute(f, [0, 1], 1, ZZ) == f
    assert dmp_permute(g, [0, 1], 1, ZZ) == g

    assert dmp_permute(f, [1, 0], 1, ZZ) == g
    assert dmp_permute(g, [1, 0], 1, ZZ) == f
```


---

## p2-19  (matplotlib/galleries/examples/event_handling/poly_editor.py)   parses: False

**PROMPT (what the model saw)**
```python
def __init__(self, ax, poly):
```

**MODEL OUTPUT (the body it wrote)**
```python
    """
    Create a new Axes object.

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.axes.Axes`
        Axes object.
    poly : `~matplotlib.
```

**ORIGINAL BODY (for comparison only)**
```python
    if poly.figure is None:
        raise RuntimeError('You must first add the polygon to a figure '
                           'or canvas before defining the interactor')
    self.ax = ax
    canvas = poly.figure.canvas
    self.poly = poly
    x, y = zip(*self.poly.xy)
    self.line = Line2D(x, y,
                       marker='o', markerfacecolor='r',
                       animated=True)
    self.ax.add_line(self.line)
    self.cid = self.poly.add_callback(self.poly_changed)
    self._ind = None  # the active vert
    canvas.mpl_connect('draw_event', self.on_draw)
    canvas.mpl_connect('button_press_event', self.on_button_press)
    canvas.mpl_connect('key_press_event', self.on_key_press)
    canvas.mpl_connect('button_release_event', self.on_button_release)
    canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
    self.canvas = canvas
```


---

## p2-20  (tornado/tornado/platform/twisted.py)   parses: True

**PROMPT (what the model saw)**
```python
@gen.convert_yielded.register(Deferred)
def _(d: Deferred) -> Future:
```

**MODEL OUTPUT (the body it wrote)**
```python
    """
    Return a new Future object.

    This is a wrapper to be called in a future.
    """
    if d is None:
        return Future()
    else:
        return Future()
```

**ORIGINAL BODY (for comparison only)**
```python
    f: Future[typing.Any] = Future()
    def errback(failure: failure.Failure) -> None:
        try:
            failure.raiseException()
            # Should never happen, but just in case
            raise Exception("errback called without error")
        except:
            future_set_exc_info(f, sys.exc_info())
    d.addCallbacks(f.set_result, errback)
    return f
```
