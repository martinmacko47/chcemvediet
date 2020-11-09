# vim: expandtab
# -*- coding: utf-8 -*-
import random
import mock
import contextlib
from collections import defaultdict

from django.db import IntegrityError
from django.test import TestCase
from django.utils.translation import ugettext as __

from poleno.timewarp import timewarp
from poleno.attachments.models import Attachment
from poleno.mail.models import Message, Recipient
from poleno.utils.date import local_datetime_from_local, naive_date, local_today
from poleno.utils.test import created_instances
from poleno.workdays import workdays

from .. import InforequestsTestCaseMixin
from ...models import InforequestEmail, Branch, Action
from ...models.deadline import Deadline


class ActionTest(InforequestsTestCaseMixin, TestCase):
    u"""
    Tests ``Action`` model.
    """

    def test_branch_field(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        self.assertEqual(action.branch, branch)

    def test_branch_field_may_not_be_null(self):
        with self.assertRaisesMessage(IntegrityError, u'NOT NULL constraint failed: inforequests_action.branch_id'):
            self._create_action(omit=[u'branch'])

    def test_email_field(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        email = self._create_message()
        action = self._create_action(branch=branch, email=email)
        self.assertEqual(action.email, email)

    def test_email_field_default_value_if_omitted(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, omit=[u'email'])
        self.assertIsNone(action.email)

    def test_type_field(self):
        tests = (
                (Action.TYPES.REQUEST,                __(u'inforequests:Action:type:REQUEST')),
                (Action.TYPES.CLARIFICATION_RESPONSE, __(u'inforequests:Action:type:CLARIFICATION_RESPONSE')),
                (Action.TYPES.APPEAL,                 __(u'inforequests:Action:type:APPEAL')),
                (Action.TYPES.CONFIRMATION,           __(u'inforequests:Action:type:CONFIRMATION')),
                (Action.TYPES.EXTENSION,              __(u'inforequests:Action:type:EXTENSION')),
                (Action.TYPES.ADVANCEMENT,            __(u'inforequests:Action:type:ADVANCEMENT')),
                (Action.TYPES.CLARIFICATION_REQUEST,  __(u'inforequests:Action:type:CLARIFICATION_REQUEST')),
                (Action.TYPES.DISCLOSURE,             __(u'inforequests:Action:type:DISCLOSURE')),
                (Action.TYPES.REFUSAL,                __(u'inforequests:Action:type:REFUSAL')),
                (Action.TYPES.AFFIRMATION,            __(u'inforequests:Action:type:AFFIRMATION')),
                (Action.TYPES.REVERSION,              __(u'inforequests:Action:type:REVERSION')),
                (Action.TYPES.REMANDMENT,             __(u'inforequests:Action:type:REMANDMENT')),
                (Action.TYPES.ADVANCED_REQUEST,       __(u'inforequests:Action:type:ADVANCED_REQUEST')),
                (Action.TYPES.EXPIRATION,             __(u'inforequests:Action:type:EXPIRATION')),
                (Action.TYPES.APPEAL_EXPIRATION,      __(u'inforequests:Action:type:APPEAL_EXPIRATION')),
                )
        # Make sure we are testing all defined action types
        tested_action_types = [a for a, _ in tests]
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for action_type, expected_display in tests:
            action = self._create_action(branch=branch, type=action_type)
            self.assertEqual(action.type, action_type)
            self.assertEqual(action.get_type_display(), expected_display)

    def test_type_field_may_not_be_null(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        with self.assertRaisesMessage(IntegrityError, u'NOT NULL constraint failed: inforequests_action.type'):
            self._create_action(branch=branch, omit=[u'type'])

    def test_subject_and_content_fields(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, subject=u'Subject', content=u'Content')
        self.assertEqual(action.subject, u'Subject')
        self.assertEqual(action.content, u'Content')

    def test_subject_and_content_fields_default_values_if_omitted(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, omit=[u'subject', u'content'])
        self.assertEqual(action.subject, u'')
        self.assertEqual(action.content, u'')

    def test_attachment_set_relation(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        attachment1 = self._create_attachment(generic_object=action)
        attachment2 = self._create_attachment(generic_object=action)
        self.assertItemsEqual(action.attachment_set.all(), [attachment1, attachment2])

    def test_attachment_set_relation_empty_by_default(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        self.assertItemsEqual(action.attachment_set.all(), [])

    def test_legal_date_field(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, legal_date=naive_date(u'2010-10-05'))
        self.assertEqual(action.legal_date, naive_date(u'2010-10-05'))

    def test_legal_date_field_may_not_be_null(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        with self.assertRaisesMessage(IntegrityError, u'NOT NULL constraint failed: inforequests_action.legal_date'):
            self._create_action(branch=branch, omit=[u'legal_date'])

    def test_deadline_property(self):
        delivered_date = naive_date(u'2010-10-05')
        legal_date = naive_date(u'2010-10-04')
        tests = (
                (Action.TYPES.REQUEST,                Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, delivered_date, 8, Deadline.UNITS.WORKDAYS, None), dict()),
                (Action.TYPES.CLARIFICATION_RESPONSE, Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, delivered_date, 8, Deadline.UNITS.WORKDAYS, None), dict()),
                (Action.TYPES.APPEAL,                 Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, delivered_date, 15, Deadline.UNITS.CALENDAR_DAYS, None), dict()),
                (Action.TYPES.CONFIRMATION,           Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, delivered_date, 8, Deadline.UNITS.WORKDAYS, None), dict()),
                (Action.TYPES.EXTENSION,              Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, delivered_date, 8+0, Deadline.UNITS.WORKDAYS, None), dict()),
                (Action.TYPES.ADVANCEMENT,            None, dict()),
                (Action.TYPES.CLARIFICATION_REQUEST,  Deadline(Deadline.TYPES.APPLICANT_DEADLINE, delivered_date, 7, Deadline.UNITS.CALENDAR_DAYS, None), dict()),
                (Action.TYPES.DISCLOSURE,             Deadline(Deadline.TYPES.APPLICANT_DEADLINE, delivered_date, 15, Deadline.UNITS.CALENDAR_DAYS, None), dict(disclosure_level=Action.DISCLOSURE_LEVELS.NONE)),
                (Action.TYPES.DISCLOSURE,             Deadline(Deadline.TYPES.APPLICANT_DEADLINE, delivered_date, 15, Deadline.UNITS.CALENDAR_DAYS, None), dict(disclosure_level=Action.DISCLOSURE_LEVELS.PARTIAL)),
                (Action.TYPES.DISCLOSURE,             None, dict(disclosure_level=Action.DISCLOSURE_LEVELS.FULL)),
                (Action.TYPES.REFUSAL,                Deadline(Deadline.TYPES.APPLICANT_DEADLINE, delivered_date, 15, Deadline.UNITS.CALENDAR_DAYS, None), dict()),
                (Action.TYPES.AFFIRMATION,            None, dict()),
                (Action.TYPES.REVERSION,              None, dict()),
                (Action.TYPES.REMANDMENT,             Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, workdays.advance(legal_date, 4), 8, Deadline.UNITS.WORKDAYS, None), dict()),
                (Action.TYPES.ADVANCED_REQUEST,       Deadline(Deadline.TYPES.OBLIGEE_DEADLINE, workdays.advance(legal_date, 4), 8, Deadline.UNITS.WORKDAYS, None), dict()),
                (Action.TYPES.EXPIRATION,             Deadline(Deadline.TYPES.APPLICANT_DEADLINE, legal_date, 15, Deadline.UNITS.CALENDAR_DAYS, None), dict()),
                (Action.TYPES.APPEAL_EXPIRATION,      None, dict()),
                )
        # Make sure we are testing all defined action types
        tested_action_types = set(a for a, _, _ in tests)
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for action_type, expected_deadline, extra_args in tests:
            previous = self._create_action(branch=branch, type=Action.TYPES.REQUEST, delivered_date=delivered_date)  # Deadline for CONFIRMATION, EXTENSION
            action = self._create_action(branch=branch, type=action_type, delivered_date=delivered_date, legal_date=legal_date, **extra_args)
            self.assertEqual(repr(action.deadline), repr(expected_deadline))

    def test_deadline_field_is_not_changed_if_saving_existing_instance(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        deadline = action.deadline
        action.subject = u'Changed'
        action.save()
        action = Action.objects.get(pk=action.pk)
        self.assertEqual(repr(action.deadline), repr(deadline))

    def test_extension_field(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, extension=3)
        self.assertEqual(action.extension, 3)

    def test_extension_field_default_value_if_omitted(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, omit=[u'extension'])
        self.assertIsNone(action.extension)

    def test_disclosure_level_field(self):
        tests = (
                (Action.DISCLOSURE_LEVELS.NONE,    __(u'inforequests:Action:disclosure_level:NONE')),
                (Action.DISCLOSURE_LEVELS.PARTIAL, __(u'inforequests:Action:disclosure_level:PARTIAL')),
                (Action.DISCLOSURE_LEVELS.FULL,    __(u'inforequests:Action:disclosure_level:FULL')),
                )
        # Make sure we are testing all defined disclosure levels
        tested_disclosure_levels = [a for a, _ in tests]
        defined_disclosure_levels = Action.DISCLOSURE_LEVELS._inverse.keys()
        self.assertItemsEqual(tested_disclosure_levels, defined_disclosure_levels)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for disclosure_level, expected_display in tests:
            action = self._create_action(branch=branch, disclosure_level=disclosure_level)
            self.assertEqual(action.disclosure_level, disclosure_level)
            self.assertEqual(action.get_disclosure_level_display(), expected_display)

    def test_disclosure_level_field_default_value_if_omitted(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, omit=[u'disclosure_level'])
        self.assertIsNone(action.disclosure_level)

    def test_refusal_reason_field(self):
        tests = (
                (Action.REFUSAL_REASONS.DOES_NOT_HAVE,    __(u'inforequests:Action:refusal_reason:DOES_NOT_HAVE')),
                (Action.REFUSAL_REASONS.DOES_NOT_PROVIDE, __(u'inforequests:Action:refusal_reason:DOES_NOT_PROVIDE')),
                (Action.REFUSAL_REASONS.DOES_NOT_CREATE,  __(u'inforequests:Action:refusal_reason:DOES_NOT_CREATE')),
                (Action.REFUSAL_REASONS.COPYRIGHT,        __(u'inforequests:Action:refusal_reason:COPYRIGHT')),
                (Action.REFUSAL_REASONS.BUSINESS_SECRET,  __(u'inforequests:Action:refusal_reason:BUSINESS_SECRET')),
                (Action.REFUSAL_REASONS.PERSONAL,         __(u'inforequests:Action:refusal_reason:PERSONAL')),
                (Action.REFUSAL_REASONS.CONFIDENTIAL,     __(u'inforequests:Action:refusal_reason:CONFIDENTIAL')),
                (Action.REFUSAL_REASONS.OTHER_REASON,     __(u'inforequests:Action:refusal_reason:OTHER_REASON')),
                )
        # Make sure we are testing all defined refusal reasons
        tested_refusal_reasons = [a for a, _ in tests]
        defined_refusal_reasons = Action.REFUSAL_REASONS._inverse.keys()
        self.assertItemsEqual(tested_refusal_reasons, defined_refusal_reasons)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for refusal_reason, expected_display in tests:
            action = self._create_action(branch=branch, refusal_reason=refusal_reason)
            self.assertEqual(action.refusal_reason, [refusal_reason])
            self.assertEqual(action.get_refusal_reason_display(), expected_display)

    def test_refusal_reason_field_default_value_if_omitted(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, omit=[u'refusal_reason'])
        self.assertIsNone(action.refusal_reason)

    def test_last_deadline_reminder_field(self):
        dt = local_datetime_from_local(u'2014-10-05 10:33:00')
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, last_deadline_reminder=dt)
        self.assertEqual(action.last_deadline_reminder, dt)

    def test_last_deadline_reminder_field_default_value_if_omitted(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, omit=[u'last_deadline_reminder'])
        self.assertIsNone(action.last_deadline_reminder)

    def test_advanced_to_set_relation(self):
        _, branch1, actions = self._create_inforequest_scenario(
                (u'advancement', [], [], [], []), # Advanced to 4 branches
                )
        _, (advancement, [(p1, _), (p2, _), (p3, _), (p4, _)]) = actions
        result = advancement.advanced_to_set.all()
        self.assertItemsEqual(result, [p1, p2, p3, p4])

    def test_advanced_to_set_relation_empty_by_default(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        result = action.advanced_to_set.all()
        self.assertItemsEqual(result, [])

    def test_branch_action_set_backward_relation(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action1 = self._create_action(branch=branch)
        action2 = self._create_action(branch=branch)
        result = branch.action_set.all()
        self.assertItemsEqual(result, [action1, action2])

    def test_branch_action_set_backward_relation_empty_by_default(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        result = branch.action_set.all()
        self.assertItemsEqual(result, [])

    def test_message_action_backward_relation(self):
        _, branch1, (request,) = self._create_inforequest_scenario()
        self.assertEqual(request.email.action, request)

    def test_message_action_backward_relation_undefined_by_default(self):
        email = self._create_message()
        with self.assertRaisesMessage(Action.DoesNotExist, u'Message has no action.'):
            email.action

    def test_no_default_ordering(self):
        self.assertFalse(Action.objects.all().ordered)

    def test_prefetch_attachments_staticmethod(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        attachment1 = self._create_attachment(generic_object=action)
        attachment2 = self._create_attachment(generic_object=action)

        # Without arguments
        with self.assertNumQueries(2):
            action = Action.objects.prefetch_related(Action.prefetch_attachments()).get(pk=action.pk)
        with self.assertNumQueries(0):
            self.assertEqual(action.attachments, [attachment1, attachment2])

        # With custom path and queryset
        with self.assertNumQueries(3):
            branch = (Branch.objects
                    .prefetch_related(Branch.prefetch_actions())
                    .prefetch_related(Action.prefetch_attachments(u'actions', Attachment.objects.extra(select=dict(moo=47))))
                    .get(pk=branch.pk))
        with self.assertNumQueries(0):
            self.assertEqual(branch.actions[0].attachments, [attachment1, attachment2])
            self.assertEqual(branch.actions[0].attachments[0].moo, 47)

    def test_attachments_property(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        attachment1 = self._create_attachment(generic_object=action)
        attachment2 = self._create_attachment(generic_object=action)

        # Property is cached
        with self.assertNumQueries(1):
            action = Action.objects.get(pk=action.pk)
        with self.assertNumQueries(1):
            self.assertEqual(action.attachments, [attachment1, attachment2])
        with self.assertNumQueries(0):
            self.assertEqual(action.attachments, [attachment1, attachment2])

        # Property is prefetched with prefetch_attachments()
        with self.assertNumQueries(2):
            action = Action.objects.prefetch_related(Action.prefetch_attachments()).get(pk=action.pk)
        with self.assertNumQueries(0):
            self.assertEqual(action.attachments, [attachment1, attachment2])

    def test_is_applicant_is_obligee_and_is_implicit_action_properties(self):
        tests = (                                   # Applicant, Obligee, Implicit
                (Action.TYPES.REQUEST,                True,      False,   False),
                (Action.TYPES.CLARIFICATION_RESPONSE, True,      False,   False),
                (Action.TYPES.APPEAL,                 True,      False,   False),
                (Action.TYPES.CONFIRMATION,           False,     True,    False),
                (Action.TYPES.EXTENSION,              False,     True,    False),
                (Action.TYPES.ADVANCEMENT,            False,     True,    False),
                (Action.TYPES.CLARIFICATION_REQUEST,  False,     True,    False),
                (Action.TYPES.DISCLOSURE,             False,     True,    False),
                (Action.TYPES.REFUSAL,                False,     True,    False),
                (Action.TYPES.AFFIRMATION,            False,     True,    False),
                (Action.TYPES.REVERSION,              False,     True,    False),
                (Action.TYPES.REMANDMENT,             False,     True,    False),
                (Action.TYPES.ADVANCED_REQUEST,       False,     False,   True),
                (Action.TYPES.EXPIRATION,             False,     False,   True),
                (Action.TYPES.APPEAL_EXPIRATION,      False,     False,   True),
                )
        # Make sure we are testing all defined action types
        tested_action_types = [a for a, _, _, _ in tests]
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for action_type, is_applicant, is_obligee, is_implicit in tests:
            action = self._create_action(branch=branch, type=action_type)
            self.assertEqual(action.is_applicant_action, is_applicant)
            self.assertEqual(action.is_obligee_action, is_obligee)
            self.assertEqual(action.is_implicit_action, is_implicit)

    @contextlib.contextmanager
    def _test_deadline_missed_aux(self, **kwargs):
        action = self._create_action(legal_date=naive_date(u'2010-10-05'), delivered_date=naive_date(u'2010-10-05'), **kwargs)
        timewarp.jump(local_datetime_from_local(u'2010-10-10 10:33:00'))
        with mock.patch(u'chcemvediet.apps.inforequests.models.action.workdays.between', side_effect=lambda a,b,*args: (b-a).days):
            yield action

    def test_deadline_workdays_passed_property_and_deadline_workdays_passed_at_method(self):
        with self._test_deadline_missed_aux() as action:
            self.assertEqual(action.deadline.workdays_passed, 5)
            self.assertEqual(action.deadline.workdays_passed_at(local_today()), 5)

    def test_deadline_workdays_remaining_property_and_deadline_workdays_remaining_at_method_without_extension(self):
        with self._test_deadline_missed_aux(omit=[u'extension']) as action:
            self.assertEqual(action.deadline.workdays_remaining, 3)
            self.assertEqual(action.deadline.workdays_remaining_at(local_today()), 3)

    def test_deadline_workdays_remaining_property_and_deadline_workdays_remaining_at_method_with_extension(self):
        branch = self._create_branch()
        previous = self._create_action(branch=branch, type=Action.TYPES.REQUEST, delivered_date=naive_date(u'2010-10-05'))
        with self._test_deadline_missed_aux(branch=branch, type=Action.TYPES.EXTENSION, extension=4) as action:
            self.assertEqual(action.deadline.workdays_remaining, 7)
            self.assertEqual(action.deadline.workdays_remaining_at(local_today()), 7)

    def test_action_without_deadline(self):
        with self._test_deadline_missed_aux(type=Action.TYPES.REVERSION) as action:
            self.assertIsNone(action.deadline)

    def test_deadline_is_deadline_missed_property_and_deadline_is_deadline_missed_at_method_with_not_missed_deadline(self):
        with self._test_deadline_missed_aux() as action:
            self.assertFalse(action.deadline.is_deadline_missed)
            self.assertFalse(action.deadline.is_deadline_missed_at(local_today()))

    def test_deadline_is_deadline_missed_property_and_deadline_is_deadline_missed_at_method_with_missed_deadline(self):
        with self._test_deadline_missed_aux() as action:
            timewarp.jump(local_datetime_from_local(u'2010-10-15 10:33:00'))
            self.assertTrue(action.deadline.is_deadline_missed)
            self.assertTrue(action.deadline.is_deadline_missed_at(local_today()))

    def test_deadline_missed_property_and_deadline_missed_at_method_with_extended_missed_deadline(self):
        branch = self._create_branch()
        previous = self._create_action(branch=branch, type=Action.TYPES.REQUEST, delivered_date=naive_date(u'2010-09-29'))
        with self._test_deadline_missed_aux(branch=branch, type=Action.TYPES.EXTENSION, extension=3) as action:
            self.assertFalse(action.deadline.is_deadline_missed)
            self.assertFalse(action.deadline.is_deadline_missed_at(local_today()))

    def test_deadline_missed_property_and_deadline_missed_at_method_with_extended_missed_deadline_missed_again(self):
        branch = self._create_branch()
        previous = self._create_action(branch=branch, type=Action.TYPES.REQUEST, delivered_date=naive_date(u'2010-09-29'))
        with self._test_deadline_missed_aux(branch=branch, type=Action.TYPES.EXTENSION, extension=2) as action:
            self.assertTrue(action.deadline.is_deadline_missed)
            self.assertTrue(action.deadline.is_deadline_missed_at(local_today()))

    def test_has_deadline_has_applicant_deadline_and_has_obligee_deadline_methods(self):
        tests = (                     # has deadline: any,   applicant, obligee
                (Action.TYPES.REQUEST,                True,  False,     True,  dict()),
                (Action.TYPES.CLARIFICATION_RESPONSE, True,  False,     True,  dict()),
                (Action.TYPES.APPEAL,                 True,  False,     True,  dict()),
                (Action.TYPES.CONFIRMATION,           True,  False,     True,  dict()),
                (Action.TYPES.EXTENSION,              True,  False,     True,  dict()),
                (Action.TYPES.ADVANCEMENT,            False, False,     False, dict()),
                (Action.TYPES.CLARIFICATION_REQUEST,  True,  True,      False, dict()),
                (Action.TYPES.DISCLOSURE,             True,  True,      False, dict(disclosure_level=Action.DISCLOSURE_LEVELS.NONE)),
                (Action.TYPES.DISCLOSURE,             True,  True,      False, dict(disclosure_level=Action.DISCLOSURE_LEVELS.PARTIAL)),
                (Action.TYPES.DISCLOSURE,             False, False,     False, dict(disclosure_level=Action.DISCLOSURE_LEVELS.FULL)),
                (Action.TYPES.REFUSAL,                True,  True,      False, dict()),
                (Action.TYPES.AFFIRMATION,            False, False,     False, dict()),
                (Action.TYPES.REVERSION,              False, False,     False, dict()),
                (Action.TYPES.REMANDMENT,             True,  False,     True,  dict()),
                (Action.TYPES.ADVANCED_REQUEST,       True,  False,     True,  dict()),
                (Action.TYPES.EXPIRATION,             True,  True,     False, dict()),
                (Action.TYPES.APPEAL_EXPIRATION,      False, False,     False, dict()),
                )
        # Make sure we are testing all defined action types
        tested_action_types = set(a for a, _, _, _, _ in tests)
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for action_type, has_deadline, has_applicant_deadline, has_obligee_deadline, extra_args in tests:
            action = self._create_action(branch=branch, type=action_type, delivered_date=naive_date(u'2010-10-05'), **extra_args)
            self.assertEqual(bool(action.deadline), has_deadline)
            self.assertEqual(action.has_applicant_deadline, has_applicant_deadline)
            self.assertEqual(action.has_obligee_deadline, has_obligee_deadline)

    def test_send_by_email_works_only_for_applicant_actions(self):
        tests = (
                (Action.TYPES.REQUEST,                True),
                (Action.TYPES.CLARIFICATION_RESPONSE, True),
                (Action.TYPES.APPEAL,                 True),
                (Action.TYPES.CONFIRMATION,           False),
                (Action.TYPES.EXTENSION,              False),
                (Action.TYPES.ADVANCEMENT,            False),
                (Action.TYPES.CLARIFICATION_REQUEST,  False),
                (Action.TYPES.DISCLOSURE,             False),
                (Action.TYPES.REFUSAL,                False),
                (Action.TYPES.AFFIRMATION,            False),
                (Action.TYPES.REVERSION,              False),
                (Action.TYPES.REMANDMENT,             False),
                (Action.TYPES.ADVANCED_REQUEST,       False),
                (Action.TYPES.EXPIRATION,             False),
                (Action.TYPES.APPEAL_EXPIRATION,      False),
                )
        # Make sure we are testing all defined action types
        tested_action_types = [a for a, _ in tests]
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        for action_type, can_send in tests:
            action = self._create_action(branch=branch, type=action_type)
            if can_send:
                with created_instances(Message.objects) as message_set:
                    action.send_by_email()
                email = message_set.get()
                self.assertEqual(email.type, Message.TYPES.OUTBOUND)
                self.assertEqual(action.email, email)
                self.assertIn(email, inforequest.email_set.all())
                rel = InforequestEmail.objects.get(email=email)
                self.assertEqual(rel.inforequest, inforequest)
                self.assertEqual(rel.type, InforequestEmail.TYPES.APPLICANT_ACTION)
            else:
                with created_instances(Message.objects) as message_set:
                    with self.assertRaisesMessage(TypeError, u'is not applicant action'):
                        action.send_by_email()
                self.assertEqual(message_set.count(), 0)

    def test_send_by_email_from_name_and_from_mail(self):
        with self.settings(INFOREQUEST_UNIQUE_EMAIL=u'{token}@example.com'):
            with mock.patch(u'chcemvediet.apps.inforequests.models.inforequest.random_readable_string', return_value=u'aaaa'):
                user = self._create_user(first_name=u'John', last_name=u'Smith')
                inforequest = self._create_inforequest(applicant=user)
                branch = self._create_branch(inforequest=inforequest)
                action = self._create_action(branch=branch)

                with created_instances(Message.objects) as message_set:
                    action.send_by_email()
                email = message_set.get()

                self.assertEqual(email.from_name, u'John Smith')
                self.assertEqual(email.from_mail, u'aaaa@example.com')

    def test_send_by_email_collected_recipients(self):
        obligee = self._create_obligee(emails=u'Obligee1 <oblige1@a.com>, oblige2@a.com')
        _, branch, _ = self._create_inforequest_scenario(obligee,
                (u'request', dict(
                    email=dict(from_name=u'Request From', from_mail=u'request-from@a.com'),
                    recipients=[
                        dict(name=u'Request To1', mail=u'request-to1@a.com', type=Recipient.TYPES.TO),
                        dict(name=u'Request To2', mail=u'request-to2@a.com', type=Recipient.TYPES.TO),
                        dict(name=u'Request Cc', mail=u'request-cc@a.com', type=Recipient.TYPES.CC),
                        dict(name=u'Request Bcc', mail=u'request-bcc@a.com', type=Recipient.TYPES.BCC),
                        ],
                    )),
                (u'refusal', dict(
                    email=dict(from_name=u'Refusal From', from_mail=u'refusal-from@a.com'),
                    recipients=[
                        dict(name=u'Refusal To', mail=u'refusal-to@a.com', type=Recipient.TYPES.TO),
                        dict(name=u'Refusal Cc', mail=u'refusal-cc@a.com', type=Recipient.TYPES.CC),
                        dict(name=u'Refusal Bcc', mail=u'refusal-bcc@a.com', type=Recipient.TYPES.BCC),
                        ],
                    )),
                )
        action = self._create_action(branch=branch)

        with created_instances(Message.objects) as message_set:
            action.send_by_email()
        email = message_set.get()

        result = [r.formatted for r in email.recipient_set.to()]
        self.assertItemsEqual(result, [
                u'Request To1 <request-to1@a.com>',
                u'Request To2 <request-to2@a.com>',
                u'Request Cc <request-cc@a.com>',
                u'Request Bcc <request-bcc@a.com>',
                # Inbound email contributes with its from address only
                u'Refusal From <refusal-from@a.com>',
                # Current obligee addresses
                u'Obligee1 <oblige1@a.com>',
                u'oblige2@a.com',
            ])

    def test_send_by_email_subject_and_content(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch, subject=u'Subject', content=u'Content')

        with created_instances(Message.objects) as message_set:
            action.send_by_email()
        email = message_set.get()

        self.assertEqual(email.subject, u'Subject')
        self.assertEqual(email.text, u'Content')
        self.assertEqual(email.html, u'')

    def test_send_by_email_attachments(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        attachment1 = self._create_attachment(generic_object=action, name=u'filename.txt', content=u'Content', content_type=u'text/plain')
        attachment2 = self._create_attachment(generic_object=action, name=u'filename.html', content=u'<html><body>HTML content</body></html>', content_type=u'text/html')

        with created_instances(Message.objects) as message_set:
            action.send_by_email()
        email = message_set.get()

        result = ((a.name, a.content, a.content_type) for a in email.attachment_set.all())
        self.assertItemsEqual(result, [
            (u'filename.txt', u'Content', u'text/plain'),
            (u'filename.html', u'<html><body>HTML content</body></html>', u'text/html'),
            ])

    def test_repr(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        action = self._create_action(branch=branch)
        self.assertEqual(repr(action), u'<Action: [{}] {}>'.format(action.pk, action.get_extended_type_display()).encode(encoding=u'utf-8'))

    def test_action_type_query_methods(self):
        Action.objects.all().delete()
        tests = (
                (Action.TYPES.REQUEST,                u'requests'),
                (Action.TYPES.CLARIFICATION_RESPONSE, u'clarification_responses'),
                (Action.TYPES.APPEAL,                 u'appeals'),
                (Action.TYPES.CONFIRMATION,           u'confirmations'),
                (Action.TYPES.EXTENSION,              u'extensions'),
                (Action.TYPES.ADVANCEMENT,            u'advancements'),
                (Action.TYPES.CLARIFICATION_REQUEST,  u'clarification_requests'),
                (Action.TYPES.DISCLOSURE,             u'disclosures'),
                (Action.TYPES.REFUSAL,                u'refusals'),
                (Action.TYPES.AFFIRMATION,            u'affirmations'),
                (Action.TYPES.REVERSION,              u'reversions'),
                (Action.TYPES.REMANDMENT,             u'remandments'),
                (Action.TYPES.ADVANCED_REQUEST,       u'advanced_requests'),
                (Action.TYPES.EXPIRATION,             u'expirations'),
                (Action.TYPES.APPEAL_EXPIRATION,      u'appeal_expirations'),
                )
        # Make sure we are testing all defined action types
        tested_action_types = [a for a, _ in tests]
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        actions = defaultdict(list)
        for i in range(3):
            for action_type, _ in tests:
                actions[action_type].append(self._create_action(branch=branch, type=action_type))

        for action_type, query_method in tests:
            result = getattr(Action.objects, query_method)()
            self.assertItemsEqual(result, actions[action_type])

    def test_applicant_obligee_and_implicit_actions_query_methods(self):
        Action.objects.all().delete()
        tests = (                                   # Applicant, Obligee, Implicit
                (Action.TYPES.REQUEST,                True,      False,   False),
                (Action.TYPES.CLARIFICATION_RESPONSE, True,      False,   False),
                (Action.TYPES.APPEAL,                 True,      False,   False),
                (Action.TYPES.CONFIRMATION,           False,     True,    False),
                (Action.TYPES.EXTENSION,              False,     True,    False),
                (Action.TYPES.ADVANCEMENT,            False,     True,    False),
                (Action.TYPES.CLARIFICATION_REQUEST,  False,     True,    False),
                (Action.TYPES.DISCLOSURE,             False,     True,    False),
                (Action.TYPES.REFUSAL,                False,     True,    False),
                (Action.TYPES.AFFIRMATION,            False,     True,    False),
                (Action.TYPES.REVERSION,              False,     True,    False),
                (Action.TYPES.REMANDMENT,             False,     True,    False),
                (Action.TYPES.ADVANCED_REQUEST,       False,     False,   True),
                (Action.TYPES.EXPIRATION,             False,     False,   True),
                (Action.TYPES.APPEAL_EXPIRATION,      False,     False,   True),
                )
        # Make sure we are testing all defined action types
        tested_action_types = [a for a, _, _, _ in tests]
        defined_action_types = Action.TYPES._inverse.keys()
        self.assertItemsEqual(tested_action_types, defined_action_types)

        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        applicant_actions = []
        obligee_actions = []
        implicit_actions = []
        for i in range(3):
            for action_type, is_applicant, is_obligee, is_implicit in tests:
                action = self._create_action(branch=branch, type=action_type)
                if is_applicant:
                    applicant_actions.append(action)
                if is_obligee:
                    obligee_actions.append(action)
                if is_implicit:
                    implicit_actions.append(action)

        applicant_result = Action.objects.applicant_actions()
        obligee_result = Action.objects.obligee_actions()
        implicit_result = Action.objects.implicit_actions()
        self.assertItemsEqual(applicant_result, applicant_actions)
        self.assertItemsEqual(obligee_result, obligee_actions)
        self.assertItemsEqual(implicit_result, implicit_actions)

    def test_by_email_and_by_smail_query_methods(self):
        Action.objects.all().delete()
        _, branch, actions = self._create_inforequest_scenario(
                u'confirmation',
                u'refusal',
                (u'appeal', dict(email=False)),
                (u'remandment', dict(email=False)),
                u'extension', # Extension is not sent
                u'expiration',
                )
        request, confirmation, refusal, appeal, remandment, extension, expiration = actions

        result_by_email = Action.objects.by_email()
        result_by_smail = Action.objects.by_smail()
        self.assertItemsEqual(result_by_email, [request, confirmation, refusal, extension])
        self.assertItemsEqual(result_by_smail, [appeal, remandment, expiration])

    def test_order_by_pk_query_method(self):
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        actions = [self._create_action(branch=branch) for _ in range(20)]
        sample = random.sample(actions, 10)
        result = Action.objects.filter(pk__in=(d.pk for d in sample)).order_by_pk().reverse()
        self.assertEqual(list(result), sorted(sample, key=lambda d: -d.pk))

    def test_order_by_created_query_method(self):
        dates = [
                u'2014-10-04',
                u'2014-10-05',
                u'2014-10-06', # Several with the same date, to check secondary ordering
                u'2014-10-06',
                u'2014-10-06',
                u'2014-10-06',
                u'2014-10-06',
                u'2014-11-05',
                u'2015-10-05',
                ]
        random.shuffle(dates)
        inforequest = self._create_inforequest()
        branch = self._create_branch(inforequest=inforequest)
        actions = []
        for date in dates:
            actions.append(self._create_action(branch=branch, created=naive_date(date), subject=u'order_by'))
        result = Action.objects.filter(subject=u'order_by').order_by_created()
        self.assertEqual(list(result), sorted(actions, key=lambda a: (a.created, a.pk)))
