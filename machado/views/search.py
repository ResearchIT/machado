# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search views."""

from haystack.generic_views import FacetedSearchView
from machado.forms import FeatureSearchForm


class FeatureSearchView(FacetedSearchView):
    """Search view."""

    form_class = FeatureSearchForm
    facet_fields = ['organism', 'so_term', 'match_part']
    template_name = 'search_result.html'
    paginate_by = 25
    context_object_name = 'object_list'

    def get_queryset(self):
        """Get queryset."""
        queryset = super(FeatureSearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        return queryset

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super(FeatureSearchView, self).get_context_data(*args,
                                                                  **kwargs)
        context['total_count'] = self.queryset.count()
        return context
