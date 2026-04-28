# Retrieval queries (one per table / topic)
RETRIEVAL_QUERIES = {
    'life_insurance_premiums_deposits': (
        'Life Insurance GAAP premiums deposits reconciliation table '
        'domestic international 2019 2018 2017 years ended December 31'
    ),
    'institutional_markets_premiums_deposits': (
        'Institutional Markets GAAP premiums deposits reconciliation table '
        'GIC pension risk transfer 2019 2018 years ended December 31'
    ),
    'group_retirement_reserves_by_charge': (
        'Group Retirement annuity reserves surrender charge category '
        'no surrender charge greater than 0 2 4 percent total reserves December 31 2019'
    ),
    'business_sub_segment_names': (
        'Life and Retirement operating segments Group Retirement '
        'Life Insurance Institutional Markets domestic international life'
    ),
}

# Observation config, 15 observations from ground_truth2019.csv
OBSERVATIONS_CONFIG = [
    # Premiums_and_Deposits — Life Insurance (page 100 reconciliation table)
    {
        'obs_id':          'Obs_01',
        'variable':        'Premiums_and_Deposits',
        'var_type':        'numeric',
        'query_key':       'life_insurance_premiums_deposits',
        'source_page':     100,
        'description':     '2019 Life Insurance total Premiums and Deposits (millions USD)',
        'extraction_hint': (
            'Find the "Premiums and deposits" total for Life Insurance for fiscal year 2019 '
            '(first/leftmost data column) in the GAAP premiums-to-premiums-and-deposits '
            'reconciliation table.'
        ),
    },
    {
        'obs_id':          'Obs_02',
        'variable':        'Premiums_and_Deposits',
        'var_type':        'numeric',
        'query_key':       'life_insurance_premiums_deposits',
        'source_page':     100,
        'description':     '2018 Life Insurance total Premiums and Deposits (millions USD)',
        'extraction_hint': (
            'Find the "Premiums and deposits" total for Life Insurance for fiscal year 2018 '
            '(second/middle data column) in the GAAP premiums-to-premiums-and-deposits '
            'reconciliation table.'
        ),
    },
    {
        'obs_id':          'Obs_03',
        'variable':        'Premiums_and_Deposits',
        'var_type':        'numeric',
        'query_key':       'life_insurance_premiums_deposits',
        'source_page':     100,
        'description':     '2017 Life Insurance total Premiums and Deposits (millions USD)',
        'extraction_hint': (
            'Find the "Premiums and deposits" total for Life Insurance for fiscal year 2017 '
            '(third/rightmost data column) in the GAAP premiums-to-premiums-and-deposits '
            'reconciliation table.'
        ),
    },
    # Premiums_and_Deposits — Institutional Markets (page 102 reconciliation table)
    {
        'obs_id':          'Obs_04',
        'variable':        'Premiums_and_Deposits',
        'var_type':        'numeric',
        'query_key':       'institutional_markets_premiums_deposits',
        'source_page':     102,
        'description':     '2019 Institutional Markets total Premiums and Deposits (millions USD)',
        'extraction_hint': (
            'Find the "Premiums and deposits" total for Institutional Markets for fiscal year 2019 '
            '(first/leftmost data column) in the GAAP premiums-to-premiums-and-deposits '
            'reconciliation table on page 102.'
        ),
    },
    {
        'obs_id':          'Obs_05',
        'variable':        'Premiums_and_Deposits',
        'var_type':        'numeric',
        'query_key':       'institutional_markets_premiums_deposits',
        'source_page':     102,
        'description':     '2018 Institutional Markets total Premiums and Deposits (millions USD)',
        'extraction_hint': (
            'Find the "Premiums and deposits" total for Institutional Markets for fiscal year 2018 '
            '(second/middle data column) in the GAAP premiums-to-premiums-and-deposits '
            'reconciliation table on page 102.'
        ),
    },
    # Reserves_by_Charge — Group Retirement (page 97 surrender-charge table)
    {
        'obs_id':          'Obs_06',
        'variable':        'Reserves_by_Charge',
        'var_type':        'numeric',
        'query_key':       'group_retirement_reserves_by_charge',
        'source_page':     97,
        'description':     'Group Retirement reserves with No surrender charge at Dec 31, 2019 (millions USD)',
        'extraction_hint': (
            'Find the reserves amount for the "No surrender charge" row at December 31, 2019 '
            '(first data column) in the Group Retirement annuities reserves by surrender charge '
            'category table.'
        ),
    },
    {
        'obs_id':          'Obs_07',
        'variable':        'Reserves_by_Charge',
        'var_type':        'numeric',
        'query_key':       'group_retirement_reserves_by_charge',
        'source_page':     97,
        'description':     'Group Retirement reserves — surrender charge Greater than 0%–2% at Dec 31, 2019 (millions USD)',
        'extraction_hint': (
            'Find the reserves amount for the "Greater than 0% - 2%" row at December 31, 2019 '
            '(first data column) in the Group Retirement annuities reserves by surrender charge '
            'category table.'
        ),
    },
    {
        'obs_id':          'Obs_08',
        'variable':        'Reserves_by_Charge',
        'var_type':        'numeric',
        'query_key':       'group_retirement_reserves_by_charge',
        'source_page':     97,
        'description':     'Group Retirement reserves — surrender charge Greater than 2%–4% at Dec 31, 2019 (millions USD)',
        'extraction_hint': (
            'Find the reserves amount for the "Greater than 2% - 4%" row at December 31, 2019 '
            '(first data column) in the Group Retirement annuities reserves by surrender charge '
            'category table.'
        ),
    },
    {
        'obs_id':          'Obs_09',
        'variable':        'Reserves_by_Charge',
        'var_type':        'numeric',
        'query_key':       'group_retirement_reserves_by_charge',
        'source_page':     97,
        'description':     'Group Retirement reserves — surrender charge Greater than 4% at Dec 31, 2019 (millions USD)',
        'extraction_hint': (
            'Find the reserves amount for the "Greater than 4%" row at December 31, 2019 '
            '(first data column) in the Group Retirement annuities reserves by surrender charge '
            'category table.'
        ),
    },
    {
        'obs_id':          'Obs_10',
        'variable':        'Reserves_by_Charge',
        'var_type':        'numeric',
        'query_key':       'group_retirement_reserves_by_charge',
        'source_page':     97,
        'description':     'Group Retirement Total reserves at Dec 31, 2019 (millions USD)',
        'extraction_hint': (
            'Find the "Total reserves" amount at December 31, 2019 (first data column) in the '
            'Group Retirement annuities reserves by surrender charge category table.'
        ),
    },
    # Business_Sub_Segment — categorical segment names
    {
        'obs_id':          'Obs_11',
        'variable':        'Business_Sub_Segment',
        'var_type':        'categorical',
        'query_key':       'business_sub_segment_names',
        'source_page':     None,
        'description':     'Group Retirement operating segment under Life and Retirement',
        'extraction_hint': (
            'Find the group retirement operating segment under Life and '
            'Retirement (the one serving K-12 schools, higher education, healthcare and '
            'not-for-profit institutions).'
        ),
    },
    {
        'obs_id':          'Obs_12',
        'variable':        'Business_Sub_Segment',
        'var_type':        'categorical',
        'query_key':       'business_sub_segment_names',
        'source_page':     None,
        'description':     'Life insurance operating segment under Life and Retirement',
        'extraction_hint': (
            'Find the life insurance operating segment under Life and '
            'Retirement (the one offering term life and universal life insurance).'
        ),
    },
    {
        'obs_id':          'Obs_13',
        'variable':        'Business_Sub_Segment',
        'var_type':        'categorical',
        'query_key':       'business_sub_segment_names',
        'source_page':     None,
        'description':     'Institutional markets operating segment under Life and Retirement',
        'extraction_hint': (
            'Find the institutional markets operating segment under Life and '
            'Retirement (the one offering stable value wrap products, GICs, and pension risk '
            'transfer annuities).'
        ),
    },
    {
        'obs_id':          'Obs_14',
        'variable':        'Business_Sub_Segment',
        'var_type':        'categorical',
        'query_key':       'business_sub_segment_names',
        'source_page':     None,
        'description':     'domestic life sub-segment within Life Insurance',
        'extraction_hint': (
            'Find the domestic life sub-segment within the Life Insurance '
            'segment (U.S. operations with term life and universal life).'
        ),
    },
    {
        'obs_id':          'Obs_15',
        'variable':        'Business_Sub_Segment',
        'var_type':        'categorical',
        'query_key':       'business_sub_segment_names',
        'source_page':     None,
        'description':     'international life sub-segment within Life Insurance',
        'extraction_hint': (
            'Find the international life sub-segment within the Life '
            'Insurance segment (UK and Ireland operations).'
        ),
    },
]
