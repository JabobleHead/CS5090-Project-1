# Baseline vs no position embeddings: generations

Same prompts, seeds [1, 2, 3], temperature 0.8, top-k 50, 80 new tokens, CPU. Checkpoints: out-baseline/ckpt.pt and out-ablation-nopos/ckpt.pt (iteration 8400 each).


## a - b


### seed 1

**baseline**
```python
x = a - b)**2
    assert ccode(ccode(z)) == 'z'
    assert ccode(z) == 'z'

    assert ccode(z) == 'z'
    assert ccode(z) == 'z'
    assert ccode(z) == 'z'

    assert ccode(z, 'z') == 'z'
    assert ccode(z
```

**no-pos-emb**
```python
x = a - b*x
    >>> c = x - y - c
    >>> f = x**2 - 2*x
    >>> f.subs(x, 2)
    f
    2
    >>> f.subs(x, 2)
    4*x*y - 1/x

    >>> f.subs(a, 2)
    f.subs(x, 2)

    >>> f.subs
```


### seed 2

**baseline**
```python
x = a - b**2
    assert _test_args(2*I*pi*x + b - c**2*pi*x, a, b, x)


def test_expand_poly():
    a = Symbol('a', real=True)
    b = Symbol('b')
    assert _test_args(x*y*x)
    assert _test_args(
```

**no-pos-emb**
```python
x = a - b*a + b + c
    assert limit(x**2 + 2, x, order='x') == x**2
    assert limit(x**2 + 1, x, order='x') == x**3
    assert limit(x**2 + 1, x, order='x') == x**2 + 2*x**2 + 15*x**2 + 16
```


### seed 3

**baseline**
```python
x = a - b + c
    return a * b


@_tracking_matrix
def _do_squares_decomposition(a, b):
    """Compute the decomposition of the power of a.

    A has shape (n, n) or (n, n)
    """
    # compute the squares equation (represented as coefficients)
    if a.is_zero:
```

**no-pos-emb**
```python
x = a - b + c
    >>> q = f(x)
    >>> q
    x**5/4 + x**2/5/4 - 4*x**6/4 + x**2/4 - 4*x**2/4 - 4*x**2/4 - 4*x**2/4 - 4
    >>> q
    x**2/5/6 + x
```


## b - a


### seed 1

**baseline**
```python
x = b - a
        # Missing source code
        if path_name != "README":
            # For a full source code, the source code is the same as the
            # source code.
            source_code = urllib.parse.urlencode(source_code)
            return source_code
        # Missing source code
        source_code = self.getsource(source_code
```

**no-pos-emb**
```python
x = b - a*x
    >>> c = x - y - c
    >>> f = x**2 - 2*x
    >>> f.subs(x, 2)
    f
    2
    >>> f.subs(x, 2)
    4*x*y - 1/x

    >>> f.subs(a, 2)
    f.subs(x, 2)

    >>> f.subs
```


### seed 2

**baseline**
```python
x = b - a + b * I + a
    assert R.dup_degree_by_dup(f, (0, K), F) == (G, K)


def test_dmp_zero_gcd():
    assert R.dmp_zero_gcd(f, 2) == (F, 0)

    f = 2*x**2 + 15*x**2 + 16
```

**no-pos-emb**
```python
x = b - a*x**2 + b**2

    s = f(x + 1)
    assert s == c
    assert s == _c1*x**2 + 1
    assert s == c**2 + 1

    s1 = c + 1
    s2 = c + 1
    s3 = c + 2
    s4 = c + 4*x**2 + 1
    s
```


### seed 3

**baseline**
```python
x = b - a + b - b - b)
        if is_sequence(b, n):
            return a*b**2 + b**2
        if is_sequence(b, n):
            return a*(b**2 + n).is_sequence(b, n)
        if is_sequence(b, n):
            return b + a*b + b
        if is_sequence
```

**no-pos-emb**
```python
x = b - a + c
    >>> q = b - c
    >>> x
    array([ 1/2 + 3*b**2 + 3*c**4 + 3*c**2 - 1/2, 2*b**2 - 3*c**4 + 1/2 - 1/2])

    """
    if len(c) < 2 or c[-1] != '+1
```


## nested indentation


### seed 1

**baseline**
```python
for i in range(3):
    for j in range(3):
        if i == j:
            raise ValueError(f"Cannot find {i} for {i!r} for {j!r}")
    for i in range(4):
        if j == j:
            if len(i) == 0:
                break

    # this is an error
    # If we have two cases
    for i in range(1, -1):
        if len(i) == 1:
```

**no-pos-emb**
```python
for i in range(3):
    for j in range(3):
        if i == j:
            a = i - j
            break
    return a, i + b


def _solve_for_update_for_update_for_update_for_update_for_update_for_update_for_update_for_update_for_for_update_for_for_update_for_for_update_for_update_for_for_update_
```


### seed 2

**baseline**
```python
for i in range(3):
    for j in range(3):
        if i == j:
            yield (i, j)
    assert list(itertools.chain(itertools.chain(itertools.chain(itertools.chain(*[len(i) for i in j) for j in i])))) == [
        [i + 1, i + 4, i + 1, i + 4, i + 2, i]
    ]
    for i in range(3
```

**no-pos-emb**
```python
for i in range(3):
    for j in range(3):
        if i == j:
            if j == j + 1:
                # Try to add a new i to j in the loop since the j is reachable
                # on i in a j
                    i += 2
                if j + 1 < j:
                    i += 1
                elif j == j + 1:
                    i += 1
                    i -= 1
                if i < n and i - i == 1:
                   
```


### seed 3

**baseline**
```python
for i in range(3):
    for j in range(3):
        if i == j:
            continue
        if j == 0:
            continue
        k = int(k)
        for j in range(0, 2):
            if j == j:
                continue
        for j in range(k+1, k+1):
            if j == 0:
                continue
        if j % 2 == j:
            continue
        k *= int(k)
        for j in range(1
```

**no-pos-emb**
```python
for i in range(3):
    for j in range(3):
        if i == j:
            continue
        if j == j:
            continue
        k = j
        if k != j:
            continue
        if k == j:
            k = j
        elif k / j - j[j:] == j:
            continue
        else:
            k = j
            continue
        if k == j:
            continue
        if k == j:
            i = j + k
        else:
            continue
```


## call with several positional args


### seed 1

**baseline**
```python
result = compute(p, p, p=p, p_tol=p_tol)
    x0 = x0
    for i in range(p_tol, x0):
        x1 = np.linalg.norm(x)
        r = p - p_tol
        if p < 0:
            f_i = p_tol + x0
        u = f0
        if p
```

**no-pos-emb**
```python
result = compute(p, q, p=q, p=q)
    if not isinstance(q, np.ndarray):
        raise ValueError("Incompatible PDF matrix")
    if p is None:
        raise ValueError("Incompatible PDF matrix")
    if q is None:
        raise ValueError("Incompatible PDF matrix")
    p = q
    if n_features > 0:
        raise ValueError
```


### seed 2

**baseline**
```python
result = compute(f, a, b, a, b, b, c, d, d, e, f, c, a, b, d, e, f)
    assert_array_almost_equal(f, a, b, c, d, e, f)


def test_gh_119_bare():
    n = 15
    a = np.arange
```

**no-pos-emb**
```python
result = compute(t, axis, result_type="numeric")
        if axis != axis:
            raise ValueError("`axis` must be one of the result")
        return result_type, None

    return result


class Correlational(Correlational):
    r"""Correlational power series coefficients with Correlational power series of Correlational

    .. math::

       
```


### seed 3

**baseline**
```python
result = compute(func, values=values, **kwargs)

            return func(func, values=values, **kwargs)

        return func.ewm(func, values=values, **kwargs)

    def _ewm_func(self, func):
        return func.ewm(func, values=values, **kwargs)

    def _ewm_func(self, func):
        return
```

**no-pos-emb**
```python
result = compute(df, result, axis=None, keepdims=False)
    else:
        # Note: this is a new copy
        result = np.empty(rows)
        if result is None:
            result.flags.writeable = True
        else:
            result.flags.writeable = True

    if result.flags.writeable:
        result = result.flags.writeable
        return
```
