# Model: `chcemvediet.apps.obligees`

![](assets/obligees.svg)

## `Obligee`

Represents a single obligee and its contact information. Obligee is automatically versioned with
Historical Obligee model representing its historical versions.

Relations:
* `history`: List of Historical Obligees; May NOT be empty.

Properties:
* `name`: String; May NOT be empty.
* `street`, `city` and `zip`: String; May NOT be empty.
* `emails`: String; May NOT be empty.\
  Comma separated list of formatted e-mail addresses.
* `slug`: String; May NOT be empty.\
  Slug for full-text search. Consists of `name`.
* `status`: Choice; May NOT be NULL.
  - pending: Obligee exists and accepts inforequests.
  - dissolved: Obligee does not exist any more, no further inforequests may be submitted to it.

Computed Properties:
* `emails_parsed`: List of (name, mail) pairs; May NOT be empty; Read-only.
* `emails_formatted`: List of Strings; May NOT be empty; Read-only.


## Views

**List of all Obligees**

URL: `/en/obligees/`

Visibility: Public

Paginated list of all obligees.

**Obligee autocomplete**

URL: `/en/autocomplete/`

Visibility: Public

## Administration

**List of obligees**
* Edit an individual obligee tracking its historical versions.
* Create a new individual obligee.
* Disable an individual obligee that does not exist any more.
* ~~Bulk export do csv/xls.~~
* ~~Bulk import from csv/xls tracking historical versions of all obligees with some heuristics and
  UI to manage matching created/deleted obligees and obligees with changed names.~~


<sub>*\* Features that are marked ~~strikethrough~~ are not implemented yet.*</sub>
