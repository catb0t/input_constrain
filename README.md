# input_constrain

simple little module for getting very specific user inputs.
---

## overview

* `read_single_keypress() -> string` — cross-platform function that gets exactly one keypress

* `thismany(count: int) -> string` — get exactly `count` characters from stdin

* `until(char: string) -> string` — get characters from stdin until `char` is read

* `until_multi(chars: string || list) -> string` — get stdin until any of `chars` is read

* `until_not(char: string) -> string` — like `until()` except it reads until the keypress of input is not `char`

* `until_not_multi(chars: string || list) -> string` — a combination of `until_not()` and `until_multi()`; gets stdin until something not in `chars` is read

* `_until_demo() -> None` — small demo of `until()`

* `_thismany_demo() -> None` — small demo of `thismany()`

* `_can_you_vote() -> None` — small demo of `until_not_multi()`
