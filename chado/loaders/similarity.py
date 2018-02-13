"""Load similarity file."""

from chado.models import Analysis, Analysisfeature, Feature, Featureloc
from chado.loaders.exceptions import ImportingError
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class SimilarityLoader(object):
    """Load similarity records."""

    help = 'Load simlarity records.'

    def __init__(self, program, programversion, *args, **kwargs):
        """Execute the init function."""
        try:
            self.analysis = Analysis.objects.create(
                    algorithm=kwargs.get('algorithm'),
                    description=kwargs.get('description'),
                    name=kwargs.get('name'),
                    program=program,
                    programversion=programversion,
                    timeexecuted=datetime.now(timezone.utc))
        except IntegrityError as e:
            raise ImportingError(e)

    def retrieve_id_from_description(self, description):
        """Retrieve ID from description."""
        for item in description.split(' '):
            try:
                key, value = item.split('=')
                if key == 'ID':
                    return value
            except ValueError:
                pass
        return None

    def store_ncbixml_record(self, record):
        """Store ncbixml record."""
        try:
            query_id = record.query.split(' ')[0]
            query_feature = Feature.objects.get(uniquename=query_id)
        except ObjectDoesNotExist as e1:
            try:
                query_id = self.retrieve_id_from_description(record.query)
                query_feature = Feature.objects.get(uniquename=query_id)
            except ObjectDoesNotExist as e2:
                raise ImportingError(e1, e2)

        # Retrieve only the first alignment since the model does not allow to
        # store more then one alignment per feature per analysis
        alignment = record.alignments[0]

        try:
            subject_id = alignment.title.split(' ')[0]
            subject_feature = Feature.objects.get(uniquename=subject_id)
        except ObjectDoesNotExist as e1:
            try:
                subject_id = self.retrieve_id_from_description(alignment.title)
                subject_feature = Feature.objects.get(uniquename=subject_id)
            except ObjectDoesNotExist as e2:
                raise ImportingError(e1, e2)

        # Retrieve only the first HSP since the model does not allow to store
        # more then one alignment per feature per analysis
        hsp = alignment.hsps[0]

        Analysisfeature.objects.create(analysis=self.analysis,
                                       feature=query_feature,
                                       identity=hsp.identities,
                                       rawscore=hsp.score,
                                       significance=hsp.expect)

        # Storing self.analysis.analysisfeature_id in locgroup in order to
        # comply to the Featureloc constraint (feature, locgroup, rank) and to
        # be able to track these records when erasing an analysis
        Featureloc.objects.create(feature=query_feature,
                                  srcfeature=subject_feature,
                                  fmax=hsp.sbjct_end,
                                  fmin=hsp.sbjct_start,
                                  is_fmax_partial=False,
                                  is_fmin_partial=False,
                                  locgroup=self.analysis.analysis_id,
                                  rank=0)
