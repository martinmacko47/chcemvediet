# Model: `chvemvediet.apps.inforequests`

![](assets/inforequests.svg)

### Inforequest Flow

![](assets/inforequest-flow.svg)

## `InforequestDraft`

Relations:
* `applicant`: User; May NOT be NULL.\
  The draft owner, the future inforequest applicant.
* `obligee`: Obligee; May be NULL.\
  The obligee the inforequest will be sent to, if the user has already set it.
* `attachment_set`: List of Attachments; May be empty; Ordered by id.\
  Attachments for the future request action.

Properties:
* `subject`: String; May be empty.\
  Draft subject for the future request action.
* `content`: String; May be empty.\
  Draft content for the future request action.

## `Inforequest`

Represents a single inforequest. Inforequests are ordered by their submission date by default.

Relations:
* `applicant`: User; May NOT be NULL.\
  The inforequest owner, the user who submitted it.
* `email_set`: List of E-mail Messages; through Inforequest E-mails; May be empty; Ordered by
  processed date.\
  List of all inbound and outbound messages related to the inforequest, decided or undecided. The
  `unique_email` address generated for the inforequest is used for communication with all obligees
  the request was advanced to. It is up to the applicant ~~and/or some heuristics~~ to decide to
  which branch the action contained in the e-mail belongs. The e-mails are ordered by the date we
  sent or received them, respectively. Queued outbound e-mails waiting to be sent are ordered by
  their id.
* `branch_set`: List of Branches; May NOT be empty; Ordered by obligee name.\
  List of all branches related to the inforequest. Every inforequest contains at least one branch,
  the main branch.
* `actiondraft_set`: List of Action Drafts; May be empty; Ordered by id.\
  List of all action drafts the applicant created for this inforequest. The inforequest may contain
  at most one draft of each action type.
* `inforequestemail_set`: List of Inforequest E-mails; May be empty; Ordered by id.

Computed Relations:
* `branch`: Branch; May NOT be NULL; Read-only.\
  Main branch of communication with the original obligee the inforequest was submitted to. The
  inforequest must contain exactly one main branch. If the inforequest was advanced to other
  obligees, the respective advancement action contains recursive sub-branches of communication with
  new obligees.
* `undecided_set`: List of E-mail Messages; May be empty; Read-only.\
  List of undecided inbound messages waiting for user decision.
* `oldest_undecided_email` and `newest_undecided_email`: E-mail Message; May be NULL; Read-only.

Properties:
* `applicant_name`, `applicant_street`, `applicant_city` and `applicant_zip`: String; May NOT be
  empty.\
  To freeze applicant current contact information for the case he changes it in the future. The
  information is frozen to its state at the moment the inforequest was submitted.
* `unique_email`: E-mail; May NOT be empty; Unique.\
  Every inforequest has a unique e-mail address of the form \*@mail.chcemvediet.sk. This address is
  used to identify which obligee e-mail belongs to which inforequest. However, if the inforequest
  was advanced to other obligees, the same e-mail address is used for communication with all such
  obligees, as there is no way to tell them to send their response to a different e-mail address.
* `submission_date`: Date; May NOT be NULL.\
  The effective date of the request action.
* `closed`: True/False; May NOT be NULL.\
  True if the inforequest is closed and the applicant may not act on it any more. The inforequest is
  closed ~~when the applicant or the administrator close it manually~~, or if all its branches are
  terminated, or the applicant abandon it for a very long time. If a request is not closed, we say
  that it is opened.
* `last_undecided_email_reminder`: Datetime; May be NULL.

Computed Properties:
* `has_undecided_email`: True/False; May NOT be NULL; Read-only.
* `can_add_X`: True/False; May NOT be NULL; Read-only.\
  Whether the user can append action X to at least one of the inforequest branches.
* `can_add_applicant_action`, `can_add_applicant_email_action`, `can_add_obligee_action`,
  `can_add_obligee_email_action`: True/False; May NOT be NULL; Read-only.\
  Whether the user can append applicant/obligee action received by s-mail or e-mail.

## `InforequestEmail`

Represents a relation between an inforequest and an inbound or outbound e-mail message. Every
inforequest has its unique e-mail address which is used for communication with all obligees the
request was advanced to. If there are multiple open branches in the inforequest, It is up to the
applicant ~~and/or some heuristics~~ to decide to which branch the action contained in the received
e-mail belongs. The e-mails are ordered by the date we processed them.

Relations:
* `inforequest`: Inforequest; May NOT be NULL.\
  Inforequest the e-mail was assigned to.
* `email`: E-mail Message; May NOT be NULL.

Properties:
* `type`: Choice; May NOT be NULL.
  - For inbound messages:
    - _obligee-action_: The e-mail represents and obligee action.
    - _undecided_: The e-mail is waiting for applicant decision.
    - _unrelated_: Marked as an unrelated e-mail.
    - _unknown_: Marked as an e-mail the applicant didn't know how to decide.
  - For outbound messages:
    - _applicant-action_: The e-mail represents an applicant action.

## `Branch`
Represents communication with a single obligee concerning a single inforequest. If the obligee
advances the inforequest to other obligees, the advancement action contains its own sub-branches of
communication with new obligees. If the branch is the main branch of its inforequest, we say that
the branch is main, otherwise we say that it's advanced. If the last branch action sets no deadline
we say that this action is terminal and the branch is terminated. No further actions may be added to
terminated branches.

Relations:
* `inforequest`: Inforequest; May NOT be NULL.\
  The inforequest the branch belongs to.
* `obligee`: Obligee; May NOT be NULL.\
  The obligee the inforequest was sent or advanced to.
* `historicalobligee`: Historical Obligee; May NOT be NULL.\
  To freeze obligee current contact information for the case it changes in the future. The
  information is frozen to its state at the moment the request was submitted if it is the main
  branch, or the moment the advancement action was received.
* `advanced_by`: Action; May be NULL.\
  NULL for main branches. The advancement action the inforequest was advanced by for advanced
  branches. Every Inforequest must contain exactly one main branch.
* `action_set`: List of Actions; May NOT be empty; Ordered by effective date.\
  The communication with the obligee. The first action of every main branch is a request action and
  the first action of every advanced branch is an advanced request action. Actions are ordered by
  their effective date.
* `actiondraft_set`: List of Action Drafts; May be empty; Ordered by id.

Computed Relations:
* `last_action`: Action; May NOT be NULL; Read-only\
  The list of actions may not be empty, so the last action is always defined.

Computed Properties:
* `is_main`: True/False; May NOT be NULL; Read-only.
  Whether the branch is its inforequest main branch, or it's advanced.
* `can_add_x`: True/False; May NOT be NULL; Read-only.\
  Whether the user can append action X to the branch.
* `can_add_applicant_action`, `can_add_applicant_email_action`, `can_add_obligee_action`,
  `can_add_obligee_email_action`: True/False; May NOT be NULL; Read-only.\
  Whether the user can append applicant/obligee action received by s-mail or e-mail.

## `Action`
Relations:
* `branch`: Branch; May NOT be NULL
* `email`: E-mail Message; May be NULL;\
  Mandatory for actions sent or received by e-mail, NULL otherwise.
* `attachment_set`: List of Attachments; May be empty; Ordered by id.
* `advanced_to_set`: List of Branches; May be empty.\
  May NOT be empty for advancement actions. Must be empty otherwise.

Properties:
* `type`: Choice; May NOT be NULL.
  - Applicant Actions: _Request_; _Clarification Response_; _Appeal_;
  - Obligee Actions: _Confirmation_; _Extension_; _Advancement_; _Clarification Request_;
  _Disclosure_; _Refusal_; _Affirmation_; _Reversion_; _Remandment_;
  - Implicit Actions: _Advanced Request_; _Expiration_; _Appeal Expiration_.
* `subject` and `content`: String; May be empty.\
  Action subject/content written by the applicant or copied from the e-mail. May be empty for
  implicit actions, should NOT be empty for other actions.
* `effective_date`: Date; May NOT be NULL.\
  The date at which the action was sent or received. If the action was sent/received by e-mail it's
  set automatically. If it was sent/received by s-mail it's filled by the applicant.
* `deadline`: Number; May be NULL.\
  The deadline that apply after the action, if the action sets a deadline, NULL otherwise. The
  deadline is expressed in a number of working days (WD) counting since the effective date. It may
  apply to the applicant or to the obligee, depending on the action type.
* `extension`: Number; May be NULL.\
  Applicant extension to the deadline, if the action sets an obligee deadline. The applicant may
  extend the deadline after it is missed in order to be patient and wait a little longer. He may
  extend it multiple times. Applicant deadlines may not be extended.
* `disclosure_level`: Choice; May be NULL.\
  Mandatory choice for advancement, disclosure, reversion and remandment actions, NULL otherwise.
  Specifies if the obligee disclosed any requested information by this action. Possible levels:
  - _none_: The obligee does not disclosed the requested information at all.
  - _part_: The obligee disclosed the requested information partially.
  - _full_: The obligee disclosed all requested information.
* `refusal_reason`: Choice; May be NULL.\
  Mandatory choice for refusal and affirmation actions, NULL otherwise. Specifies the reason why the
  obligee refused to disclose the information. Possible reasons:
  - _does not have information_; _does not provide information_; _does not create information_;
    _copyright restriction_; _business secret_; _personal information_; _confidential information_;
    _no reason specified_; _other reason_.
* ~~`delivery_status`: Choice; May be NULL.~~\
  ~~Mandatory choice for applicant actions, NULL otherwise. Whether the action was delivered.~~
  - ~~_delivered_: If we got e-mail receipt confirmation, or the applicant got an s-mail proof of
    delivery.~~
  - ~~_undelivered_: If we got an e-mail delivery status notification for all its recipients, or the
    s-mail was returned undelivered to the applicant.~~
  - ~~_unknown_.~~
* `last_deadline_reminder`: Datetime; May be NULL.

Computed Properties:
* `is_applicant_action`, `is_obligee_action` and `is_implicit_action`: True/False; May NOT be NULL;
  Read-only\
  Whether the action was made by the applicant, by the obligee, or whether it was implicit.
* `days_passed` and `days_passed_at`: Number; May NOT be NULL; Read-only\
  Number of WD since the effective date until today and until the specified date, respectively.
* `deadline_remaining` and `deadline_remaining_at`: Number; May be NULL; Read-only.\
  Number of WD remaining until the deadline is missed including all its extensions with respect to
  today and with respect to the specified date, respectively. NULL if the action sets no deadline.
* `deadline_missed` and `deadline_missed_at`: True/False; May NOT be NULL; Read-only\
  True if the deadline including all its extensions is already missed. False if it is not yet missed
  or if the action does not set any deadline. The value is computed with respect to today or to the
  the specified date, respectively.
* `has_deadline`, `has_applicant_deadline` and `has_obligee_deadline`: True/False; May NOT be NULL;
  Read-only.\
  Whether the action sets a deadline, and whether it is set for the applicant or for the obligee.

## `ActionDraft` <sup>[1](#footnote1)</sup>

Relations:
* `inforequest`: Inforequest; May NOT be NULL
* `branch`: Branch; May be NULL.\
  Must be owned by `inforequest` if set.
* `obligee_set`: List of Obligees; May be empty; Ordered by id.\
  May be empty for advancement actions. Must be empty for all other actions.
* `attachment_set`: List of Attachments; May be empty; Ordered by id.

Properties:
* `type`: Choice; May NOT be NULL.\
  Choices are the same as for action type.
* `subject` and `content`: String; May be empty.
* `effective_date`: Date; May be NULL.
* `deadline`: Number; May be NULL.\
  Optional for extension actions. Must be NULL for all other actions.
* `disclosure_level`: Choice; May be NULL\
  Optional for advancement, disclosure, reversion and remandment actions. Must be NULL for all other
  actions. Choices are the same as for action disclosure level.
* `refusal_reason`: Choice; May be NULL\
  Optional for refusal and affirmation actions. Must be NULL for all other actions. Choices are the
  same as for action refusal reason.

## Extended Backward Relations

### `User`

* `inforequestdraft_set`: List of InforequestDrafts; May be empty; Ordered by id.
* `inforequest_set`: List of Inforequest; May be empty; Ordered by submission date.

### `Obligee`
* `inforequestdraft_set`: List of InforequestDrafts; May be empty; Ordered by id.
* `branch_set`: List of Branches; May be empty; Ordered by obligee name.
* `actiondraft_set`: List of Action Drafts; May be empty; Ordered by id.

### `HistoricalObligee`
* `branch_set`: List of Branches; May be empty; Ordered by obligee name.

### `EmailMessage`
* `inforequest_set`: List of Inforequest; May be empty; Ordered by submission date.
* `inforequestemail_set`: List of InforequestEmail; May be empty; Ordered by id.
* `action`: Action; May be undefined.

## Applicant Actions

**Request**: Represents an applicant action of requesting the obligee for information. A request may
be sent either by e-mail ~~or by s-mail~~. Every main branch must contain at least one instance of
request action. Advanced branches may not contain any request actions, instead they contain advanced
request actions. ~~There are two cases that can happen for a main branch:~~

1. It contains exactly one request action, either sent by e-mail ~~or by s-mail~~. In this case the
   request action must be the very first branch action.
2. ~~It contains exactly two request actions, of which the first one was sent by e-mail and was
   marked as undelivered later and the second one, which is a copy of the first one, was sent by
   s-mail thereafter. In this case both these request actions must be the very first two actions of
   the branch.~~

_Properties that apply_:
* If the request was sent by e-mail:
  - `email`: a reference to the sent e-mail
  - `effective_date`: e-mail sent date
* ~~If the request was sent by s-mail:~~
  - ~~`effective_date`: the date the s-mail was generated~~
* `subject` + `content` + `attachment_set`
* `deadline`: 8 WD for the obligee to response
* `extension`
* ~~`delivery_status`~~

**Clarification Response**: represents an applicant action of providing the obligee an clarification
to his inforequest. A clarification response may only be sent if the last branch action is a
clarification request. The branch may contain multiple clarification responses as it may contain
multiple clarification requests.

Properties that apply:
* If the clarification response was sent by e-mail:
  - `email`: a reference to the sent e-mail
  - `effective_date`: e-mail sent date
* If the clarification response was sent by s-mail:
  - `effective_date`: the date the s-mail was generated
* `subject` + `content` + `attachment_set`
* `deadline`: 8 WD for the Obligee to response
* `extension`
* ~~`delivery_status`: notice that clarification response may be sent to multiple e-mails; it is
  considered undelivered after it fails to be delivered to all its recipients.~~

**Appeal**: represents an applicant action of appealing against the obligee resolution. An appeal is
sent to the obligee by s-mail only. The obligee should forward it to its superior automatically. An
appeal may only be sent if the last branch action is a non-full disclosure, refusal or advancement,
or if it is a request, clarification response, confirmation, extension, remandment or advanced
request and its deadline is missed. A branch may contain only one appeal until a remandment was
made.

_Properties that apply_:
* `subject` + `content` + `attachment_set`
* `effective_date`: the date the s-mail was generated
* `deadline`: 30 WD for the obligee superior to respond
* `extension`
* ~~`delivery_status`~~

## Obligee Actions

**Confirmation**: represents an obligee action of confirming they received the inforequest. It may
be received either by e-mail or by s-mail, and it applies to both the regular requests and the
advanced requests as well. In the case the request was advanced the confirmation is sent by the new
obligee. The confirmation action resets the obligee deadline. A confirmation may only be added if
the last branch action is a request or advanced request.

_Properties that apply_:
* If the confirmation was received by e-mail:
  - `email`: a reference to the received e-mail
  - `effective_date`: e-mail received date
* If the confirmation was received by s-mail:
  - `effective_date`: the date the s-mail was received on; filled by the Applicant
* `subject` + `content` + `attachment_set`
* `deadline`: 8 WD for the obligee to response
* `extension`

**Extension**: represents an obligee action of extending their deadline. An extension may only be
added if the last branch action is a request, confirmation, clarification response, remandment or
advanced request.

_Properties that apply_:
* If the extension was received by e-mail:
  - `email`: a reference to the received e-mail
  - `effective_date`: e-mail received date
* If the extension was received by s-mail:
  - `effective_date`: the date the s-mail was received on; filled by the applicant
* `subject` + `content` + `attachment_set`
* `deadline`: 10 WD for the obligee to response or the deadline specified by the obligee
* `extension`

**Advancement**: represents an obligee action of advancing the inforequest to one or more other
obligees. An advancement may only be added if the last branch action is a request, clarification
response, confirmation or advanced request. An advancement may contain part of requested information
disclosed. ~~Note, that the new obligee does not have to be in our database, yet. In such case we
should let the applicant fill in the new obligee contact information.~~

_Properties and relations that apply_:
* If the advancement was received by e-mail:
  - `email`: a reference to the received e-mail
  - `effective_date`: e-mail received date
* If the advancement was received by s-mail:
  - `effective_date`: the date the s-mail was received on; filled by the applicant
* `subject` + `content` + `attachment_set`
* `advanced_to_set`: May NOT be empty. Branches of communication with the obligees the inforequest
  was advanced to.
* `disclosure_level`: (Mandatory)

**Clarification Request**: represents an obligee action of asking the applicant to clarify his
inforequest. A clarification request may only be added if the last branch action is a   request,
clarification response, confirmation, clarification request or advanced request.

_Properties that apply_:
* If the clarification request was received by e-mail:
  - `email`: a reference to the received e-mail
  - `effective_date`: e-mail received date
* If the clarification request was received by s-mail:
  - `effective_date`: the date the s-mail was received on; filled by the applicant
* `subject` + `content` + `attachment_set`
* `deadline`: 7 WD for the applicant to response; the applicant should response to the obligee
  within the deadline, however, it is not enforced.

**Disclosure**: represents an obligee action of disclosing the requested information. The
information may be disclosed to the full extent, or it may be disclosed partially. The applicant
decides if the information was disclosed fully, partially, or not at all, despite the fact the
obligee said they are disclosing it. If a branch contains a full disclosure action, it is its
terminal action the branch is terminated. A disclosure may only be added if the last branch action
is request, clarification response, confirmation, extension, remandment or advanced request.

_Properties that apply_:
* If the disclosure was received by e-mail:
  - `email`: a reference to the received e-mail
  - `effective_date`: e-mail received date
* If the disclosure was received by s-mail:
  - `effective_date`: the date the s-mail was received on; filled by the applicant
* `subject` + `content` + `attachment_set`
* `deadline`: 15 WD for the applicant to appeal if the information was not fully disclosed; the
  applicant should appeal within the deadline, however, it is not enforced.
* `disclosure_level`: (Mandatory choice)

**Refusal**: represents an obligee action of refusing to disclose the requested information.
A refusal may only be added if the last branch action is request, clarification response,
confirmation, extension, remandment or advanced request.

_Properties that apply_:
* If the refusal was received by e-mail:
  - `email`: a reference to the received e-mail
  - `effective_date`: e-mail received date
* If the refusal was received by s-mail:
  - `effective_date`: the date the s-mail was received on; filled by the applicant
* `subject` + `content` + `attachment_set`
* `deadline`: 15 WD for the applicant to appeal; the applicant should appeal within the deadline,
  however, it is not enforced.
* `refusal_reason`: (Mandatory choice)

**Affirmation**: represents an obligee superior action of affirming the obligee resolution. It may
be received by s-mail only and only if the last branch action is appeal. This action ends the appeal
process and terminates the branch as well.

_Properties that apply_:
* `subject` + `content` + `attachment_set`
* `effective_date`: the date the s-mail was received on; filled by the applicant.
* `refusal_reason`: (Mandatory choice)

**Reversion**: represents an obligee superior action of reversing the obligee resolution. It may be
received by s-mail only and only if the last branch action is appeal. The obligee superior may
disclose the requested information within this action. It may disclose it to the full extent, or
just partially. This action ends the appeal process and terminates the branch as well.

_Properties that apply_:
* `subject` + `content` + `attachment_set`
* `effective_date`: the date the s-mail was received on; filled by the applicant.
* `disclosure_level`: (Mandatory choice)

**Remandment**: represents an obligee superior action of remanding the inforequest back to the
obligee. It may be received by s-mail only and only if the last branch action is appeal. The obligee
superior may disclose the requested information within this action. If they disclose some
information within this action, they usually disclose just its part, as the rest of the requested
information should disclose the obligee to which the request was remanded. This action ends the
appeal process, but does not terminate the branch itself. The obligee should act thereafter.

_Properties that apply_:
* `subject` + `content` + `attachment_set`
* `effective_date`: the date the s-mail was received on; filled by the applicant
* `deadline`: 8+5 = 13 WD for the obligee to response
* `extension`
* `disclosure_level`: (Mandatory choice)

## Implicit Actions

**Advanced Request**: represents an implicit action of requesting the new obligee for information
after the original request was advanced to the new obligee. It is just an implicit action, so it's
never performed in reality. Every advanced branch contains exactly one advanced request action as
its very first action. Main branches may not contain this action, they contain regular request
action instead.

_Properties that apply_:
* `effective_date`: the effective date of the advancement action from the branch this branch
  advanced from.
* `deadline`: 8+5 = 13 WD for the new obligee to response
* `extension`

**Expiration**: represents an implicit action of missing the inforequest deadline by the obligee.
It is just an implicit action, so it's never performed in reality. The expiration action is added
just before the applicant makes an appeal action or the branch is closed while there is a missed
obligee deadline.

_Properties that apply_:
* `effective_date`: the effective date of the corresponding appeal action or the date the branch was
closed.

**Appeal Expiration**: represents an implicit action of missing the appeal deadline by the obligee
superior. It is just an implicit action, so it's never performed in reality. The appeal expiration
action is added just before the branch is closed while there a missed obligee superior deadline.

_Properties that apply_:
* `effective_date`: the date the branch was closed.

## Wizards

### Obligee Action Wizard

![](assets/obligee-action-wizard.svg)

Overview of wizard results:

![](assets/obligee-action-wizard-table.svg)

_Legend_:
* Tick: The wizard correctly categorizes the new action.
* Dash: The new action is impossible in such cases, so we don't care what wizard does about them.
* Green H: The new action is invalid in such case and the wizard ends with a help request.
* Red action type: The new action is invalid in such case, but the wizard ends with a categorization
  as a wrong action type. Such cases are very rare, however, so we don't care about them.

## Events

### Received E-mail

Trigger: Received inbound e-mail.

When an inbound e-mail is received, we assign the e-mail to an inforequest according to the e-mail
recipient address and the inforequest unique e-mail address. If there is no such inforequest, we
leave the received e-mail unassigned. The administrator can see a list of all unassigned inbound
e-mails.

If the assigned request is opened, we send a notification to the inforequest applicant. If there are
more undecided e-mails waiting in the inforequest, the applicant is informed about it. The
notification contains a link where the applicant may decide the received e-mails.

If the assigned inforequest is closed, no notification is sent. The administrator can see a list of
all undecided e-mails assigned to closed inforequests.

### Undecided E-mail Reminder

Trigger: Daily at 9:00

For every opened inforequest with a newest undecided raw e-mail received 5 WD ago, we send a
notification to its applicant to remind him about the undecided e-mails. The notification contains
a link where the applicant may decide the received e-mails.

### Obligee Deadline Reminder

Trigger: Daily at 9:00

For every opened inforequest with no waiting undecided e-mails, and every its branch which latest
action sets an obligee deadline, which was missed today taking into account all deadline extensions
made by its applicant, we send a reminder to its applicant to remind him about the expiring
deadline. The notification contains information about the action which deadline was missed and a
link where the applicant may act or extend the deadline. If an extended deadline is missed again, we
send the reminder again.

The following actions set obligee deadlines:
* Applicant Actions: Request, Clarification Response, Appeal
* Obligee Actions: Confirmation, Extension, Remandment
* Implicit Actions: Advanced Request


### Applicant Deadline Reminder

Trigger: Daily at 9:00

For every opened inforequest with no waiting undecided e-mails, and every branch which latest action
sets an applicant deadline, which is about to be missed in 2 WD, we send a reminder to its applicant
to remind him about the expiring deadline. The notification contains information which action
deadline is about to be missed and a link where the applicant may act.

The following actions set applicant deadlines: Clarification Request, Disclosure, Refusal.

### Close Inforequests

Trigger: Daily at 9:00

We close all inforequests that have all their branches terminated or abandoned. A branch is
abandoned if its latest action sets a deadline which was already missed at least 100 WD ago.

Just before we close an inforequest, we add an implicit expiration or appeal expiration action to
every its branch which latest action sets an obligee deadline. If the original latest action was an
appeal action, we add an appeal expiration action. Otherwise, we add an expiration action.

If there are any undecided e-mails in the closed inforequest, the administrator can see them in a
list of all undecided e-mails assigned to closed inforequests.

## User Actions

### Decide Undecided E-mail

URL: `/en/inforequests/decide-email/<action>/<inforequest_id>/<email_id>/`

Conditions:
* User is authenticated.
* User is the inforequest applicant.
* The inforequest is not closed.
* There is no older undecided e-mail in the inforequest.

The applicant decides if the received raw e-mail is related to the inforequest, and if so, he
decides which obligee action the e-mail represents. As advanced branches share their e-mail
addresses with their main branches, all raw e-mails are associated to the inforequest only. It is up
to the applicant ~~and/or some heuristics~~ to decide to which branch the action contained in the
received e-mail belongs.

The applicant may say that he doesn't know how to decide the received e-mail, for instance if he
does not know what this e-mail is. The administrator can see a list of e-mails  the users didn't
know how to decide.

If there are multiple undecided e-mails in the inforequest, the applicant must decide them in the
order they were received. After a raw e-mail is decided it's marked as decided and the corresponding
obligee action is added to the branch. If the applicant decides the received e-mail is unrelated to
the inforequest, no action is added to the branch, but the received e-mail is marked as unrelated
instead.

Only the following actions may be received by e-mail:
* **Confirmation**
* **Extension**: The applicant may input custom obligee deadline specified in the obligee response.
  If there is no custom obligee deadline in the response, the default deadline is used.
* **Advancement**: After this action is added, new advanced branches containing implicit advanced
  request actions are created. While the obligee may advance the inforequest to multiple new
  obligees, multiple new advanced branches may be created. It's up to the applicant to input the
  list of all obligees to which the request advanced. The inforequest may not be advanced to the
  same obligee, nor to two identical obligees. As this action may contain part of the requested
  information disclosed, the applicant should input if any of the information was disclosed or not.
* **Clarification Request**
* **Disclosure**: The applicant should input if the requested information was disclosed to the full
  extent, only partially, or not at all. If he says the information was fully disclosed, the branch
  is terminated.
* **Refusal**: The applicant should input the reason why the information was refused to disclose.

The created action received e-mail is set to the received e-mail and its subject, content and list
of uploaded files is copied. The effective date of the action received by e-mail is the date the
e-mail was received.

### Add Obligee Action received by S-mail

URL: `/en/inforequests/add-smail/<action>/<inforequest_id>/`

Conditions:

* User is authenticated.
* User is the inforequest applicant.
* The inforequest is not closed.
* There is no undecided e-mail in the inforequest.

The applicant decides which obligee action the s-mail represents. All actions that may be received
by e-mail may be received by s-mail as well. Apart from them, the following actions may be received
by s-mail only:
* **Affirmation**: After this action is added, the branch is terminated. The applicant should input
  the reason why the information was refused to disclose.
* **Reversion**: After this action is added, the branch is terminated. As this action may contain
  part of the requested information disclosed, the applicant should input if any of the information
  was disclosed or not.
* **Remandment**: As this action may contain part of the requested information disclosed, the
  applicant should input if any of the information was disclosed or not.

If the applicant add a new action received by s-mail, he should input all its content either as a
plain text or rather as a scanned attachment file. The effective date of the action received by
s-mail should be specified by the applicant. However it may not be older than the current last
branch action. Moreover it may not be older than one month nor from the future.

If there is undecided e-mail waiting in the inforequest the user may not add any action received by
s-mail, however he may save it as a draft.

### Extend Missed Obligee Deadline

URL: `/en/inforequests/extend-deadline/<inforequest_id>/<branch_id>/<action_id>`

Conditions:
* User is authenticated.
* User is the inforequest applicant.
* The inforequest is not closed.
* There is no undecided e-mail in the inforequest.
* The latest branch action sets an obligee deadline, which is already missed taking into account all
  previous deadline extensions made by the applicant.

The applicant may extend the deadline by any number of WD, by default by 5 WD. The extension is
expressed in a number of WD relative to the day the extension was made. After the extended deadline
is missed as well, the applicant gets a notification about it.

The following actions set obligee deadlines that can be extended:
* Applicant Actions: Request, Clarification Response, Appeal
* Obligee Actions: Confirmation, Extension, Remandment
* Implicit Actions: Advanced Request

### Make a Clarification Response Action

URL: `/en/inforequests/new-action/clarification-response/<inforequest_id>/`

Conditions:
* User is authenticated.
* User is the inforequest applicant.
* The inforequest is not closed.
* There is no undecided raw e-mail in the inforequest.
* The last branch action is clarification request

Clarification responses may be made either by e-mail or by s-mail. ~~However, if the respective
clarification request was received by e-mail, the clarification response should be sent by e-mail as
well, and vice versa. It's up to the applicant to decide.~~ If he decides to send it by s-mail, he
should be able to print ~~and/or download a pdf of~~ the prepared action content.

The obligee may respond from different e-mail addresses during the inforequest branch. To ensure the
clarification response is sent to the correct obligee address, it is sent to all e-mail addresses
collected during this branch. However not to addresses collected from other inforequest branches, as
every branch represents communication with different obligee.

The applicant may save the clarification response as a draft and send it later. There may be only
one clarification response draft in the inforequest. If the conditions change while the applicant
edits the clarification response, and it is not possible to send it any more, the clarification
response is not sent, but the applicant may save it as a draft and send it later. For instance, this
may happen if a new raw e-mail is received while the applicant edits the clarification response. In
such case, he must decide the received e-mail foremost.

The effective date of a clarification response is the date it was sent if it was sent by e-mail, or
the date it was generated if it was sent by s-mail.

### Make an Appeal Action

URL: `/en/inforequests/new-action/appeal/<inforequest_id>/`

Conditions:
* User is authenticated.
* User is the inforequest applicant.
* The inforequest is not closed.
* There is no undecided raw e-mail in the inforequest.
* The last branch action is a non-full disclosure, refusal or advancement, or if it is a request,
  clarification response, confirmation, extension, remandment or advanced request and its deadline
  is missed.

Appeals may be sent by s-mail only. They are sent to the postal address of the obligee, which should
automatically forward it to its superior. The applicant should be able to print ~~and/or download
a pdf of~~ the prepared action content.

If the appeal is sent after an obligee deadline was missed, an implicit expiration action is added
just before the appeal action.

The applicant may save the appeal as a draft and send it later. There may be only one appeal draft
in the inforequest. If the conditions change while the applicant edits the appeal, and it is not
possible to send it any more, the appeal is not sent, but the applicant may save it as a draft and
send it later. For instance, this may happen if a new raw e-mail is received while the applicant
edits the appeal. In such case, he must decide the received e-mail foremost.

The effective date of an appeal is the date it was generated.

### ~~Resend Undelivered E-mail by S-mail~~

~~URL: `/en/inforequests/...`~~

Conditions:
* ~~User is authenticated.~~
* ~~User is the inforequest applicant.~~
* ~~The inforequest is not closed.~~
* ~~There is no undecided raw e-mail in the inforequest.~~
* ~~The latest branch action is marked undelivered.~~

~~If an applicant action sent by e-mail returned as undelivered, the applicant may try to resend it
by s-mail.~~

~~The following applicant actions may be sent by e-mail:~~
* ~~Request~~
* ~~Clarification Response~~

### Create a New Inforequest / InforequestDraft

URL: `/en/inforequests/create/`\
URL: `/en/inforequests/create/<draft_id>/`

Conditions:
* User is authenticated.
* User has a verified e-mail address

Instead of submitting the created inforequest directly, the user may decide to save it as a
inforequestdraft and submit it later. The user may edit the draft until he submits it. The obligee
property does not have to be set while the inforequest is just a draft. The user may own multiple
unfinished request drafts.

### Delete a InforequestDraft

URL: `/en/inforequests/delete-draft/<draft_id>/`

Conditions:
* User is authenticated.
* User is the request draft owner.

## Views

### ~~List of all Inforequests~~

~~URL: `/en/inforequests/...`~~

~~Visibility: Public~~

~~The view contains a link to create a new inforequest.~~

### List of Inforequests Created by the User

URL: `/en/inforequests/`

Visibility: Authenticated user

The user may see his inforequestdrafts besides his submitted and closed inforequests as well. The
view contains a link to create a new inforequest.

### Inforequest Detail

URL: `/en/inforequests/detail/<inforequest_id>/`

~~Visibility: Public~~

1. _For the applicant_:\
   The applicant sees basic inforequest information, branch of actions in chronological order by
   their effective date and his undecided e-mails.\
   The applicant may act on the inforequest if it's not closed, yet. He can:
   - decide undecided e-mails,
   - add obligee actions based on obligee responses received by s-mail,
   - extend missed obligee deadlines,
   - ~~resend undelivered e-mail by s-mail,~~
   - send a clarification response,
   - make an appeal.
2. ~~_For other users and the public_:~~\
   ~~Other users and the public see only anonymized request information, branch of actions, and~~
   ~~undecided e-mails. If possible, content of actions and e-mails should be anonymized as well.~~\
   ~~Neither other users nor the public may act on the case.~~

If the inforequest was advanced, details of all its descendant branches are shown in a tree
structure as well.

### Upload Attachment

URL: `/en/inforequests/attachments/`

Visibility: Authenticated user

Uploaded files are attached to the user. The user may use uploaded files while composing an
inforequest or an action. He may use only his uploaded files.

### Download Attachment

URL: `/en/inforequests/attachments/<attachment_id>/`

~~Visibility: Public~~

~~Anonymous user may download only files attached to actions connected to public inforequests.~~
Authenticated user may also download files attached to him, to his inforequestdrafts or to any
e-mails, actions or action drafts connected to his inforequests.

## Administration

**List of Unassigned Received E-mails**
* May assign an unassigned e-mail to a case

**List of Undecided Raw E-mails Assigned to Closed Inforequests**

**List of E-mails Marked as Unrelated**

**List of E-mails the Users didn't Know how to Decide**
* May decide the e-mail


<sub><a name="footnote1">1</a>: *`ActionDraft` was replaced with `WizardDraft`*</sub>\
<sub>*\* Features that are marked ~~strikethrough~~ are not implemented yet.*</sub>
