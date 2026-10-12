---
id: CR-1020
title: Class diagram shows list fields as their element type
status: To Do
assignee: []
created_date: '2026-10-12 17:53'
labels: []
dependencies: []
type: fix
project: plcc-ng
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A field produced by an arbno rule (`**=`) holds a list, but `plcc-diagram` draws it in the class diagram as a single value of the element type. The diagram misstates the generated classes, which is the thing a student reads it to learn.

The languages-ng V0 grammar has

```
<Rands> **= <Exp> +COMMA
```

and its generated `class.puml` contains

```
class Rands {
  expList: Exp
}
```

The field should be shown as `List[Exp]`: the semantics code iterates it (`for e in self.expList`).

The model already carries the information. [build_model.py](../../../plcc-ng/src/plcc/model/build_model.py) records arbno fields with `is_list: True`, but [class_diagram/plantuml/emit.py](../../../plcc-ng/src/plcc/diagram/class_diagram/plantuml/emit.py) renders every field as `name: type` and ignores `is_list`.

### Steps to reproduce

Run `plcc-diagram` on any spec with an arbno rule, e.g.:

```
skip WS '\s+'
token NUM '\d+'
token COMMA ','
%
<Nums> **= <NUM> +COMMA
```

`plcc-ng/diagram/class.puml` shows `numList: Token` where `List[Token]` is expected.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A field from an arbno (`**=`) rule is shown in the class diagram as `List[T]`, where T is its element type
- [ ] #2 Fields from `::=` rules are rendered unchanged
- [ ] #3 A unit test in the class-diagram emitter covers a list field
<!-- AC:END -->
