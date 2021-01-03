import os
from testfixtures import TempDirectory

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from chcemvediet.apps.anonymization.models import AttachmentFinalization
from chcemvediet.tests import ChcemvedietTestCaseMixin


class AttachmentAnonymizationManagementCommandTest(ChcemvedietTestCaseMixin, TestCase):

    def _pre_setup(self):
        super(AttachmentAnonymizationManagementCommandTest, self)._pre_setup()
        self.tempdir = TempDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.tempdir.path,
        )
        self.settings_override.enable()
        self.attachment = self._create_attachment()

    def _post_teardown(self):
        self.settings_override.disable()
        self.tempdir.cleanup()
        super(AttachmentAnonymizationManagementCommandTest, self)._post_teardown()

    def _create_attachment(self, **kwargs):
        return super(AttachmentAnonymizationManagementCommandTest, self)._create_attachment(
                generic_object=self.action,
                **kwargs
                )


    def test_attachment_anonymization_command_with_valid_arguments_creates_attachment_finalization(self):
        with open(os.path.join(self.tempdir.path, u'myfile.txt'), u'w') as file:
            call_command(u'attachment_anonymization', self.attachment.pk, file.name)
            AttachmentFinalization.objects.get(attachment=self.attachment)

    def test_attachment_anonymization_command_file_option(self):
        with open(os.path.join(self.tempdir.path, u'myfile.txt'), u'w') as file:
            call_command(u'attachment_anonymization', self.attachment.pk, filename=file.name)
            AttachmentFinalization.objects.get(attachment=self.attachment)

    def test_attachment_anonymization_command_content_type_option(self):
        with open(os.path.join(self.tempdir.path, u'myfile.txt'), u'w') as file:
            call_command(u'attachment_anonymization', self.attachment.pk, file.name, content_type=u'type')
            attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
            self.assertEqual(attachment_finalization.content_type, u'type')

    def test_attachment_anonymization_command_debug_option(self):
        with open(os.path.join(self.tempdir.path, u'myfile.txt'), u'w') as file:
            call_command(u'attachment_anonymization', self.attachment.pk, file.name, debug=u'debug')
            attachment_finalization = AttachmentFinalization.objects.get(attachment=self.attachment)
            self.assertEqual(attachment_finalization.debug, u'debug')

    def test_attachment_anonymization_command_with_existing_attachment_finalization(self):
        with open(os.path.join(self.tempdir.path, u'myfile.txt'), u'w') as file:
            call_command(u'attachment_anonymization', self.attachment.pk, file.name)
            attachment_finalization1 = AttachmentFinalization.objects.get(attachment=self.attachment)
            call_command(u'attachment_anonymization', self.attachment.pk, file.name)
            attachment_finalization2 = AttachmentFinalization.objects.get(attachment=self.attachment)
            self.assertEqual(attachment_finalization1.pk, attachment_finalization2.pk)

    def test_attachment_anonymization_command_force_option(self):
        with open(os.path.join(self.tempdir.path, u'myfile.txt'), u'w') as file:
            call_command(u'attachment_anonymization', self.attachment.pk, file.name)
            attachment_finalization1 = AttachmentFinalization.objects.get(attachment=self.attachment)
            call_command(u'attachment_anonymization', self.attachment.pk, file.name, force=True)
            attachment_finalization2 = AttachmentFinalization.objects.get(attachment=self.attachment)
            self.assertNotEqual(attachment_finalization1.pk, attachment_finalization2.pk)
