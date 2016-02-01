# input_constrain

#### simple little module for getting very specific user inputs.

---

## module overview

* `read_single_keypress() -> string` — cross-platform function that gets exactly one keypress

* `thismany(count: int = -1) -> string` — get exactly `count` characters from stdin. if count is `-1`, then `sys.maxsize` chars will be read.

* `until(chars: string || list, count: int = -1) -> string` — get characters from stdin until `char` is read, or until `count` chars have been read. if `count` is `-1`, `sys.maxsize` chars will be read.

* `until_not(chars: string || list, count: int = -1) -> string` — get characters from stdin until any of `chars` is not read. if `count` is `-1`, then `sys.maxsize` chars will be read.

## other parts of the module

* class `_Getch`: determines system platform and calls one of `_GetchUnix` or `_GetchWindows` appropriately

* class `_GetchUnix`: get a raw character from stdin, on any *nx box

* class `_GetchWindows`: get a raw character from stdin, on any Windows box

* function `nbsp`: do stuff accordingly for certain chars of input; handles backspace, etc

* function `parsenum`: return a number, or `sys.maxsize` if number is `-1`

## examples overview

* `_until_demo() -> None` — small demo of `until()`

* `_thismany_demo() -> None` — small demo of `thismany()`

* `_can_you_vote() -> None` — small demo of `until_not_multi()`

* `_forth_syntax_test() -> None` — small practical demo of `until()`