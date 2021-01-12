import os
import sys
from StringIO import StringIO
from testfixtures import TempDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from chcemvediet.apps.anonymization.models import AttachmentFinalization
from chcemvediet.tests import ChcemvedietTestCaseMixin


class AttachmentAnonymizationManagementCommandTest(ChcemvedietTestCaseMixin, TestCase):

    def _pre_setup(self):
        super(AttachmentAnonymizationManagementCommandTest, self)._pre_setup()
        self.tempdir = TempDirectory()
        self.tempdir.write(u'testfile.txt', u'Default testing content')
        self.filename = os.path.join(self.tempdir.path, u'testfile.txt')
        self.attachment = self._create_attachment()

    def _post_teardown(self):
        self.tempdir.cleanup()
        super(AttachmentAnonymizationManagementCommandTest, self)._post_teardown()

    def _create_attachment(self, **kwargs):
        return super(AttachmentAnonymizationManagementCommandTest, self)._create_attachment(
                generic_object=self.action,
                **kwargs
                )


    def test_attachment_and_file_arguments(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename)
        attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
        self.assertEqual(attachment_finalization.attachment.pk, self.attachment.pk)
        self.assertEqual(attachment_finalization.file.read(), u'Default testing content')
        self.assertEqual(attachment_finalization.successful, True)

    def test_attachment_argument_may_not_be_omitted(self):
        with self.assertRaisesMessage(CommandError, u'attachment_anonymization takes at least 1 argument (0 given).'):
            call_command(u'attachment_anonymization')

    def test_non_existent_attachment_raises_exception(self):
        with self.assertRaisesMessage(CommandError, u'Attachment instance with pk -1 does not exist.'):
            call_command(u'attachment_anonymization', u'-1', self.filename)

    def test_command_with_too_many_arguments(self):
        with self.assertRaisesMessage(CommandError, u'attachment_anonymization takes at most 2 arguments (3 given).'):
            call_command(u'attachment_anonymization', self.attachment.pk, self.filename, u'filename2')

    def test_file_argument_is_read_from_stdin_if_omitted(self):
        self.addCleanup(setattr, sys, u'stdin', sys.stdin)
        sys.stdin = StringIO(self.filename)
        call_command(u'attachment_anonymization', self.attachment.pk)

    def test_file_argument_and_stdin_together_may_not_be_omitted(self):
        self.addCleanup(setattr, sys, u'stdin', sys.stdin)
        sys.stdin = StringIO(u'\n')
        with self.assertRaisesMessage(CommandError, u'Missing source file name.'):
            call_command(u'attachment_anonymization', self.attachment.pk)

    def test_content_type_option(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename, content_type=u'application/pdf')
        attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
        self.assertEqual(attachment_finalization.content_type, u'application/pdf')

    def test_content_type_option_default_value_if_omitted(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename)
        attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
        self.assertEqual(attachment_finalization.content_type, u'text/plain')

    def test_debug_option(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename, debug=u'debug')
        attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
        self.assertEqual(attachment_finalization.debug, u'debug')

    def test_debug_option_default_value_if_omitted(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename)
        attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
        self.assertEqual(attachment_finalization.debug, u'')

    def test_force_option(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename)
        attachment_finalization1 = AttachmentFinalization.objects.get(attachment=self.attachment)
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename, force=True)
        attachment_finalization2 = AttachmentFinalization.objects.get(attachment=self.attachment)
        with self.assertRaisesMessage(AttachmentFinalization.DoesNotExist, u'AttachmentFinalization matching query does not exist'):
            AttachmentFinalization.objects.get(pk=attachment_finalization1.pk)

    def test_existent_attachment_finalization_raises_exception_if_force_option_is_omitted(self):
        call_command(u'attachment_anonymization', self.attachment.pk, self.filename)
        attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
        with self.assertRaisesMessage(CommandError, u'Anonymization files already exist. Use the --force option to overwrite them.'):
            call_command(u'attachment_anonymization', self.attachment.pk, self.filename)
