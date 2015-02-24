# vim: expandtab
# -*- coding: utf-8 -*-
import traceback

from django.db import transaction
from django.conf import settings

from poleno.cron import cron_job, cron_logger
from poleno.workdays import workdays
from poleno.utils.translation import translation
from poleno.utils.date import local_date, local_today

from .models import Inforequest, Branch

# All these jobs do all their work the first time they are run in a day. Any later runs in the same
# day should do nothing. However, we run them multiple times in a day in case something was broken
# at the morning and the jobs failed.
RUN_AT_TIMES = [u'09:00', u'10:00', u'11:00', u'12:00', u'13:00', u'14:00']

@cron_job(run_at_times=RUN_AT_TIMES)
@transaction.atomic
def undecided_email_reminder():
    with translation(settings.LANGUAGE_CODE):
        inforequests = (Inforequest.objects
                .not_closed()
                .with_undecided_email()
                .prefetch_related(Inforequest.prefetch_newest_undecided_email())
                )

        filtered = []
        for inforequest in inforequests:
            try:
                email = inforequest.newest_undecided_email
                last = inforequest.last_undecided_email_reminder
                if last and last > email.processed:
                    continue
                days = workdays.between(local_date(email.processed), local_today())
                if days < 5:
                    continue
                filtered.append(inforequest)
            except Exception:
                cron_logger.error(u'Checking if undecided email reminder should be sent failed: %s\n%s' % (repr(inforequest), traceback.format_exc()))

        if not filtered:
            return

        filtered = (Inforequest.objects
                .select_related(u'applicant')
                .select_undecided_emails_count()
                .prefetch_related(Inforequest.prefetch_main_branch(None, Branch.objects.select_related(u'historicalobligee')))
                .prefetch_related(Inforequest.prefetch_newest_undecided_email())
                .filter(pk__in=(o.pk for o in filtered))
                )
        for inforequest in filtered:
            try:
                with transaction.atomic():
                    inforequest.send_undecided_email_reminder()
                    cron_logger.info(u'Sent undecided email reminder: %s' % repr(inforequest))
            except Exception:
                cron_logger.error(u'Sending undecided email reminder failed: %s\n%s' % (repr(inforequest), traceback.format_exc()))

@cron_job(run_at_times=RUN_AT_TIMES)
@transaction.atomic
def obligee_deadline_reminder():
    with translation(settings.LANGUAGE_CODE):
        inforequests = (Inforequest.objects
                .not_closed()
                .without_undecided_email()
                .prefetch_related(Inforequest.prefetch_branches())
                .prefetch_related(Branch.prefetch_last_action(u'branches'))
                )

        filtered = []
        for inforequest in inforequests:
            for branch in inforequest.branches:
                try:
                    if not branch.last_action.has_obligee_deadline:
                        continue
                    if not branch.last_action.deadline_missed:
                        continue
                    # The last reminder was sent after the deadline was extended for the last time iff
                    # the extended deadline was missed before the reminder was sent. We don't want to
                    # send any more reminders if the last reminder was sent after the deadline was
                    # extended for the last time.
                    last = branch.last_action.last_deadline_reminder
                    last_date = local_date(last) if last else None
                    if last and branch.last_action.deadline_missed_at(last_date):
                        continue
                    filtered.append(branch)
                except Exception:
                    cron_logger.error(u'Checking if obligee deadline reminder should be sent failed: %s\n%s' % (repr(branch.last_action), traceback.format_exc()))

        if not filtered:
            return

        filtered = (Branch.objects
                .select_related(u'inforequest__applicant')
                .select_related(u'historicalobligee')
                .prefetch_related(Branch.prefetch_last_action())
                .filter(pk__in=(o.pk for o in filtered))
                )
        for branch in filtered:
            try:
                with transaction.atomic():
                    branch.inforequest.send_obligee_deadline_reminder(branch.last_action)
                    cron_logger.info(u'Sent obligee deadline reminder: %s' % repr(branch.last_action))
            except Exception:
                cron_logger.error(u'Sending obligee deadline reminder failed: %s\n%s' % (repr(branch.last_action), traceback.format_exc()))

@cron_job(run_at_times=RUN_AT_TIMES)
@transaction.atomic
def applicant_deadline_reminder():
    with translation(settings.LANGUAGE_CODE):
        inforequests = (Inforequest.objects
                .not_closed()
                .without_undecided_email()
                .prefetch_related(Inforequest.prefetch_branches())
                .prefetch_related(Branch.prefetch_last_action(u'branches'))
                )

        filtered = []
        for inforequest in inforequests:
            for branch in inforequest.branches:
                try:
                    if not branch.last_action.has_applicant_deadline:
                        continue
                    # The reminder is sent 2 WDs before the deadline is missed.
                    if branch.last_action.deadline_remaining > 2:
                        continue
                    # Applicant deadlines may not be extended, so we send at most one applicant
                    # deadline reminder for the action.
                    if branch.last_action.last_deadline_reminder:
                        continue
                    filtered.append(branch)
                except Exception:
                    cron_logger.error(u'Checking if applicant deadline reminder should be sent failed: %s\n%s' % (repr(branch.last_action), traceback.format_exc()))

        if not filtered:
            return

        filtered = (Branch.objects
                .select_related(u'inforequest__applicant')
                .prefetch_related(Branch.prefetch_last_action())
                .filter(pk__in=(o.pk for o in filtered))
                )
        for branch in filtered:
            try:
                with transaction.atomic():
                    branch.inforequest.send_applicant_deadline_reminder(branch.last_action)
                    cron_logger.info(u'Sent applicant deadline reminder: %s' % repr(branch.last_action))
            except Exception:
                cron_logger.error(u'Sending applicant deadline reminder failed: %s\n%s' % (repr(branch.last_action), traceback.format_exc()))

@cron_job(run_at_times=RUN_AT_TIMES)
@transaction.atomic
def close_inforequests():
    inforequests = (Inforequest.objects
            .not_closed()
            .prefetch_related(Inforequest.prefetch_branches())
            .prefetch_related(Branch.prefetch_last_action(u'branches'))
            )

    filtered = []
    for inforequest in inforequests:
        try:
            for branch in inforequest.branches:
                if branch.last_action.has_deadline and branch.last_action.deadline_remaining > -100:
                    break
            else:
                # Every branch that has a deadline have been missed for at least 100 WD.
                filtered.append(inforequest)
        except Exception:
            cron_logger.error(u'Checking if inforequest should be closed failed: %s\n%s' % (repr(inforequest), traceback.format_exc()))

    for inforequest in filtered:
        try:
            with transaction.atomic():
                for branch in inforequest.branches:
                    branch.add_expiration_if_expired()
                inforequest.closed = True
                inforequest.save()
                cron_logger.info(u'Closed inforequest: %s' % repr(inforequest))
        except Exception:
            cron_logger.error(u'Closing inforequest failed: %s\n%s' % (repr(inforequest), traceback.format_exc()))
