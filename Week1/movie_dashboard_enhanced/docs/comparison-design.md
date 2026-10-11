# Enhanced movie analyzer

User-approved scope: implement the proposed improvements as a separate app,
leaving movie_dashboard intact. Use movie_dashboard_enhanced and port 8504.

Preserve the three-tab flow and all existing filters. Prepare a broader dataset
from train.csv with only essential-field eligibility, record exclusions, and
use Unknown for optional missing metadata. Add median revenue and counts;
ranked genre bars by default and optional pie; concise active-filter summary;
explicit USD, nominal revenue, release-year and sample-coverage limitations.

Implementation completed inline with tests before new preparation/view logic.
37 tests passed before final review. Source total and yearly total are
200,177,555,666 USD. Genre allocation reconciles within one cent; median is
16,807,068 USD. Original CSVs and application code were not edited.
