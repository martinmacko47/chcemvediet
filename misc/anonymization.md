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


## `attachment_anonymization`

	 $ env/bin/python manage.py attachment_anonymization [options] attachment_id [file]


Creates AttachmentFinalization instance for the specified Attachment. By default, the file path is
read from stdin. You can pass file path explicitly as an argument.

AttachmentFinalization created this way will be marked as successful. Only one successful
AttachmentFinalization can be assigned to the Attachment.

* `--content_type=CONTENT_TYPE`: Content type of file, e.g. "application/pdf". Automatically
                                 computed if not specified.
* `--debug=DEBUG`: Debug message to the newly created instance. Empty by default.
* `--force`: The command refuses to anonymize attachment if a successful anonymization already
             exists. This flag disables this check. Deletes all existing successful
             AttachmentFinalizations and creates new one. Unsuccessful AttachmentFinalizations will
             stay unaffected.


<sub>*\* Features that are marked ~~strikethrough~~ are not implemented yet.*</sub>
