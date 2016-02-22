# PMLR = poor man's (python) libreadline

#### a minimal, simplistic readline / curses in pure Python

---

Usage:

```python
>>> import pmlr
>>> pmlr.init()
>>> key = pmlr.readkey()
>>> print(key)
'a'
```

also see the `examples/` directory for more examples you can play around with.



Thanks to [Dannno](http://codereview.stackexchange.com/users/47529/dannnno) and [their post](http://codereview.stackexchange.com/a/118726/87163) for making this module cool.