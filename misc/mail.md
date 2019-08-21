# Model: `poleno.mail`

![](assets/mail.svg) 

## `Message`

Represents a single inbound or outbound e‑mail message.

Relations:
* `recipient_set`: List of Recipients; Should NOT be empty; Ordered by id.
* `attachment_set`: List of Attachments; May be empty; Ordered by id.

Properties:
* `type`: Choice; May NOT be NULL.\
  - inbound, outbound
* `processed`: Datetime ; May be NULL.\
  Time the message was sent/received. NULL for queued outbound messages.
* `from_name`: String; May be empty.
* `from_mail`: E-mail; Should NOT be empty.
* `received_for`: E-mail; May be empty.\
  The address we received the message for. It may, but does not have to be among the message 
  recipients, as the address may have been bcc-ed to. The address is empty for all outbound messages
  and may be empty for some inbound messages if we don't know it, or the used e-mail transport 
  doesn't support it.
* `subject`: String; May be empty.
* `text` and `html`: String; May be empty.\
  Text/plain and text/html body alternatives of the message. At least one should be defined.
* `headers`: JSON; May be empty.\
  Dictionary mapping header names to their values, or lists of their values. For outbound messages
  it contains only extra headers added by the sender. For inbound messages it contains all message
  headers.

Computed Properties:
* `from_formatted`: String; May be empty; Read-write.\
  Formatted from address, combination of `from_name` and `from_mail`.
* `to_formatted`, `cc_formatted` and `bcc_formatted`: String; May be empty; Read‑only.\
  Comma separated lists of formatted addresses of message recipients of the respective type.

## `Recipient`

Relations:
* `message`: Message; May NOT be NULL.

Properties:
* `name`: String; May be empty.
* `mail`: E-mail; May NOT be empty.
* `type`: Choice; May NOT be NULL.\
  - to, cc, bcc
* `status`: Choice; May NOT be NULL.\
  - For inbound messages:
    - inbound
  - For outbound messages:
    - undefined
    - queued: The message is waiting to be sent.
    - rejected: The message was rejected by the recipient.
    - invalid: The e-mail transport refused the message as invalid for this recipient.
    - sent: The message was successfully sent for this recipient.
    - delivered: There is an evidence the message was delivered to the recipient.
    - opened: There is an evidence the message was opened by the recipient.
* `status_details`: String; May be empty.\
  Various details about `status` set by the e-mail transport. E.g. rejection reason.
* `remote_id`: String; May be empty.\
  Message id used by the e-mail transport.

Computed Properties:
* `formatted`: String; May NOT be empty; Read-write.\
  Formatted address, combination of `name` and `mail`.

## SMTP transport events

**Send outbound e-mails**\
  Trigger: every few minutes if there are any queued outbound messages waiting.

## IMAP transport events

**Poll for inbound e-mails**\
  Trigger: every few minutes.

## Mandrill transport events

**Send outbound e-mails**\
  Trigger: every few minutes if there are any queued outbound messages waiting.

**Message status webhook event**\
  Trigger: request to Mandrill webhook\
  Updates message recipient status according to the Mandrill event received. The message and its
  recipients are identified by `remote_id`.

**Inbound e-mail webhook event**\
  Trigger: request to Mandrill webhook

## Mandrill transport views
**Mandrill webhook**\
  URL: /mandrill/webhook/


## Administration

**List of All E-mails** 

<sub>*\* Features that are marked ~~strikethrough~~ are not implemented yet.*</sub>
