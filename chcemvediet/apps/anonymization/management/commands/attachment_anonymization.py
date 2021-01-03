from optparse import make_option

import magic
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from poleno.attachments.models import Attachment
from chcemvediet.apps.anonymization.models import AttachmentFinalization
from chcemvediet.apps.inforequests.models import Action


class Command(BaseCommand):
    help = u'Creates AttachmentFinalization for the specified Attachment.'

    option_list = BaseCommand.option_list + (
        make_option(u'-f', u'--file',
                    dest=u'filename',
                    help=u'define file path'),
        make_option(u'--content_type',
                    help=u'define content type of file',
                    ),
        make_option(u'--debug',
                    default=u'',
                    help=u'add debug message'
                    ),
        make_option(u'--force',
                    action=u'store_true',
                    help=u'overwrite an existing successful AttachmentFinalization'
                    ),
    )

    def usage(self, subcommand=None):
        return u'manage.py attachment_anonymization attachment [options] [file]'

    def handle(self, *args, **options):
        try:
            filename = options[u'filename'] or args[1]
        except IndexError:
            self.stdout.write(u'Usage: {}'.format(self.usage()))
            self.stdout.write(
                u'Try "manage.py attachment_anonymization --help" for more information.')
            return 1

        with open(filename, u'rb') as file:
            try:
                attachment = (Attachment.objects
                              .attached_to(Action)
                              .not_normalized()
                              .get(pk=int(args[0])))
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
            except Attachment.DoesNotExist:
                raise CommandError(u'Attachment {} does not exist'.format(args[0]))
