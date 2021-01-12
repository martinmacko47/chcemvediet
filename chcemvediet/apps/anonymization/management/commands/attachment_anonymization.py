from optparse import make_option

import magic
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from poleno.attachments.models import Attachment
from poleno.utils.misc import squeeze
from chcemvediet.apps.anonymization.models import AttachmentFinalization
from chcemvediet.apps.inforequests.models import Action


class Command(BaseCommand):
    args = u'attachment [file]'
    help = squeeze(u"""
            Creates anonymization for the specified Attachment. By default, the file path is read
            from stdin. File path can be explicitly passed as an command argument. Anonymization
            created this way will be marked as successful. Only one successful anonymization can be
            assigned to the Attachment.
            """)

    option_list = BaseCommand.option_list + (
        make_option(u'--content_type',
                    help=squeeze(u"""
                            Content type of file, e.g. "application/pdf". Automatically computed if
                            not specified.
                            """)
                    ),
        make_option(u'--debug',
                    default=u'',
                    help=u'Debug message to the newly created anonymization. Empty by default.'
                    ),
        make_option(u'--force',
                    action=u'store_true',
                    help=squeeze(u"""
                            The command refuses to anonymize attachment if a successful
                            anonymization already exists. This flag disables this check. Deletes all
                            existing successful anonymizations and creates new one. Unsuccessful
                            anonymizations will stay unaffected.
                            """)
                    ),
    )

    def handle(self, *args, **options):
        if not args:
            raise CommandError(u'attachment_anonymization takes at least 1 argument (0 given).')
        if len(args) > 2:
            raise CommandError(
                u'attachment_anonymization takes at most 2 arguments ({} given).'.format(len(args))
                )
        pk = args[0]
        filename = args[1] if len(args) == 2 else raw_input(u'File:')
        if not filename:
            raise CommandError(u'Missing source file name.')
        with open(filename, u'rb') as file:
            try:
                attachment = Attachment.objects.attached_to(Action).get(pk=pk)
                attachments_finalization = (AttachmentFinalization.objects
                                            .filter(attachment=attachment)
                                            .successful())
                if options[u'force'] or not attachments_finalization:
                    attachments_finalization.delete()
                    content = file.read()
                    content_type = magic.from_buffer(content, mime=True)
                    AttachmentFinalization.objects.create(
                        attachment=attachment,
                        successful=True,
                        file=ContentFile(content),
                        content_type=options[u'content_type'] or content_type,
                        debug=options[u'debug'],
                    )
                else:
                    raise CommandError(squeeze(u"""
                            Anonymization files already exist. Use the --force option to overwrite
                            them.
                            """))
            except Attachment.DoesNotExist:
                raise CommandError(u'Attachment instance with pk {} does not exist.'.format(pk))
