# Model: `chcemvediet.apps.anonymization`

![](assets/anonymization.svg)

## `AttachmentNormalization`

Represents a single local file, which was created by normalization of Attachment file.

Relations:
* `attachment`: Attachment; May NOT be NULL.\
  The Attachment from which AttachmentNormalization was created.

Properties:
* `successful`: Boolean; May NOT be NULL.
* `file`: File; May NOT be NULL.\
  Empty filename if normalization failed or normalization didn’t create any file.
* `name`: String; May be empty.\
  Automatically computed when creating a new object. Empty, if file.name is empty.
* `content_type`: String; May be NULL.
* `created`: Datetime; May NOT be NULL.
* `size`: Number; May be NULL.
* `debug`: String; May NOT be NULL; May be empty.

Computed Properties:
* `content`: String; May be NULL; May be empty; Read-only.

## `AttachmentRecognition`

Represents a single local file, which was created by recognition of Attachment file.

Relations:
* `attachment`: Attachment; May NOT be NULL.\
  The Attachment from which AttachmentRecognition was created.

Properties:
* `successful`: Boolean; May NOT be NULL.
* `file`: File; May NOT be NULL.\
  Empty filename if recognition failed.
* `name`: String; May be empty.\
  Automatically computed when creating a new object. Empty, if file.name is empty.
* `content_type`: String; May be NULL.
* `created`: Datetime; May NOT be NULL.
* `size`: Number; May be NULL.
* `debug`: String; May NOT be NULL; May be empty.

Computed Properties:
* `content`: String; May be NULL; May be empty; Read-only.

## `AttachmentAnonymization`

Represents a single local file, which was created by anonymization of Attachment file.

Relations:
* `attachment`: Attachment; May NOT be NULL.\
  The Attachment from which AttachmentAnonymization was created.

Properties:
* `successful`: Boolean; May NOT be NULL.
* `file`: File; May NOT be NULL.\
  Empty filename if anonymization failed.
* `name`: String; May be empty.\
  Automatically computed when creating a new object. Empty, if file.name is empty.
* `content_type`: String; May be NULL.
* `created`: Datetime; May NOT be NULL.
* `size`: Number; May be NULL.
* `debug`: String; May NOT be NULL; May be empty.

Computed Properties:
* `content`: String; May be NULL; May be empty; Read-only.

## `AttachmentFinalization`

Represents a single local file, which was created by finalization of Attachment file.

Relations:
* `attachment`: Attachment; May NOT be NULL.\
  The Attachment from which AttachmentFinalization was created.

Properties:
* `successful`: Boolean; May NOT be NULL.
* `file`: File; May NOT be NULL.\
  Empty filename if finalization failed.
* `name`: String; May be empty.\
  Automatically computed when creating a new object. Empty, if file.name is empty.
* `content_type`: String; May be NULL.
* `created`: Datetime; May NOT be NULL.
* `size`: Number; May be NULL.
* `debug`: String; May NOT be NULL; May be empty.

Computed Properties:
* `content`: String; May be NULL; May be empty; Read-only.


<sub>*\* Features that are marked ~~strikethrough~~ are not implemented yet.*</sub>


## Anonymization
You can manually anonymize `Attachment` using management command:

```
manage.py attachment_anonymization attachment [options] [file]

Options:
  -v VERBOSITY, --verbosity=VERBOSITY
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings=SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath=PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Raise on exception
  --no-color            Don't colorize the command output.
  -f FILENAME, --file=FILENAME
                        define file path
  --content_type=CONTENT_TYPE
                        define content type of file
  --debug=DEBUG         add debug message
  --force               overwrite an existing successful
                        AttachmentFinalization
  --version             show program's version number and exit
  -h, --help            show this help message and exit
```
