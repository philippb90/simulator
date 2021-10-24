
"""
Stores all configurations and infos to initialize the database
"""



INDEX_TICKERS = [
    #America
    "SPX Index",
    "INDU Index",
    "CCMP Index",
    "SPTSX Index",
    "MEXBOL Index",
    "IBOV Index",
    "NDX Index",
    "RAY Index",
    "RTY Index",

    #EMEA
    "SX5R Index",
    "SXXR Index",
    "UKX Index",
    "DAX Index",
    "MDAX Index",
    "TDXP Index",
    "CAC Index",
    "IBEX Index",
    "FTSEMIB Index",
    "SMI Index",
    "PTL Index",
    "LUXXR Index",
    "WIG Index",

    #Asia
    "NKY Index",
    "HSI Index",
    "SHSZ300 Index",
    "AS51 Index",
    "TPX Index"
]


STATIC_SECURITY_FIELDS = {
    'name': 'name',
    'bpipe_reference_security_class': 'asset_class',
    'country_full_name': 'country_name',
    'country': 'country_code',
    'rel_index': 'relative_index',
    'crncy': 'currency',
    'gics_sector_name': 'gics_sector',
    'gics_industry_name': 'gics_industry',
    'gics_sub_industry_name': 'gics_sub_industry',
    'bics_level_1_sector_name': 'bics_sector',
    'bics_level_2_industry_name': 'bics_industry_group',
    'bics_level_3_industry_name': 'bics_industry',
    'bics_level_4_sub_industry_name': 'bics_sub_industry',
    'fut_init_spec_ml': 'margin'
}
