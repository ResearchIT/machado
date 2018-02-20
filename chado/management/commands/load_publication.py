"""Load Publication file."""

from chado.loaders.common import FileValidator
from chado.loaders.exceptions import ImportingError
from chado.loaders.publication import PublicationLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
# import os
from tqdm import tqdm
import bibtexparser


class Command(BaseCommand):
    """Load Publication file."""

    help = 'Load Publication file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="BibTeX File", required=True,
                            type=str)

    def handle(self,
               file=str,
               **options):
        """Execute the main function."""
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        # filename = os.path.basename(file)
        bib_database = 0
        try:
            bib_database = bibtexparser.load(open(file))
        except ValueError as e:
            return CommandError(e)

        cpu = options.get('cpu')
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for entry in bib_database.entries:
            # create model object for each entry
            if (entry['ENTRYTYPE']):
                bibtex = PublicationLoader(entry['ENTRYTYPE'])
                tasks.append(pool.submit(bibtex.store_bibtex_entry,
                                         entry))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Done'))
