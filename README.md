# input_constrain

simple little module for getting very specific user inputs.
---

## overview

* `read_single_keypress() -> string` — cross-platform function that gets exactly one keypress

* `until(char: string) -> string` — get characters from stdin until `char` is read

* `thismany(count: int) -> string` — get exactly `count` characters from stdin

* `_until_demo() -> None` — small demo of `until()`

* `_thismany_demo() -> None` — small demo of `thismany()`