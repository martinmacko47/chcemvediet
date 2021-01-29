from django.test import TestCase

from poleno.timewarp import timewarp
from poleno.utils.date import naive_date, local_today, local_datetime_from_local

from .. import InforequestsTestCaseMixin
from ...models.deadline import Deadline


class DeadlineTest(InforequestsTestCaseMixin, TestCase):
    u"""
    Tests ``Deadline`` model.
    """
    def _create_deadline(self, **kwargs):
        return self._call_with_defaults(Deadline, kwargs, {
            u'type': Deadline.TYPES.OBLIGEE_DEADLINE,
            u'base_date': local_today(),
            u'value': 8,
            u'unit': Deadline.UNITS.WORKDAYS,
            u'snooze': None,
        })


    def test_is_obligee_deadline_and_is_applicant_deadline_properties(self):
        tests = (
                (Deadline.TYPES.OBLIGEE_DEADLINE,   True,    False),
                (Deadline.TYPES.APPLICANT_DEADLINE, False,   True),
        )
        # Make sure we are testing all defined deadline types
        tested_deadline_types = [a for a, _, _ in tests]
        defined_deadline_types = vars(Deadline.TYPES).values()
        self.assertItemsEqual(tested_deadline_types, defined_deadline_types)

        for deadline_type, is_obligee_deadline, is_applicant_deadline in tests:
            deadline = self._create_deadline(type=deadline_type)
            self.assertEqual(deadline.is_obligee_deadline, is_obligee_deadline)
            self.assertEqual(deadline.is_applicant_deadline, is_applicant_deadline)

    def test_is_in_calendar_days_and_is_in_workdays_properties(self):
        tests = (
                (Deadline.UNITS.CALENDAR_DAYS, True,          False),
                (Deadline.UNITS.WORKDAYS,      False,         True),
        )
        # Make sure we are testing all defined deadline units
        tested_deadline_units = [a for a, _, _ in tests]
        defined_deadline_units = vars(Deadline.UNITS).values()
        self.assertItemsEqual(tested_deadline_units, defined_deadline_units)

        for deadline_unit, is_in_calendar_days, is_in_workdays in tests:
            deadline = self._create_deadline(unit=deadline_unit)
            self.assertEqual(deadline.is_in_calendar_days, is_in_calendar_days)
            self.assertEqual(deadline.is_in_workdays, is_in_workdays)

    def test_deadline_date_property(self):
        deadline1 = self._create_deadline(base_date=naive_date(u'2010-10-10'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS)
        self.assertEqual(deadline1.deadline_date, naive_date(u'2010-10-18'))
        deadline2 = self._create_deadline(base_date=naive_date(u'2010-10-10'), value=8, unit=Deadline.UNITS.WORKDAYS)
        self.assertEqual(deadline2.deadline_date, naive_date(u'2010-10-20'))

    def test_calendar_days_passed_property_and_calendar_days_passed_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-10 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'))
        self.assertEqual(deadline.calendar_days_passed, 5)
        self.assertEqual(deadline.calendar_days_passed_at(naive_date(u'2010-10-12')), 7)

    def test_workdays_passed_property_and_workdays_passed_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-10 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'))
        self.assertEqual(deadline.workdays_passed, 3)
        self.assertEqual(deadline.workdays_passed_at(naive_date(u'2010-10-12')), 5)

    def test_calendar_days_remaining_property_and_calendar_days_remaining_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-08 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS)
        self.assertEqual(deadline.calendar_days_remaining, 5)
        self.assertEqual(deadline.calendar_days_remaining_at(naive_date(u'2010-10-10')), 3)

    def test_workdays_remaining_property_and_workdays_remaining_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-08 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS)
        self.assertEqual(deadline.workdays_remaining, 3)
        self.assertEqual(deadline.workdays_remaining_at(naive_date(u'2010-10-12')), 1)

    def test_calendar_days_behind_property_and_calendar_days_behind_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-26 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS)
        self.assertEqual(deadline.calendar_days_behind, 13)
        self.assertEqual(deadline.calendar_days_behind_at(naive_date(u'2010-10-28')), 15)

    def test_workdays_behind_property_and_workdays_behind_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-26 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS)
        self.assertEqual(deadline.workdays_behind, 9)
        self.assertEqual(deadline.workdays_behind_at(naive_date(u'2010-10-28')), 11)

    def test_is_deadline_missed_property_and_is_deadline_missed_at_method(self):
        tests = (
                (Deadline.UNITS.CALENDAR_DAYS, naive_date(u'2010-10-13'), False),
                (Deadline.UNITS.CALENDAR_DAYS, naive_date(u'2010-10-14'), True),
                (Deadline.UNITS.WORKDAYS,      naive_date(u'2010-10-15'), False),
                (Deadline.UNITS.WORKDAYS,      naive_date(u'2010-10-16'), True),
        )
        for unit, today, is_deadline_missed in tests:
            timewarp.jump(today)
            deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=unit)
            self.assertEqual(deadline.is_deadline_missed, is_deadline_missed)
            self.assertEqual(deadline.is_deadline_missed_at(today), is_deadline_missed)

    def test_snooze_date_property(self):
        deadline1 = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-14'))
        self.assertEqual(deadline1.snooze_date, naive_date(u'2010-10-14'))
        deadline2 = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-12'))
        self.assertEqual(deadline2.snooze_date, naive_date(u'2010-10-13'))

    def test_snooze_date_property_default_value_if_omitted(self):
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=None)
        self.assertEqual(deadline.snooze_date, naive_date(u'2010-10-13'))

    def test_is_snoozed_property(self):
        deadline1 = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-14'))
        self.assertTrue(deadline1.is_snoozed)
        deadline2 = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-13'))
        self.assertFalse(deadline2.is_snoozed)

    def test_snooze_in_calendar_days_and_snooze_in_workdays_properties(self):
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-18'))
        self.assertEqual(deadline.snooze_in_calendar_days, 5)
        self.assertEqual(deadline.snooze_in_workdays, 3)

    def test_snooze_calendar_days_remaining_property_and_snooze_calendar_days_remaining_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-08 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-18'))
        self.assertEqual(deadline.snooze_calendar_days_remaining, 10)
        self.assertEqual(deadline.snooze_calendar_days_remaining_at(naive_date(u'2010-10-10')), 8)

    def test_snooze_workdays_remaining_property_and_snooze_workdays_remaining_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-08 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-18'))
        self.assertEqual(deadline.snooze_workdays_remaining, 6)
        self.assertEqual(deadline.snooze_workdays_remaining_at(naive_date(u'2010-10-12')), 4)

    def test_snooze_calendar_days_behind_property_and_snooze_calendar_days_behind_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-25 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-18'))
        self.assertEqual(deadline.snooze_calendar_days_behind, 7)
        self.assertEqual(deadline.snooze_calendar_days_behind_at(naive_date(u'2010-10-27')), 9)

    def test_snooze_workdays_behind_property_and_snooze_workdays_behind_at_method(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-25 10:33:00'))
        deadline = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-18'))
        self.assertEqual(deadline.snooze_workdays_behind, 5)
        self.assertEqual(deadline.snooze_workdays_behind_at(naive_date(u'2010-10-27')), 7)

    def test_is_snooze_missed_property_and_is_snooze_missed_at_methods(self):
        timewarp.jump(local_datetime_from_local(u'2010-10-26 10:33:00'))
        deadline1 = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-25'))
        self.assertTrue(deadline1.is_snooze_missed)
        self.assertTrue(deadline1.is_snooze_missed_at(naive_date(u'2010-10-26')))
        timewarp.jump(local_datetime_from_local(u'2010-10-24 10:33:00'))
        deadline2 = self._create_deadline(base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-25'))
        self.assertFalse(deadline2.is_snooze_missed)
        self.assertFalse(deadline2.is_snooze_missed_at(naive_date(u'2010-10-24')))

    def test_repr(self):
        deadline1 = self._create_deadline(type=Deadline.TYPES.APPLICANT_DEADLINE, base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.CALENDAR_DAYS, snooze=naive_date(u'2010-10-25'))
        self.assertEqual(repr(deadline1), u'<Deadline: 8 CD for Applicant since 2010-10-05 +12 CD>')
        deadline2 = self._create_deadline(type=Deadline.TYPES.OBLIGEE_DEADLINE, base_date=naive_date(u'2010-10-05'), value=8, unit=Deadline.UNITS.WORKDAYS, snooze=None)
        self.assertEqual(repr(deadline2), u'<Deadline: 8 WD for Obligee since 2010-10-05>')
